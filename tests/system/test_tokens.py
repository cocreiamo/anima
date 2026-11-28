"""Token logins against the database server, with PostgreSQL's own test client.

The client is `oauth_hook_client` of the PostgreSQL source (the `oauth-test-client`
target of the database container file): it presents a token it is given. The
tokens are issued by the identity provider of the engine to the example
application `reporting` of `config/access/identities.yaml` (client credentials).
A person's token comes from the device flow of the engine's own client: the test
plays the person's browser, a scripted one, against the identity provider's
published port, signing in as the person `carol` of the same file. The file holds
no credential, so the test sets one at run time, generated, through the identity
provider's administration interface, and it exists only in the engine container
of the session.
"""

import base64
import http.cookiejar
import json
import re
import secrets
import ssl
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from conftest import CACHE
from engine_logic import (
    audit_names_person,
    form_submission,
    issuer_faults,
    production_faults,
    temporary_administrators,
)

ISSUER = "http://localhost:8080/realms/anima"
PUBLIC_HOST = "localhost:8080"
# The identity provider's two credentials of the configurator, derived inside the
# engine from its root of trust: the temporary one it was started with, and the
# permanent client of the configurator in the master realm.
BOOTSTRAP_CLIENT = "anima-bootstrap"
CONFIGURATOR_CLIENT = "anima-configurator"
TOKEN_SCRIPT = r"""
seed=$( { printf 'configurator-applications\n'; cat /var/lib/anima/root-of-trust/seal; } | sha256sum | cut -d' ' -f1)
secret=$(printf '%s' "$seed:reporting" | sha256sum | cut -d' ' -f1)
body="grant_type=client_credentials&client_id=reporting&client_secret=$secret&scope=readonly"
exec 3<>/dev/tcp/127.0.0.1/8080
printf 'POST /realms/anima/protocol/openid-connect/token HTTP/1.0\r\nHost: __HOST__\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s' "${#body}" "$body" >&3
cat <&3
"""


def application_token(engine, host: str = PUBLIC_HOST) -> str:
    """The token of the application `reporting`, asked by the name `host`."""
    code, out = engine.exec("bash", "-c", TOKEN_SCRIPT.replace("__HOST__", host))
    assert code == 0 and '"access_token":"' in out, out
    return out.split('"access_token":"')[1].split('"')[0]


def token_claims(token: str) -> dict:
    payload = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Inside:
    """The identity provider as the configurator reaches it: on the pod's
    loopback, in plain HTTP, from inside the engine container. The entry never
    forwards its administration interface or its administrative realm, so a test
    that needs them comes this way, as the configurator does."""

    base = "http://127.0.0.1:8080"

    def __init__(self, engine):
        self.engine = engine

    def request(self, url, data=None, headers=None, method=None, json_body=None):
        """(status, body); a redirect is not followed; never raises on a status."""
        headers = {"Host": "localhost:8080", **(headers or {})}
        body = None
        if json_body is not None:
            body = json.dumps(json_body)
            headers["Content-Type"] = "application/json"
        elif data is not None:
            body = urllib.parse.urlencode(data)
        command = ["curl", "--silent", "--show-error", "--max-time", "30"]
        command += ["--write-out", "\n%{http_code}"]
        command += ["--request", method or ("POST" if body is not None else "GET")]
        for key, value in headers.items():
            command += ["--header", f"{key}: {value}"]
        if body is not None:
            command += ["--data-raw", body]
        code, out = self.engine.exec(*command, url)
        assert code == 0, out
        text, _, status = out.rpartition("\n")
        return int(status), text


class Provider:
    """The identity provider as a person's browser reaches it: through the entry,
    over TLS, trusting the engine's own authority. Its public URL (the issuer)
    names port 8080, so every address it hands out is moved to the entry's
    published port; cookies are kept and redirects are followed by hand."""

    def __init__(self, engine):
        self.base = f"https://127.0.0.1:{engine.container.get_exposed_port(8443)}"
        code, authority = engine.exec("cat", "/run/anima/entrytls/ca.crt")
        assert code == 0 and "BEGIN CERTIFICATE" in authority, authority
        jar = self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar),
            urllib.request.HTTPSHandler(
                context=ssl.create_default_context(cadata=authority)
            ),
            _NoRedirect,
        )

    def local(self, url: str) -> str:
        return url.replace("http://localhost:8080", self.base)

    def request(self, url, data=None, headers=None, method=None, json_body=None):
        """(status, body); follows redirects; never raises on a status."""
        # A person reaches the provider by its public name; the published port
        # only carries the connection. Without this header the issuer of the
        # tokens follows the address used and the database server refuses them.
        headers = {"Host": "localhost:8080", **(headers or {})}
        body = None
        if json_body is not None:
            body = json.dumps(json_body).encode()
            headers["Content-Type"] = "application/json"
        elif data is not None:
            body = urllib.parse.urlencode(data).encode()
        url = self.local(url)
        for _ in range(10):
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            # The provider marks its cookies Secure although the engine's public
            # URL is plain HTTP in the local profile; a browser on localhost sends
            # them anyway, the cookie jar does not.
            for cookie in self.jar:
                cookie.secure = False
            try:
                with self.opener.open(req, timeout=30) as response:
                    return response.status, response.read().decode()
            except urllib.error.HTTPError as error:
                if error.code in (301, 302, 303, 307):
                    url = urllib.parse.urljoin(
                        url, self.local(error.headers["Location"])
                    )
                    body, method = None, None
                    headers.pop("Content-Type", None)
                    continue
                return error.code, error.read().decode()
        raise AssertionError(f"too many redirects at {url}")


