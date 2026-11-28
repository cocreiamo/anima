"""Companions of the engine tests that show their decisions failing (R21, R42).

No container is started: each feeds the pure decision a recorded wrong input.
"""

import json

from engine_logic import (
    audit_names_person,
    certificate_facts,
    container_phase,
    form_submission,
    issuer_faults,
    production_faults,
    regress_tests_passed,
    renewal_failure_faults,
    renewal_faults,
    secret_store_storage_stage,
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
