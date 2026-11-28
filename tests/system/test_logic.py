"""Companions of the engine tests that show their decisions failing (R21, R42).

No container is started: each feeds the pure decision a recorded wrong input.
"""

import json

from engine_logic import (
    audit_names_person,
    certificate_facts,
    container_phase,
    form_submission,
    inner_start_times,
    issuer_faults,
    on_hosted_runner,
    production_faults,
    regress_tests_passed,
    renewal_failure_faults,
    renewal_faults,
    secret_store_storage_stage,
    session_duration_faults,
    shared_engine_faults,
    temporary_administrators,
)

PASSED_LOG = (
    "ok 1\n=====================\n All 215 tests passed.\n=====================\n"
)
FAILED_LOG = "not ok 3\n=====================\n 2 of 215 tests failed.\n"
RUNNING = json.dumps({"Status": "running", "Running": True, "Paused": False})
EXITED = json.dumps({"Status": "exited", "Running": False, "Paused": False})


def test_R21_upstream_regression_suite_passes_detects_violation():
    """The verdict reads the kept result: a pass is a number; a failure, an empty
    file and the build output of a cached build are none."""
    assert regress_tests_passed(PASSED_LOG) == 215
    assert regress_tests_passed(FAILED_LOG) is None
    assert regress_tests_passed("") is None
    cached_build_output = "STEP 5/5: RUN make check\n--> Using cache abc\nCOMMIT\n"
    assert regress_tests_passed(cached_build_output) is None


def test_R42_abrupt_stop_recovers_with_same_start_detects_violation():
    """A kill counts only when the container is seen stopped: a running, paused,
    created, missing or unreadable one is not, and neither is one that podman
    reports `stopped` after giving up waiting for the exit (ExitCode -1): the
    previous run is not finished and a start would be undone by its late exit."""
    assert container_phase(EXITED) == "stopped"
    assert container_phase(RUNNING) == "running"
    paused = json.dumps({"Status": "paused", "Running": True, "Paused": True})
    assert container_phase(paused) == "unknown"
    assert container_phase("") == "unknown"
    assert container_phase("null") == "unknown"
    assert container_phase("Error: no such container") == "unknown"
    created = json.dumps({"Status": "created", "Running": False})
    assert container_phase(created) == "unknown"
    gave_up = json.dumps({"Status": "stopped", "Running": False, "ExitCode": -1})
    assert container_phase(gave_up) == "stopping"


def test_R42_abrupt_stop_in_secret_store_first_start_recovers_detects_violation():
    """The kill counts only at the stage it was aimed at: each stage is told
    apart from the storage keys, and keys of no stage are not taken for one."""
    barrier = ["/core/keyring", "/core/root-key"]
    initialised = [*barrier, "/core/seal-config", "/core/mounts/x", "/sys/token/salt"]
    assert secret_store_storage_stage([]) == "empty"
    assert secret_store_storage_stage(barrier) == "barrier"
    assert secret_store_storage_stage(initialised) == "initialised"
    marked = [*initialised, "/core/status/self-init"]
    assert secret_store_storage_stage(marked) == "self-initialising"
    assert secret_store_storage_stage(["/core/root-key"]) == "unknown"
    assert secret_store_storage_stage(["/logical/x/y"]) == "unknown"


CERTIFICATE = "serial=0A1B\nnotAfter=Nov 28 12:00:00 2026 GMT\n"
FIRST = {"serial": "0A1B", "not_after": 1000.0}
SECOND = {"serial": "0C2D", "not_after": 1600.0}


def test_R118_certificate_renewed_before_expiry_detects_violation():
    """A renewal counts only when the certificate is another one, outliving the
    first, taken before the first expired, with no restart of the server."""
    assert renewal_faults(FIRST, SECOND, 900.0, "t1", "t1") == []
    assert renewal_faults(FIRST, FIRST, 900.0, "t1", "t1")
    assert renewal_faults(FIRST, {**SECOND, "not_after": 900.0}, 900.0, "t1", "t1")
    assert renewal_faults(FIRST, SECOND, 1000.0, "t1", "t1")
    assert renewal_faults(FIRST, SECOND, 900.0, "t1", "t2")
    assert certificate_facts(CERTIFICATE) == {
        "serial": "0A1B",
        "not_after": 1795867200.0,
    }
    assert certificate_facts("") is None
    assert certificate_facts("serial=0A1B\nnotAfter=never\n") is None
    assert certificate_facts("notAfter=Nov 28 12:00:00 2026 GMT\n") is None


