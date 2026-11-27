"""System tests of what the parts of the engine do together once it is ready."""

import json
import subprocess

from conftest import CACHE, ROOT


def database_image() -> str:
    return (CACHE / "database.ref").read_text().strip()


def psql_outside(engine, tmp_path, conninfo: str, *volume: str) -> tuple[int, str]:
    """psql of the database image, on the host's network, against the published port."""
    result = subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--network=host",
            *volume,
            "--entrypoint=psql",
            database_image(),
            f"{conninfo} port={engine.container.get_exposed_port(5432)} connect_timeout=10",
            "--no-psqlrc",
            "--command=select 1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


# ---- R15 ---------------------------------------------------------------------


def test_R15_encrypted_connections_only(engine, tmp_path):
    """The secret store issued the server's certificate, and from outside the
    server takes part in TLS and refuses everything that is not."""
    code, ca = engine.exec("cat", "/run/anima/pgtls/ca.crt")
    assert code == 0 and "BEGIN CERTIFICATE" in ca, ca
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=show ssl",
    )
    assert out.strip() == "on", out
    root_file = tmp_path / "root.crt"
    root_file.write_text(ca)
    mount = f"--volume={root_file}:/root.crt:ro"
    base = "host=127.0.0.1 user=nobody dbname=postgres"
    # Without TLS: refused as unencrypted, before any rule about the user is read.
    code, out = psql_outside(engine, tmp_path, f"{base} sslmode=disable")
    assert code != 0 and "no encryption" in out, out
    # With TLS, verified against the authority of the secret store: the handshake
    # succeeds (the later refusal is about the user, not about the transport).
    code, out = psql_outside(
        engine,
        tmp_path,
        f"{base} sslmode=verify-full sslrootcert=/root.crt",
        mount,
    )
    assert code != 0 and "SSL encryption" in out, out
    assert "certificate" not in out.lower().replace("pg_hba", ""), out


# ---- R62 ---------------------------------------------------------------------


def as_secret_store(engine, role: str, database: str, sql: str) -> tuple[int, str]:
    """psql as the secret store's operating-system user (uid 1010) on the socket."""
    return engine.exec(
        "podman",
        "exec",
        "--user",
        "1010",
        "database",
        "psql",
        "--host=/run/postgresql",
        f"--username={role}",
        f"--dbname={database}",
        "--no-psqlrc",
        "--tuples-only",
        f"--command={sql}",
    )


def test_R62_storage_connection_uses_no_secret(engine):
    """The storage connection has no password anywhere; it is accepted by the
    operating-system user's peer credentials; the secret store's two roles are
    confined to their own work."""
    config = (ROOT / "engine/secrets/openbao.hcl").read_text()
    url = next(line for line in config.splitlines() if "connection_url" in line)
    assert "postgres://svc_secrets_store@/secrets_store?" in url, url
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=select string_agg(rolname || ':' || coalesce(rolpassword, 'none'), ',' "
        "order by rolname) from pg_authid where rolname like 'svc\\_secrets\\_%'",
    )
    assert out.strip() == "svc_secrets_manage:none,svc_secrets_store:none", out
    # The storage role: its own database only, and no more than that.
    assert (
        as_secret_store(engine, "svc_secrets_store", "secrets_store", "select 1")[0]
        == 0
    )
    code, out = as_secret_store(engine, "svc_secrets_store", "postgres", "select 1")
    assert code != 0, out
    code, out = as_secret_store(
        engine, "svc_secrets_store", "secrets_store", "create role probe"
    )
    assert code != 0 and "permission denied" in out, out
    # The management role: sets the credentials of service roles, stores nothing.
    code, out = as_secret_store(
        engine,
        "svc_secrets_manage",
        "postgres",
        "create role svc_probe; drop role svc_probe",
    )
    assert code == 0, out
    code, out = as_secret_store(
        engine, "svc_secrets_manage", "secrets_store", "select 1"
    )
    assert code != 0, out
    # Other operating-system users cannot take either role.
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=svc_secrets_manage",
        "--dbname=postgres",
        "--no-psqlrc",
        "--command=select 1",
    )
    assert code != 0 and "Peer authentication failed" in out, out


