"""Companions of the engine tests that show their decisions failing (R21, R42).

No container is started: each feeds the pure decision a recorded wrong input.
"""

import json

from engine_logic import (
    audit_names_person,
    container_phase,
    form_submission,
    regress_tests_passed,
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
    created, missing or unreadable one is not."""
    assert container_phase(EXITED) == "stopped"
    assert container_phase(RUNNING) == "running"
    paused = json.dumps({"Status": "paused", "Running": True, "Paused": True})
    assert container_phase(paused) == "unknown"
    assert container_phase("") == "unknown"
    assert container_phase("null") == "unknown"
    assert container_phase("Error: no such container") == "unknown"
    created = json.dumps({"Status": "created", "Running": False})
    assert container_phase(created) == "unknown"


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
