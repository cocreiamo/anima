"""Fixtures of the integration tests of the commands that the workflows call.

They start containers (podman, rootless, a throwaway registry), so they run only
through `mise run ci:test`; a plain `pytest` skips them, which keeps
`mise run check` within its limit (R55).
"""

import os
import shutil
from pathlib import Path

import pytest
from ci_support import Store


def pytest_collection_modifyitems(config, items):
    if os.environ.get("ANIMA_CI_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="integration test: run `mise run ci:test`")
    for item in items:
        if "tests/ci" in str(Path(str(item.fspath))).replace("\\", "/"):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def store():
    """One registry for the session."""
    assert shutil.which("podman"), "podman is needed"
    started = Store()
    try:
        yield started
    finally:
        started.close()