def token_answer(engine, provider: Provider, client: str, file: str):
    """(status, text of the answer) of the client-credentials grant of the master
    realm for `client`, whose secret the engine holds in `file`."""
    code, secret = engine.exec("cat", f"/run/anima/configurator/{file}")
    assert code == 0, secret
    return provider.request(
        f"{provider.base}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client,
            "client_secret": secret,
        },
    )


def administrator(engine, provider: Provider | Inside) -> dict:
    """The authorization header of the configurator's permanent client."""
    status, text = token_answer(
        engine, provider, CONFIGURATOR_CLIENT, "identity_provider_configurator_secret"
    )
    assert status == 200, text
    return {"Authorization": f"Bearer {json.loads(text)['access_token']}"}


def set_credential(engine, provider: Provider | Inside, person: str) -> str:
    """Give `person` a generated password at run time and return it. The
    configurator's own client signs in; its secret is derived inside the engine."""
    auth = administrator(engine, provider)
    users = f"{provider.base}/admin/realms/anima/users"
    status, text = provider.request(
        f"{users}?username={person}&exact=true", headers=auth
    )
    assert status == 200 and json.loads(text), text
    user = json.loads(text)[0]
    password = secrets.token_urlsafe(24)
    status, text = provider.request(
        f"{users}/{user['id']}/reset-password",
        headers=auth,
        method="PUT",
        json_body={"type": "password", "value": password, "temporary": False},
    )
    assert status == 204, (status, text)
    # The person's first-login steps are not under test: no required action, and
    # a name, so that the sign-in goes straight to the grant.
    user.update(requiredActions=[], firstName=person, lastName="Example")
    status, text = provider.request(
        f"{users}/{user['id']}", headers=auth, method="PUT", json_body=user
    )
    assert status == 204, (status, text)
    return password


def person_token(engine, person: str, role: str) -> str:
    """A token of `person` for the scope `role`, got through the device flow of
    the engine's client with a scripted browser."""
    provider = Provider(engine)
    password = set_credential(engine, Inside(engine), person)
    endpoint = f"{ISSUER}/protocol/openid-connect"
    status, text = provider.request(
        f"{endpoint}/auth/device", data={"client_id": "anima-engine", "scope": role}
    )
    assert status == 200, text
    device = json.loads(text)
    start = provider.local(device["verification_uri_complete"])
    status, page = provider.request(start)
    for _ in range(6):
        submission = form_submission(page, person, password)
        if submission is None:
            break
        action, data = submission
        status, page = provider.request(urllib.parse.urljoin(start, action), data=data)
    status, text = provider.request(
        f"{endpoint}/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device["device_code"],
            "client_id": "anima-engine",
        },
    )
    shown = " ".join(re.sub(r"<[^>]*>", " ", page.split("<body", 1)[-1]).split())
    assert status == 200, f"{status} {text} (last page: {shown[:600]})"
    return json.loads(text)["access_token"]


def client_image() -> str:
    return (CACHE / "database-test-client.ref").read_text().strip()


def login(engine, token: str, role: str) -> tuple[int, str]:
    """oauth_hook_client with `token`, over TLS to the published port, as `role`."""
    port = engine.container.get_exposed_port(5432)
    conninfo = (
        f"host=127.0.0.1 port={port} dbname=postgres user={role} sslmode=require "
        f"oauth_issuer={ISSUER} oauth_client_id=anima-engine connect_timeout=15"
    )
    result = subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--network=host",
            "--env=PGOAUTHDEBUG=UNSAFE",
            "--entrypoint=oauth_hook_client",
            client_image(),
            "--token",
            token,
            conninfo,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def server_log(engine) -> str:
    return engine.exec("podman", "logs", "database")[1]


