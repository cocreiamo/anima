"""The decisions of the system tests that need no engine to be tested.

Each is a function of text or of a recorded state, so that it runs in every
`pytest` run and can be shown to fail on a wrong input (PM-008).
"""

import json
import re

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
