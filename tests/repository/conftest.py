"""Make the generators of `mise run generate` importable by the tests, export
the model once per test session, and time the session for R55."""

import sys
import time

import pytest
from repo_facts import outside_snapshot
from sysml_model import ROOT, export_model

sys.path.insert(0, str(ROOT / "mise-tasks" / "generate"))

STARTED = pytest.StashKey[float]()
OUTSIDE = pytest.StashKey[set]()
# The test that reads the clock runs last, so that it sees the whole session.
LAST = "test_R55_checks_stay_fast"


def pytest_configure(config):
    # A conftest below the root is loaded at collection, after the session
    # started: the clock starts when this file is loaded.
    config.stash[STARTED] = time.monotonic()
    # Before anything exports the model (R90, PM-003).
    config.stash[OUTSIDE] = outside_snapshot()


def pytest_collection_modifyitems(items):
    items.sort(key=lambda item: item.originalname == LAST)  # stable: others keep order


@pytest.fixture
def seconds_in_session(request):
    """A function that returns the seconds elapsed since the session started."""
    started = request.config.stash[STARTED]
    return lambda: time.monotonic() - started


@pytest.fixture(scope="session")
def model():
    """The elements of model/anima.sysml, exported once per session. The export
    itself is also cached on disk by the hash of the model (mise-tasks/model/
    export), which the generators and the generate:check task share."""
    return export_model()


@pytest.fixture
def outside_before(request):
    """The files above the repository when the session started (R90)."""
    return request.config.stash[OUTSIDE]
