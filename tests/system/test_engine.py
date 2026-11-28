"""System tests of the engine image, started as a container (Testcontainers)."""

import json
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest
from conftest import READY_LIMIT_SECONDS, ROOT
from engine_logic import secret_store_storage_stage

UNITS = {
    "database": ROOT / "engine/database/database.container",
    "database-init": ROOT / "engine/database/database-init.container",
    "database-prepare": ROOT / "engine/database/database-prepare.container",
    "access": ROOT / "engine/access/access.container",
    "secrets": ROOT / "engine/secrets/secrets.container",
}
# Containers that keep running and so carry the three checks (the others run to
# completion and are waited for by systemd).
SERVING = ["database", "access", "secrets"]


def submodule_commit(path: str) -> str:
    out = subprocess.run(
        ["git", "submodule", "status", path],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return out.strip().lstrip("+-U ").split()[0]


def unit_keys(path: Path) -> dict[str, list[str]]:
    keys: dict[str, list[str]] = {}
    for line in path.read_text().splitlines():
        match = re.match(r"^([A-Za-z]+)=(.*)$", line)
        if match:
            keys.setdefault(match.group(1), []).append(match.group(2))
    return keys


# ---- R1 ----------------------------------------------------------------------


def test_R1_engine_built_from_pinned_sources(engine):
    """Each inner image of the engine carries the commit of its source, equal to the pin."""
    components = tomllib.loads((ROOT / "components.toml").read_text())["component"]
    pinned = {c["name"]: c["commit"] for c in components if "commit" in c}
    labels = {
        "database": {
            "postgresql": "postgresql",
            "pgvector": "pgvector",
            "pg_oidc_validator": "pg_oidc_validator",
            "pgbackrest": "pgbackrest",
        },
        "access": {"keycloak": "keycloak"},
        "secrets": {"openbao": "openbao"},
    }
    for image, mapping in labels.items():
        code, out = engine.exec(
            "podman", "image", "inspect", f"localhost/anima/{image}:engine"
        )
        assert code == 0, out
        found = json.loads(out)[0]["Labels"]
        for label, component in mapping.items():
            assert found[f"org.anima.source.{label}"] == pinned[component], (
                image,
                label,
            )
            sub = pinned_path(component)
            assert submodule_commit(sub) == pinned[component], sub


def pinned_path(component: str) -> str:
    components = tomllib.loads((ROOT / "components.toml").read_text())["component"]
    return next(c["submodule"] for c in components if c["name"] == component)


# ---- R9 ----------------------------------------------------------------------


def test_R9_single_command_start(engine):
    """One `podman run` line; ready, as the engine's own answer, within the limit."""
    assert engine.ready_after is not None
    assert engine.ready_after <= READY_LIMIT_SECONDS
    code, out = engine.exec("systemctl", "is-active", "anima-ready.target")
    assert (code, out.strip()) == (0, "active")


# ---- R12 ---------------------------------------------------------------------


def test_R12_superuser_local_only(engine):
    """The superuser has no password and cannot connect over the network."""
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=select rolpassword is null from pg_authid where rolname = 'postgres'",
    )
    assert code == 0, out
    assert out.strip() == "t"
    # The only way in is the local socket, by the operating-system user's peer
    # credentials.
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=select type || ':' || auth_method from pg_hba_file_rules "
        "where user_name = '{postgres}'",
    )
    assert code == 0, out
    assert out.split() == ["local:peer"], out
    code, out = engine.exec(
        "podman",
        "run",
        "--rm",
        "--network=host",
        "--pod=anima",
        "--entrypoint=psql",
        "localhost/anima/database:engine",
        "--host=127.0.0.1",
        "--username=postgres",
        "--no-password",
        "--command=select 1",
    )
    assert code != 0
    assert "pg_hba.conf rejects" in out or "no pg_hba.conf entry" in out, out


# ---- R13 ---------------------------------------------------------------------