def test_R119_failed_renewal_leaves_engine_not_ready_detects_violation():
    """The answer after a failed renewal must be negative and say why: a ready
    answer, a silent one and one that names another fault are not."""
    said = (
        "not ready\ndatabase-tls.service: failed\ncertificate renewal failed: refused"
    )
    assert renewal_failure_faults("unhealthy", said) == []
    assert renewal_failure_faults("healthy", said)
    assert renewal_failure_faults("unhealthy", "")
    assert renewal_failure_faults("unhealthy", "not ready\naccess.service: failed")


LOGIN_PAGE = (
    '<form id="kc-form-login" action="http://localhost:8080/a?x=1&amp;y=2" method="post">'
    '<input name="username" type="text"/><input name="password" type="password"/>'
    '<input type="hidden" name="credentialId" value=""/>'
    '<input name="login" type="submit" value="Sign In"/></form>'
)
GRANT_PAGE = (
    '<form action="/g" method="post"><input type="hidden" name="code" value="c1"/>'
    '<input name="accept" type="submit" value="Yes"/>'
    '<input name="cancel" type="submit" value="No"/></form>'
)
AUTHENTICATED = '2026-11-28 10:00:00 UTC [{n}] LOG:  connection authenticated: identity="carol" method=oauth\n'
AUTHORIZED = "2026-11-28 10:00:00 UTC [{n}] LOG:  connection authorized: user=readwrite database=postgres\n"


def test_R2_valid_token_opens_session_detects_violation():
    """The scripted browser fills the sign-in form and accepts the grant, never
    refuses it; the audit counts only when one session shows the person and the
    role together."""
    action, data = form_submission(LOGIN_PAGE, "carol", "pw")
    assert action == "http://localhost:8080/a?x=1&y=2"
    assert data == {
        "username": "carol",
        "password": "pw",
        "credentialId": "",
        "login": "Sign In",
    }
    _, grant = form_submission(GRANT_PAGE, "carol", "pw")
    assert grant == {"code": "c1", "accept": "Yes"}
    assert form_submission("<p>You may close this window</p>", "carol", "pw") is None

    same_session = AUTHENTICATED.format(n=41) + AUTHORIZED.format(n=41)
    assert audit_names_person(same_session, "carol", "readwrite")
    assert not audit_names_person(same_session, "alice", "readwrite")
    assert not audit_names_person(same_session, "carol", "readonly")
    two_sessions = AUTHENTICATED.format(n=41) + AUTHORIZED.format(n=42)
    assert not audit_names_person(two_sessions, "carol", "readwrite")
    assert not audit_names_person("", "carol", "readwrite")


def test_R123_identity_provider_runs_in_production_mode_detects_violation():
    """Production counts only with its own profile line, none of the
    development mode, and a realm in its own database."""
    prod = "started in 9s. Profile prod activated. Installed features"
    assert production_faults(prod, 3) == []
    assert production_faults(prod.replace("prod", "dev"), 3)
    assert production_faults(prod + " Running the server in development mode.", 3)
    assert production_faults(prod, 0)
    assert production_faults("", 3)


def test_R116_issuer_is_the_configured_public_url_detects_violation():
    """Every name must give the configured issuer, and one name proves nothing."""
    url = "http://localhost:8080/realms/anima"
    other = "http://127.0.0.1:41000/realms/anima"
    assert issuer_faults({"localhost:8080": url, "127.0.0.1:41000": url}, url) == []
    assert issuer_faults({"localhost:8080": url, "127.0.0.1:41000": other}, url)
    assert issuer_faults({"localhost:8080": url}, url)
    assert issuer_faults({}, url)


def test_R117_no_temporary_administrator_remains_detects_violation():
    """A user, or a service account, marked temporary is found; others are not."""
    marked = {
        "username": "service-account-x",
        "attributes": {"is_temporary_admin": ["true"]},
    }
    other = {"username": "service-account-y", "attributes": {"other": ["true"]}}
    plain = {"username": "alice"}
    assert temporary_administrators([marked, other, plain]) == ["service-account-x"]
    assert temporary_administrators([other, plain]) == []
    assert temporary_administrators([]) == []


ENGINE = {
    "container": "c1",
    "started": "t0",
    "health": "healthy",
    "ready": True,
    "inner": {"database": "100", "access": "101", "secrets": "102"},
}


