"""System tests of what the parts of the engine do together once it is ready."""

import json
import secrets
import subprocess
import time

from conftest import CACHE, ROOT, model_thresholds
from engine_logic import certificate_facts, renewal_failure_faults, renewal_faults


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


# ---- R118, R119 --------------------------------------------------------------

TLS_UNIT = ROOT / "engine/database/database-tls.container"
# The lifetimes that the tests give the certificate (in seconds), so that no test
# waits for days: set by a drop-in on one engine, never in the shipped unit.
SHORT_LIFETIME = 180
LONGER_LIFETIME = 240


def short_lived_certificate(tmp_path, seconds: int) -> dict[str, str]:
    """A drop-in of the certificate unit that sets its lifetime, as a bind mount."""
    dropin = tmp_path / "database-tls-lifetime.conf"
    dropin.write_text(
        f"[Container]\nEnvironment=ANIMA_TLS_LIFETIME_SECONDS={seconds}\n"
    )
    return {
        str(dropin): "/etc/containers/systemd/database-tls.container.d/50-test.conf"
    }


def presented_certificate(engine) -> dict:
    """The serial and the end of validity of the certificate that the server
    presents on its port, asked from inside the pod."""
    code, out = engine.inner(
        "database",
        "sh",
        "-c",
        "openssl s_client -starttls postgres -connect 127.0.0.1:5432 </dev/null "
        "2>/dev/null | openssl x509 -noout -serial -enddate",
    )
    facts = certificate_facts(out)
    assert code == 0 and facts, out
    return facts


def postmaster_start(engine) -> str:
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=select pg_postmaster_start_time()",
    )
    assert code == 0 and out.strip(), out
    return out.strip()


def test_R118_certificate_renewed_before_expiry(own_engine, tmp_path):
    """With a short lifetime, the certificate that the server presents is replaced
    by another before the first expires, and the server is not restarted."""
    engine = own_engine("r118", short_lived_certificate(tmp_path, SHORT_LIFETIME))
    engine.wait_for(
        "certificate in place", lambda: engine.active("database-tls.service"), 170
    )
    engine.wait_ready()
    first = presented_certificate(engine)
    started = postmaster_start(engine)
    container = engine.inner_container_started_at("database")
    engine.wait_for(
        "another certificate presented",
        lambda: presented_certificate(engine)["serial"] != first["serial"],
        SHORT_LIFETIME,
        2,
    )
    now = float(engine.exec("date", "+%s")[1])
    faults = renewal_faults(
        first, presented_certificate(engine), now, started, postmaster_start(engine)
    )
    assert not faults, faults
    assert engine.inner_container_started_at("database") == container
    assert engine.active("anima-ready.target")
    # The shipped unit carries the thresholds of the model, and nothing else does.
    limits, _ = model_thresholds("certificateRenewedBeforeExpiry")
    assert limits["certificateLifetime"][1] == "s"
    unit = unit_environment(TLS_UNIT)
    assert unit["ANIMA_TLS_LIFETIME_SECONDS"] == str(limits["certificateLifetime"][0])
    assert unit["ANIMA_TLS_RENEW_AFTER_PERCENT"] == str(limits["renewAfterPercent"][0])


def unit_environment(path) -> dict[str, str]:
    """The `Environment=NAME=value` lines of a unit file."""
    found = {}
    for line in path.read_text().splitlines():
        if line.startswith("Environment=") and "=" in line[12:]:
            name, value = line[12:].split("=", 1)
            found[name] = value
    return found


def health_report(engine) -> tuple[str, str]:
    """The engine's readiness answer: its status and the output of its last check."""
    code, out = engine.exec_host(
        "podman", "inspect", "--format", "{{json .State.Health}}", engine.name
    )
    if code != 0:
        return "unknown", ""
    health = json.loads(out)
    log = health.get("Log") or []
    return health.get("Status", "unknown"), (log[-1].get("Output", "") if log else "")