def failing_unit_dropin(tmp_path: Path, unit: str) -> dict[str, str]:
    """A systemd drop-in that makes `unit` fail at every start, as bind mounts."""
    dropin = tmp_path / f"{unit}-fails.conf"
    dropin.write_text("[Service]\nExecStartPre=/bin/false\n")
    return {str(dropin): f"/etc/systemd/system/{unit}.service.d/50-test-fails.conf"}


def database_answers(engine) -> bool:
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=select 1",
    )
    return code == 0 and out.strip() == "1"


def test_R13_database_server_starts_without_identity_provider(own_engine, tmp_path):
    """The identity provider's unit fails at every start: the database server still
    starts and accepts local connections (the engine as a whole is not ready)."""
    engine = own_engine("r13", failing_unit_dropin(tmp_path, "access"))
    engine.wait_for("database server answers", lambda: database_answers(engine), 150)
    assert not engine.active("access.service")
    assert not engine.active("anima-ready.target")


def test_R61_database_server_serves_without_secret_store(own_engine, tmp_path):
    """The secret store's unit fails at every start: the database server serves."""
    engine = own_engine("r61", failing_unit_dropin(tmp_path, "secrets"))
    engine.wait_for("database server answers", lambda: database_answers(engine), 150)
    assert not engine.active("secrets.service")
    assert not engine.active("anima-ready.target")


# ---- R29 ---------------------------------------------------------------------


