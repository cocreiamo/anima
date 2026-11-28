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

import http.cookiejar
import json
import re
import secrets
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from conftest import CACHE
from engine_logic import audit_names_person, form_submission

ISSUER = "http://localhost:8080/realms/anima"
TOKEN_SCRIPT = r"""
seed=$( { printf 'configurator-applications\n'; cat /var/lib/anima/root-of-trust/seal; } | sha256sum | cut -d' ' -f1)
secret=$(printf '%s' "$seed:reporting" | sha256sum | cut -d' ' -f1)
body="grant_type=client_credentials&client_id=reporting&client_secret=$secret&scope=readonly"
exec 3<>/dev/tcp/127.0.0.1/8080
printf 'POST /realms/anima/protocol/openid-connect/token HTTP/1.0\r\nHost: localhost:8080\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n%s' "${#body}" "$body" >&3
cat <&3
"""


def application_token(engine) -> str:
    code, out = engine.exec("bash", "-c", TOKEN_SCRIPT)
    assert code == 0 and '"access_token":"' in out, out
    return out.split('"access_token":"')[1].split('"')[0]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Provider:
    """The identity provider as a person's browser reaches it: through the
    published port. Its public URL (the issuer) names port 8080, so every address
    it hands out is moved to the published port; cookies are kept and redirects
    are followed by hand."""

    def __init__(self, engine):
        self.base = f"http://127.0.0.1:{engine.container.get_exposed_port(8080)}"
        jar = self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar), _NoRedirect
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


def set_credential(engine, provider: Provider, person: str) -> str:
    """Give `person` a generated password at run time and return it. The
    administrator's password is derived inside the engine and read there."""
    code, admin_password = engine.exec(
        "cat", "/run/anima/configurator/identity_provider_admin_password"
    )
    assert code == 0, admin_password
    status, text = provider.request(
        f"{provider.base}/realms/master/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": "admin",
            "password": admin_password,
        },
    )
    assert status == 200, text
    auth = {"Authorization": f"Bearer {json.loads(text)['access_token']}"}
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
    password = set_credential(engine, provider, person)
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
    code, out = login(engine, application_token(engine), "readonly")
    assert code == 0 and "connection succeeded" in out, out
    log = server_log(engine)
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
