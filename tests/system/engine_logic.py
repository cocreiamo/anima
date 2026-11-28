"""The decisions of the system tests that need no engine to be tested.

Each is a function of text or of a recorded state, so that it runs in every
`pytest` run and can be shown to fail on a wrong input (PM-008).
"""

import json
import re
from datetime import UTC, datetime

PASSED = re.compile(r"All (\d+) tests passed")


def regress_tests_passed(result: str) -> int | None:
    """The number of tests the upstream suite reports as all passed, or None.

    `result` is the file the build step keeps in the image, not the output of the
    build: a cached build does not print the step again.
    """
    matches = PASSED.findall(result)
    return int(matches[-1]) if matches else None


def container_phase(inspected_state: str) -> str:
    """`running`, `stopped` or `unknown`, from the JSON of `podman inspect --format
    '{{json .State}}'`. Only a state that says the container is not running and
    has exited is `stopped`; an empty or unreadable answer is `unknown`."""
    try:
        state = json.loads(inspected_state)
    except ValueError:
        return "unknown"
    if not isinstance(state, dict):
        return "unknown"
    if state.get("Running") is True and not state.get("Paused"):
        return "running"
    if state.get("Running") is False and state.get("Status") in ("exited", "stopped"):
        return "stopped"
    return "unknown"


def certificate_facts(openssl_output: str) -> dict | None:
    """The serial and the end of validity (seconds since the epoch) of a certificate,
    from `openssl x509 -noout -serial -enddate`; None when either is missing."""
    serial = re.search(r"^serial=(\S+)", openssl_output, re.MULTILINE)
    end = re.search(r"^notAfter=(.+?)\s*$", openssl_output, re.MULTILINE)
    if not serial or not end:
        return None
    try:
        stamp = datetime.strptime(end.group(1), "%b %d %H:%M:%S %Y GMT")
    except ValueError:
        return None
    return {
        "serial": serial.group(1),
        "not_after": stamp.replace(tzinfo=UTC).timestamp(),
    }


def renewal_faults(
    before: dict, after: dict, now: float, start_before: str, start_after: str
) -> list[str]:
    """What is wrong with a renewal seen from outside (R118): the certificate must
    be another one, that outlives the first, taken while the first was still valid,
    by a server that was not restarted (its start time is the same)."""
    faults = []
    if after["serial"] == before["serial"]:
        faults.append("the certificate presented is still the first one")
    if after["not_after"] <= before["not_after"]:
        faults.append("the new certificate does not outlive the first")
    if now >= before["not_after"]:
        faults.append("the first certificate had already expired")
    if start_after != start_before:
        faults.append("the database server was restarted")
    return faults


def renewal_failure_faults(status: str, output: str) -> list[str]:
    """What is wrong with the readiness answer after a failed renewal (R119): it
    must be negative (not `healthy`) and its text must say that the certificate
    could not be renewed."""
    faults = []
    if status == "healthy":
        faults.append("the engine still answers ready")
    if "certificate renewal failed" not in output:
        faults.append("the answer does not say that the renewal failed")
    return faults