def test_R181_shared_engine_stays_undisturbed_detects_violation():
    """A test that restarted or replaced the engine or one of its parts, stopped
    one, or left the engine not ready has disturbed it; one that changed nothing
    that matters has not. A snapshot that could not be taken is a fault."""
    assert shared_engine_faults(ENGINE, dict(ENGINE)) == []
    assert shared_engine_faults(ENGINE, {**ENGINE, "container": "c2"})
    assert shared_engine_faults(ENGINE, {**ENGINE, "started": "t1"})
    restarted = {**ENGINE, "inner": {**ENGINE["inner"], "database": "200"}}
    assert shared_engine_faults(ENGINE, restarted) == ["database was started again"]
    gone = {**ENGINE, "inner": {"access": "101", "secrets": "102"}}
    assert shared_engine_faults(ENGINE, gone) == ["database no longer runs"]
    assert shared_engine_faults(ENGINE, {**ENGINE, "health": "unhealthy"})
    assert shared_engine_faults(ENGINE, {**ENGINE, "ready": False})
    assert shared_engine_faults({**ENGINE, "health": "starting"}, ENGINE)
    assert shared_engine_faults(None, ENGINE)
    assert shared_engine_faults(ENGINE, None)
    # A part that started after the first snapshot is not a disturbance.
    more = {**ENGINE, "inner": {**ENGINE["inner"], "probe": "300"}}
    assert shared_engine_faults(ENGINE, more) == []
    listing = "database 100\naccess 101\n\nodd line here\nsecrets 102\n"
    assert inner_start_times(listing) == ENGINE["inner"]
    assert inner_start_times("") == {}


def test_R180_system_tests_stay_fast_detects_violation():
    """A session over the limit, a limit missing, in another unit or not positive,
    and a text that states a number of its own are faults."""
    limits = {"maxSystemTestTime": (1500, "s")}
    assert session_duration_faults(900.0, limits, "within the bound") == []
    assert session_duration_faults(1501.0, limits, "within the bound")
    assert session_duration_faults(900.0, {}, "within the bound")
    assert session_duration_faults(900.0, {"maxSystemTestTime": (1500, "B")}, "x")
    assert session_duration_faults(900.0, {"maxSystemTestTime": (0, "s")}, "x")
    assert session_duration_faults(900.0, limits, "within 25 minutes")
    # Off the hosted runner the time is reported, not judged; a wrong limit still is.
    assert session_duration_faults(2100.0, limits, "within the bound", False) == []
    assert session_duration_faults(2100.0, {}, "within the bound", False)
    # On the hosted runner an over-budget session fails, and the runner is told
    # apart by GitHub's variable only: absent, empty or another value is not it.
    hosted = on_hosted_runner({"GITHUB_ACTIONS": "true"})
    assert hosted
    assert session_duration_faults(2100.0, limits, "within the bound", hosted)
    for other in ({}, {"GITHUB_ACTIONS": ""}, {"GITHUB_ACTIONS": "false"}):
        assert not on_hosted_runner(other)


DECLARED = {
    "access": {"memory_mib": 640, "cpu_percent": 200, "tasks": 128},
    "mail": {"memory_mib": 128, "cpu_percent": 50, "tasks": 64},
}
SEEN = {
    "access": {"memory": "671088640\n", "cpu": "200000 100000\n", "pids": "128\n"},
    "mail": {"memory": "134217728", "cpu": "50000 100000", "pids": "64"},
}


def test_R207_every_container_runs_within_its_declared_envelope_detects_violation():
    """A container with no limit (`max`), a wrong limit or no declared envelope is
    named; the infrastructure container the declaration exempts is not."""
    from engine_logic import envelope_faults

    assert envelope_faults(DECLARED, SEEN, set()) == []
    for key, value, what in (
        ("memory", "max", "no memory limit"),
        ("cpu", "max 100000", "no CPU bound"),
        ("pids", "max", "no task limit"),
        ("memory", "1", "memory.max"),
        ("cpu", "100000 100000", "cpu.max"),
        ("pids", "2048", "pids.max"),
    ):
        broken = {**SEEN, "mail": {**SEEN["mail"], key: value}}
        faults = envelope_faults(DECLARED, broken, set())
        assert faults and what in faults[0] and "mail" in faults[0], (key, faults)
    stranger = {**SEEN, "other": SEEN["mail"]}
    assert envelope_faults(DECLARED, stranger, set())
    assert envelope_faults(DECLARED, stranger, {"other"}) == []


def test_R208_identity_provider_heap_follows_its_envelope_detects_violation():
    """The runtime's own default on this host (70 % of its memory), a heap over
    the declared share and one over the limit are each named."""
    from engine_logic import heap_faults

    host = 15353 * 1048576
    assert heap_faults(285212672, 640, 43, host) == []
    assert heap_faults(11274289152, 640, 43, host)
    assert heap_faults(700 * 1048576, 640, 43, host)
    assert heap_faults(8000 * 1048576, 16000, 43, host)