def test_R119_failed_renewal_leaves_engine_not_ready(own_engine, tmp_path):
    """The secret store refuses the server's machine login once the engine is
    ready: when the renewal falls due it fails, the engine stops answering ready,
    and its answer says that the certificate could not be renewed."""
    engine = own_engine("r119", short_lived_certificate(tmp_path, LONGER_LIFETIME))
    engine.wait_ready()
    secret_id = engine.exec("cat", "/run/anima/configurator/secret_store_secret_id")[1]
    code, token = engine.inner(
        "secrets",
        "bao",
        "write",
        "-field=token",
        "auth/configurator/login",
        "role_id=configurator",
        f"secret_id={secret_id.strip()}",
    )
    assert code == 0, token
    code, out = engine.exec(
        "podman",
        "exec",
        "--env",
        f"BAO_TOKEN={token.strip()}",
        "secrets",
        "bao",
        "delete",
        "auth/approle/role/database-server",
    )
    assert code == 0, out

    def reported() -> bool:
        status, output = health_report(engine)
        return status != "healthy" and "certificate renewal failed" in output

    deadline = time.monotonic() + LONGER_LIFETIME + 60
    try:
        engine.wait_for("the failure is reported", reported, LONGER_LIFETIME + 60, 3)
    finally:
        status, output = health_report(engine)
    assert time.monotonic() < deadline
    faults = renewal_failure_faults(status, output)
    assert not faults, (faults, output)
    assert not engine.active("anima-ready.target")


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
    # The entry follows the way of starting; the identity provider never does:
    # it listens on the loopback of the pod, whatever the way (R135).
    code, out = engine.exec("cat", "/run/anima/listen/entry.env")
    assert code == 0 and "Kestrel__Endpoints__Https__Url=https://0.0.0.0:8443" in out, (
        out
    )
    code, out = engine.exec("cat", "/run/anima/listen/access.env")
    assert code == 0 and out.strip() == "KC_HTTP_HOST=127.0.0.1", out
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
        "cat $d/database.conf $d/access.env $d/entry.env; "
        "printf 'x; drop\\n' >$d/address; "
        "if ANIMA_LISTEN_DIR=$d/b ANIMA_LISTEN_ADDRESS_FILE=$d/address /usr/libexec/anima/listen host; "
        "then echo ACCEPTED; else echo REFUSED; fi; "
        "ANIMA_LISTEN_DIR=$d/c ANIMA_LISTEN_ADDRESS_FILE=$d/missing /usr/libexec/anima/listen host; "
        "cat $d/c/database.conf"
    )
    code, out = engine.exec("bash", "-c", script)
    assert code == 0, out
    assert "listen_addresses = '192.0.2.7'" in out, out
    assert "KC_HTTP_HOST=127.0.0.1" in out and "KC_HTTP_HOST=192.0.2.7" not in out, out
    assert "Kestrel__Endpoints__Https__Url=https://192.0.2.7:8443" in out, out
    assert "ANIMA_ENTRY_HOST=192.0.2.7" in out, out
    assert "REFUSED" in out and "ACCEPTED" not in out, out
    assert "listen_addresses = '127.0.0.1'" in out, out


# ---- R64 ---------------------------------------------------------------------


def smtp_and_read(engine, subject: str) -> str:
    """Send one message with `subject` to the stand-in's SMTP port and return its
    API's list."""
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
printf 'Subject: __SUBJECT__\r\nFrom: anima@example.org\r\nTo: person@example.org\r\n\r\nbody\r\n.\r\n' >&3
read -r -u 3 line
say 'QUIT'
exec 3<&-
exec 4<>/dev/tcp/127.0.0.1/8025
printf 'GET /api/v1/messages HTTP/1.0\r\n\r\n' >&4
cat <&4
"""
    code, out = engine.exec("bash", "-c", script.replace("__SUBJECT__", subject))
    assert code == 0, out
    return out


def test_R64_mail_delivered_through_configured_service(engine):
    """The local profile selects the mail catcher: a message sent to the
    configured service is readable from it, as data. The engine is the one of the
    session, so the message carries a subject of its own and the list is read
    for that."""
    assert engine.active("mail.service")
    subject = f"anima-system-test-message-{secrets.token_hex(8)}"
    out = smtp_and_read(engine, subject)
    body = out[out.index("{") :]
    ours = [m for m in json.loads(body)["messages"] if m["Subject"] == subject]
    assert len(ours) == 1, out
    assert ours[0]["To"][0]["Address"] == "person@example.org"
