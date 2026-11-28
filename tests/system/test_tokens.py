"""Token logins against the database server, with PostgreSQL's own test client.

The client is `oauth_hook_client` of the PostgreSQL source (the `oauth-test-client`
target of the database container file): it presents a token it is given. The
tokens are issued by the identity provider of the engine to the example
application `reporting` of `config/access/identities.yaml` (client credentials);
a person's token needs a browser, which a test does not have.
"""

import subprocess

from conftest import CACHE

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
    session of that role (an application's token; a person's needs a browser)."""
    code, out = login(engine, application_token(engine), "readonly")
    assert code == 0 and "connection succeeded" in out, out
    log = server_log(engine)
    assert "method=oauth" in log and "user=readonly" in log, log[-1500:]


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