def test_R2_valid_token_opens_session(engine):
    """A valid token of the configured issuer, for the scope of a role, opens a
    session of that role, over TLS: an application's token, and a person's token
    from the device flow, whose audit line names the person."""
    # The engine is shared: only what the server logged from here on counts.
    logged = len(server_log(engine))
    code, out = login(engine, application_token(engine), "readonly")
    assert code == 0 and "connection succeeded" in out, out
    log = server_log(engine)[logged:]
    assert "method=oauth" in log and "user=readonly" in log, log[-1500:]

    # A person: the token is the person's own, the session is the role's, and the
    # server's log names the person (the person stays identifiable).
    token = person_token(engine, "carol", "readwrite")
    code, out = login(engine, token, "readwrite")
    assert code == 0 and "connection succeeded" in out, out
    log = server_log(engine)
    assert audit_names_person(log, "carol", "readwrite"), log[-2500:]
    assert "SSL enabled" in log, "the session was not over TLS"
    # The person holds `readwrite` and no other role: the token of that role does
    # not open the session of one the person does not hold.
    code, out = login(engine, token, "admin")
    assert code != 0 and "connection succeeded" not in out, out


def test_R3_1_tampered_token_rejected(engine):
    """A token whose signature was altered is refused."""
    token = application_token(engine)
    head, payload, signature = token.split(".")
    flipped = ("A" if signature[10] != "A" else "B").join(
        [signature[:10], signature[11:]]
    )
    code, out = login(engine, f"{head}.{payload}.{flipped}", "readonly")
    assert code != 0 and "connection succeeded" not in out, out


def test_R5_identity_maps_to_role(engine):
    """The application holds `readonly` and no other role: its token opens that
    session, and the session of a role it does not hold is refused."""
    token = application_token(engine)
    assert login(engine, token, "readonly")[0] == 0
    code, out = login(engine, token, "admin")
    assert code != 0 and "connection succeeded" not in out, out


def test_R123_identity_provider_runs_in_production_mode(engine):
    """Seen from the running engine: the provider's log reports the production
    profile and not the development mode, and the realms are rows of its own
    database of the database server."""
    log = engine.exec("podman", "logs", "access")[1]
    code, rows = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--dbname=idp",
        "--no-psqlrc",
        "--tuples-only",
        "--command=select count(*) from realm",
    )
    count = int(rows.strip()) if code == 0 and rows.strip().isdigit() else 0
    faults = production_faults(log, count)
    assert not faults, (faults, rows, log[-1500:])


def test_R116_issuer_is_the_configured_public_url(engine):
    """Whatever name a request uses to reach the provider (the public name, the
    published address and port, an unrelated name), the discovery document and
    the tokens carry the configured public URL as issuer."""
    provider = Provider(engine)
    port = engine.container.get_exposed_port(8443)
    names = [PUBLIC_HOST, f"127.0.0.1:{port}", "other.example.test"]
    issuers = {}
    for name in names:
        status, text = provider.request(
            f"{provider.base}/realms/anima/.well-known/openid-configuration",
            headers={"Host": name},
        )
        assert status == 200, (name, status, text)
        issuers[f"discovery by {name}"] = json.loads(text)["issuer"]
        issuers[f"token by {name}"] = token_claims(application_token(engine, name))[
            "iss"
        ]
    faults = issuer_faults(issuers, ISSUER)
    assert not faults, faults


def test_R117_no_temporary_administrator_remains(engine):
    """After the configurator has run, no user of the master realm, service
    accounts included, is a temporary administrator, and the credentials the
    provider was started with obtain no token."""
    provider = Inside(engine)
    auth = administrator(engine, provider)
    status, text = provider.request(
        f"{provider.base}/admin/realms/master/users?briefRepresentation=false&max=1000",
        headers=auth,
    )
    assert status == 200, text
    users = json.loads(text)
    # The listing leaves out the service accounts: they are read client by client.
    status, text = provider.request(
        f"{provider.base}/admin/realms/master/clients", headers=auth
    )
    assert status == 200, text
    for client in json.loads(text):
        if client.get("serviceAccountsEnabled"):
            status, text = provider.request(
                f"{provider.base}/admin/realms/master/clients/{client['id']}/service-account-user",
                headers=auth,
            )
            assert status == 200, text
            users.append(json.loads(text))
    assert not temporary_administrators(users), temporary_administrators(users)
    # The service account of the permanent client is there, so the listing is
    # not an empty answer.
    assert f"service-account-{CONFIGURATOR_CLIENT}" in [u["username"] for u in users]
    status, text = token_answer(
        engine, provider, BOOTSTRAP_CLIENT, "identity_provider_bootstrap_secret"
    )
    assert status in (400, 401), (status, text)