# ---- R30: the listen address ---------------------------------------------------


def test_R30_listen_address_follows_the_way_of_starting(engine, tmp_path):
    """Run as a container, the services listen on every address of the container
    (the outer publish restricts); the host mode, run here with an address file,
    would bind them to the configured address and refuses anything else.
    Unverified: the units of the booted case were never started on a booted machine."""
    code, out = engine.exec("cat", "/run/anima/listen/database.conf")
    assert code == 0 and out.strip() == "listen_addresses = '*'", out
    assert engine.active("anima-listen-container.service")
    assert not engine.active("anima-listen-host.service")
    # The condition that selects the unit is the one systemd evaluates here.
    assert (
        engine.exec(
            "systemd-analyze", "condition", "ConditionVirtualization=container"
        )[0]
        == 0
    )
    assert (
        engine.exec(
            "systemd-analyze", "condition", "ConditionVirtualization=!container"
        )[0]
        != 0
    )
    script = (
        "set -e; d=$(mktemp -d); printf '192.0.2.7\\n' >$d/address; "
        "ANIMA_LISTEN_DIR=$d ANIMA_LISTEN_ADDRESS_FILE=$d/address /usr/libexec/anima/listen host; "
        "cat $d/database.conf $d/access.env; "
        "printf 'x; drop\\n' >$d/address; "
        "if ANIMA_LISTEN_DIR=$d/b ANIMA_LISTEN_ADDRESS_FILE=$d/address /usr/libexec/anima/listen host; "
        "then echo ACCEPTED; else echo REFUSED; fi; "
        "ANIMA_LISTEN_DIR=$d/c ANIMA_LISTEN_ADDRESS_FILE=$d/missing /usr/libexec/anima/listen host; "
        "cat $d/c/database.conf"
    )
    code, out = engine.exec("bash", "-c", script)
    assert code == 0, out
    assert (
        "listen_addresses = '192.0.2.7'" in out and "KC_HTTP_HOST=192.0.2.7" in out
    ), out
    assert "REFUSED" in out and "ACCEPTED" not in out, out
    assert "listen_addresses = '127.0.0.1'" in out, out


# ---- R64 ---------------------------------------------------------------------


def smtp_and_read(engine) -> str:
    """Send one message to the stand-in's SMTP port and return its API's list."""
    script = r"""
set -e
exec 3<>/dev/tcp/127.0.0.1/1025
read -r -u 3 line
say() { printf '%s\r\n' "$1" >&3; read -r -u 3 line; }
say 'EHLO test'
while read -r -t 1 -u 3 line; do :; done
say 'MAIL FROM:<anima@example.org>'
say 'RCPT TO:<person@example.org>'
say 'DATA'
printf 'Subject: anima-system-test-message\r\nFrom: anima@example.org\r\nTo: person@example.org\r\n\r\nbody\r\n.\r\n' >&3
read -r -u 3 line
say 'QUIT'
exec 3<&-
exec 4<>/dev/tcp/127.0.0.1/8025
printf 'GET /api/v1/messages HTTP/1.0\r\n\r\n' >&4
cat <&4
"""
    code, out = engine.exec("bash", "-c", script)
    assert code == 0, out
    return out


def test_R64_mail_delivered_through_configured_service(own_engine):
    """The local profile selects the mail catcher: a message sent to the
    configured service is readable from it, as data."""
    engine = own_engine(
        "r64",
        binds={str(ROOT / "config"): "/etc/anima/config"},
        env={"ANIMA_PROFILE": "local"},
    )
    engine.wait_ready()
    assert engine.active("mail.service")
    out = smtp_and_read(engine)
    body = out[out.index("{") :]
    messages = json.loads(body)["messages"]
    assert [m["Subject"] for m in messages] == ["anima-system-test-message"], out
    assert messages[0]["To"][0]["Address"] == "person@example.org"
