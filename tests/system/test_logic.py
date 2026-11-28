"""Companions of the engine tests that show their decisions failing (R21, R42).

No container is started: each feeds the pure decision a recorded wrong input.
"""

import json

from engine_logic import container_phase, regress_tests_passed

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
