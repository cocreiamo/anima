"""Fixtures of the configurator's tests.

The static tests read files and start nothing. The tests that need the pod of
throwaway containers (the database server, the secret store and the identity
provider) are marked `needs_pod` and skipped unless the environment variable
CONFIGURE_PROOF=1 is set, as `mise run engine:configure-test` does: that task
runs the standalone proof (`mise run engine:configure-prove`) once, and each
test reads what the proof recorded for the scenarios it names. A test fails when
a scenario it names did not pass or did not run.
"""

import os
import subprocess

import pytest
from support import ROOT, read_results


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "needs_pod: needs the pod of throwaway containers"
    )


def pytest_collection_modifyitems(config, items):
    """Tests that need the pod run only when CONFIGURE_PROOF=1."""
    if os.environ.get("CONFIGURE_PROOF") == "1":
        return
    skip = pytest.mark.skip(
        reason="needs the pod: run `mise run engine:configure-test`"
    )
    for item in items:
        if "needs_pod" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def proof():
    """The results of the standalone proof, which is run once for the session."""
    if os.environ.get("CONFIGURE_PROOF_REUSE") != "1":
        subprocess.run(["mise", "run", "engine:configure-prove"], cwd=ROOT, check=False)
    return read_results()
