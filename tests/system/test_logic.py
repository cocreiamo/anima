"""Companions of the engine tests that show their decisions failing (R21, R42).

No container is started: each feeds the pure decision a recorded wrong input.
"""

import json

from engine_logic import (
    certificate_facts,
    container_phase,
    regress_tests_passed,
    renewal_failure_faults,
    renewal_faults,
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