def test_R29_depends_only_on_container_engine(engine):
    """Started with `podman run` and a volume flag each, on a host that has none of
    the engine's parts installed: the container reaches readiness, and every image
    it runs came from inside it (nothing was pulled)."""
    code, out = engine.exec("podman", "images", "--format", "{{.Repository}}:{{.Tag}}")
    assert code == 0
    names = set(out.split())
    assert {
        "localhost/anima/database:engine",
        "localhost/anima/access:engine",
        "localhost/anima/secrets:engine",
    } <= names
    host = subprocess.run(
        [
            "podman",
            "inspect",
            "--format",
            "{{json .Config.Cmd}} {{.HostConfig.Privileged}}",
            engine.name,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert host.strip().endswith("false")


# ---- R30 ---------------------------------------------------------------------


def test_R30_nothing_reachable_by_default(engine):
    """Only the two declared ports are published, and only on the loopback."""
    out = subprocess.run(
        [
            "podman",
            "inspect",
            "--format",
            "{{json .NetworkSettings.Ports}}",
            engine.name,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    ports = json.loads(out)
    published = {
        port: [b["HostIp"] for b in bindings or []]
        for port, bindings in ports.items()
        if bindings
    }
    assert set(published) == {"5432/tcp", "8080/tcp"}, published
    for port, addresses in published.items():
        assert addresses == ["127.0.0.1"], (port, addresses)


# ---- R41 ---------------------------------------------------------------------


def test_R41_probes_and_single_readiness(engine):
    """Every serving container declares the three checks; one target answers."""
    for name in SERVING:
        keys = unit_keys(UNITS[name])
        assert keys.get("HealthStartupCmd"), f"{name}: no startup check"
        assert keys.get("HealthCmd"), f"{name}: no liveness check"
        assert keys.get("HealthOnFailure") == ["kill"], (
            f"{name}: a failed check must restart"
        )
        assert keys.get("Notify") == ["healthy"], f"{name}: no readiness"
        assert "always" in keys.get("Restart", []), f"{name}: not restarted"
    target = (ROOT / "engine/image/anima-ready.target").read_text()
    for name in SERVING:
        assert f"{name}.service" in target
    # The engine's health check is the readiness target and nothing else.
    out = subprocess.run(
        [
            "podman",
            "inspect",
            "--format",
            "{{json .Config.Healthcheck.Test}}",
            engine.name,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "anima-ready.target" in out
    # The answer is true now, and false when one part is not active.
    assert (
        engine.exec("systemctl", "is-active", "--quiet", "anima-ready.target")[0] == 0
    )


# ---- R97 ---------------------------------------------------------------------


def test_R97_failing_health_check_restarts_container(own_engine):
    """The database server's process is stopped (it stays alive but answers
    nothing), so its liveness check fails: the container is killed, started
    again, the readiness target leaves and then returns to active."""
    engine = own_engine("r97")
    engine.wait_ready()
    before = engine.inner_container_started_at("database")
    assert before
    code, out = engine.exec("podman", "kill", "--signal", "STOP", "database")
    assert code == 0, out

    def restarted_and_ready() -> bool:
        started = engine.inner_container_started_at("database")
        return (
            bool(started) and started != before and engine.active("anima-ready.target")
        )

    engine.wait_for(
        "restart of the database server container", restarted_and_ready, 120, 0.5
    )
    # The readiness answer was negative while the part was down (it left the
    # active state) and became positive again by itself.
    journal = engine.exec("journalctl", "--no-pager", "--unit=anima-ready.target")[1]
    assert "Stopped target anima-ready.target" in journal, journal
    assert database_answers(engine)
    engine.wait_for("outer health", lambda: engine.health() == "healthy", 60)


# ---- R42 ---------------------------------------------------------------------


def test_R42_abrupt_stop_recovers_with_same_start(own_engine):
    """Killed in the middle of the first start, then after a complete start, the
    same container is started again and reaches readiness; data written before
    the kill is still there. A clean stop is the contrast: no crash recovery.
    The helpers wait for the observed phase, not for an exit code (PM-008)."""
    engine = own_engine("r42")
    # In the middle of the first start: as soon as the cluster creation has begun.
    engine.wait_for(
        "cluster creation started",
        lambda: (
            engine.exec("test", "-e", "/var/lib/anima/database/cluster.tmp/PG_VERSION")[
                0
            ]
            == 0
        ),
        120,
        0.02,
    )
    engine.kill()
    engine.start_again()
    engine.wait_ready()

    def sql(command: str) -> str:
        code, out = engine.inner(
            "database",
            "psql",
            "--host=/run/postgresql",
            "--username=postgres",
            "--no-psqlrc",
            "--tuples-only",
            f"--command={command}",
        )
        assert code == 0, out
        return out.strip()

    sql("create table if not exists survivor (n int)")
    sql("insert into survivor values (42)")
    # Abrupt stop of a running engine, same start command.
    engine.kill()
    engine.start_again()
    engine.wait_ready()
    assert sql("select n from survivor") == "42"
    logs = engine.exec("podman", "logs", "database")[1]
    assert "was not properly shut down" in logs, logs
    # Clean stop, then the same start: the server needs no crash recovery.
    engine.stop()
    engine.start_again()
    engine.wait_ready()
    assert sql("select n from survivor") == "42"
    logs = engine.exec("podman", "logs", "database")[1]
    assert "was not properly shut down" not in logs, logs


# The secret store initialises itself once, on empty storage, in a window of about
# a second that polling cannot hit. The test holds the store's start (a drop-in),
# puts a trigger on its storage table that sleeps before one chosen write, lets
# the store start, and kills the engine while the write is held. Each moment
# leaves storage at a stage that the store never repairs by itself.
HELD = "/run/anima/test-held"
GO = "/run/anima/test-go"
SECRET_STORE_KILL_MOMENTS = {
    # key ring written, seal configuration not yet: the store cannot unseal
    "barrier": "NEW.key = 'seal-config'",
    # initialised, self-initialisation not marked as started: the store skips it
    "initialised": "NEW.key = 'self-init'",
    # marked as started, a request of it not yet written: the store refuses to unseal
    "self-initialising": (
        "NEW.key <> 'self-init' AND EXISTS "
        "(SELECT FROM openbao_kv_store WHERE key = 'self-init')"
    ),
}
HOLD_WRITE = """
CREATE TABLE IF NOT EXISTS openbao_kv_store (parent_path TEXT COLLATE "C" NOT NULL,
  path TEXT COLLATE "C", key TEXT COLLATE "C", value BYTEA,
  CONSTRAINT openbao_kv_store_pkey PRIMARY KEY (path, key));
ALTER TABLE openbao_kv_store OWNER TO svc_secrets_store;
CREATE FUNCTION anima_test_hold() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN IF {condition} THEN PERFORM pg_sleep(600); END IF; RETURN NEW; END $$;
CREATE TRIGGER anima_test_hold BEFORE INSERT OR UPDATE ON openbao_kv_store
  FOR EACH ROW EXECUTE FUNCTION anima_test_hold();
"""


def secret_store_hold(tmp_path: Path) -> dict[str, str]:
    """A drop-in that holds every start of the secret store until GO exists."""
    dropin = tmp_path / "secrets-hold.conf"
    dropin.write_text(
        f"[Service]\nExecStartPre=/bin/sh -c 'touch {HELD}; "
        f"while [ ! -e {GO} ]; do sleep 0.2; done'\n"
    )
    return {str(dropin): "/etc/systemd/system/secrets.service.d/50-test-hold.conf"}


def superuser_sql(engine, database: str, command: str) -> tuple[int, str]:
    return engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        f"--dbname={database}",
        "--no-psqlrc",
        "--tuples-only",
        "--set=ON_ERROR_STOP=1",
        f"--command={command}",
    )


@pytest.mark.parametrize("stage", list(SECRET_STORE_KILL_MOMENTS))
def test_R42_abrupt_stop_in_secret_store_first_start_recovers(
    own_engine, tmp_path, stage
):
    """Killed while the secret store initialises itself for the first time, at
    each stage its storage can be left in, the same container is started again
    and reaches readiness, with the store's first start recorded as completed
    (PM-009)."""
    engine = own_engine(f"r42-{stage}", secret_store_hold(tmp_path))

    def held() -> bool:
        return engine.exec("test", "-e", HELD)[0] == 0

    engine.wait_for("the secret store's start held", held, 240)
    hold = HOLD_WRITE.replace("{condition}", SECRET_STORE_KILL_MOMENTS[stage])
    code, out = superuser_sql(engine, "secrets_store", hold)
    assert code == 0, out
    engine.exec("touch", GO)
    sleeping = "select count(*) from pg_stat_activity where wait_event = 'PgSleep'"
    engine.wait_for(
        "the secret store held at the write",
        lambda: superuser_sql(engine, "postgres", sleeping)[1].strip() == "1",
        180,
        0.5,
    )
    rows = superuser_sql(
        engine, "secrets_store", "select path || key from openbao_kv_store"
    )[1]
    assert secret_store_storage_stage(rows.split()) == stage, rows
    engine.kill()
    engine.start_again()
    engine.wait_for("the secret store's start held again", held, 240)
    # The test's own trigger goes, if the storage it was on is still there.
    code, out = superuser_sql(
        engine, "secrets_store", "DROP FUNCTION IF EXISTS anima_test_hold() CASCADE"
    )
    assert code == 0, out
    engine.exec("touch", GO)
    engine.wait_ready()
    completed = "select count(*) from anima.secret_store_first_start"
    assert superuser_sql(engine, "postgres", completed)[1].strip() == "1"


# ---- R98 ---------------------------------------------------------------------


def test_R98_readiness_negative_when_configurator_fails(own_engine, tmp_path):
    """A configuration the configurator refuses (no identity holds `admin`): the
    run fails with a message that names the fault, nothing changes, the readiness
    answer stays negative, and the parts that need no configuration keep serving."""
    shutil.copytree(ROOT / "config", tmp_path / "config")
    (tmp_path / "config/access/identities.yaml").write_text(
        "people:\n  - name: nobody\n    email: nobody@example.org\n    roles: [monitor]\n"
        "applications: []\n"
    )
    engine = own_engine("r98", binds={str(tmp_path / "config"): "/etc/anima/config"})
    engine.wait_for("database server answers", lambda: database_answers(engine), 150)

    def refused() -> bool:
        journal = engine.exec("journalctl", "--no-pager", "--unit=configure.service")[1]
        return "admin" in journal and "Error" in journal

    engine.wait_for("the configurator's refusal", refused, 240, 2)
    assert not engine.active("configure.service")
    assert not engine.active("anima-ready.target")
    assert engine.health() != "healthy"
