"""Fixtures of the promotion's integration tests: real podman, a throwaway registry.

The commands of `mise-tasks/promote/` are run as they are, against the pinned
registry image started rootless on a free local port, with a tiny image built
from the pinned alpine; the engine image is never touched. Everything created
has a unique name and is removed in a `finally`; a session killed with SIGKILL
can leave a container whose name starts with `anima-promote-test-`.

They start containers, so they run only through `mise run promote:test`
(`ANIMA_PROMOTE_TESTS=1`), never in `mise run check` (R55).
"""

import os
import tempfile
import time
import urllib.request
import uuid
from pathlib import Path

import pytest
from helpers import Image, Registry, pinned, podman


def pytest_collection_modifyitems(config, items):
    """The tests start containers: run them only through `mise run promote:test`."""
    if os.environ.get("ANIMA_PROMOTE_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="promotion test: run `mise run promote:test`")
    for item in items:
        if "tests/promote" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip)


@pytest.fixture
def registry(tmp_path):
    """A registry on a free local port, without TLS; podman is told to allow it."""
    name = f"anima-promote-test-{uuid.uuid4().hex[:12]}"
    podman(
        "run", "--detach", "--rm", "--name", name,
        "--publish", "127.0.0.1::5000", pinned("distribution"),
    )  # fmt: skip
    try:
        port = podman("port", name, "5000/tcp").stdout.strip().rsplit(":", 1)[1]
        found = Registry(name, f"localhost:{port}")
        for _ in range(100):
            try:
                urllib.request.urlopen(found.url("/v2/"), timeout=2).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("the registry did not answer")
        conf = tmp_path / "registries.conf"
        conf.write_text(f'[[registry]]\nlocation = "{found.host}"\ninsecure = true\n')
        previous = os.environ.get("CONTAINERS_REGISTRIES_CONF")
        os.environ["CONTAINERS_REGISTRIES_CONF"] = str(conf)
        os.environ["ANIMA_REGISTRY_INSECURE"] = "1"
        try:
            yield found
        finally:
            os.environ.pop("ANIMA_REGISTRY_INSECURE", None)
            if previous is None:
                os.environ.pop("CONTAINERS_REGISTRIES_CONF", None)
            else:
                os.environ["CONTAINERS_REGISTRIES_CONF"] = previous
    finally:
        podman("rm", "--force", "--time", "0", name, check=False)


@pytest.fixture
def make_image():
    """Builds tiny images from the pinned alpine, each with its own content, and
    removes them at the end."""
    made = []

    def make():
        unique = uuid.uuid4().hex
        with tempfile.TemporaryDirectory() as context:
            (Path(context) / "Containerfile").write_text(
                f"FROM {pinned('alpine')}\nRUN echo {unique} > /unique\n"
            )
            ref = f"localhost/anima-promote-test/{unique[:12]}:t"
            podman("build", "--format", "docker", "--quiet", "--tag", ref, context)
        image_id = podman("image", "inspect", "--format", "{{.Id}}", ref).stdout.strip()
        made.append(ref)
        return Image(ref, image_id)

    try:
        yield make
    finally:
        for ref in made:
            podman("rmi", "--force", ref, check=False)
