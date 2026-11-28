"""The secret store builds with the network off, and a missing dependency is named. R168 (TASK-43).

These tests build (the stages are cached by `mise run engine:build`, which the
system tests run first, so the build of a stage that did not change costs
seconds): the compile stages of engine/secrets/Containerfile run with
`--network=none` and read their modules only from the dependencies image
(`.cache/engine/secrets-dependencies.ref`). A copy of that image with one module
removed must fail the build at once, naming the module. The temporary images are
removed afterwards.
"""

import re
import subprocess
import uuid

import pytest
from conftest import CACHE, ROOT

CONTAINERFILE = "engine/secrets/Containerfile"
GOLANG = re.search(
    r"^ARG GOLANG=(\S+)", (ROOT / CONTAINERFILE).read_text(), re.MULTILINE
).group(1)
# A module that the secret store imports, taken out of the dependencies image.
MISSING = "github.com/hashicorp/go-hclog"


def podman(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["podman", *args], capture_output=True, text=True, check=check, cwd=ROOT
    )


def dependencies_ref() -> str:
    ref = CACHE / "secrets-dependencies.ref"
    if not ref.exists():
        pytest.fail("no dependencies image: run `mise run engine:build secrets`")
    return ref.read_text().strip()


def build_verified(dependencies: str, tag: str) -> subprocess.CompletedProcess:
    """Build the stage that checks the modules offline, from a dependencies image."""
    return podman(
        "build",
        "--format=docker",
        "--file",
        CONTAINERFILE,
        "--target",
        "verified",
        "--build-context",
        "openbao=third_party/openbao",
        "--build-context",
        f"dependencies=container-image://{dependencies}",
        "--tag",
        tag,
        ".",
        check=False,
    )


@pytest.fixture
def temporary_images():
    """Tags made by a test, removed at its end."""
    tags: list[str] = []
    yield tags
    for tag in tags:
        podman("rmi", "--force", tag, check=False)
    podman("image", "prune", "--force", check=False)


def test_R168_offline_build_succeeds_and_names_what_is_missing(
    tmp_path, temporary_images
):
    """The dependencies image is enough: the stage that verifies the modules and
    lists every package of the build, with the network off, succeeds."""
    tag = f"localhost/anima/offline-test-verified:{uuid.uuid4().hex[:8]}"
    temporary_images.append(tag)
    built = build_verified(dependencies_ref(), tag)
    assert built.returncode == 0, built.stderr[-2000:]

    # The guarantee is podman's: a step with `--network=none` cannot download a module,
    # even with the default proxy.
    (tmp_path / "Containerfile").write_text(
        f"FROM {GOLANG}\n"
        "RUN --network=none sh -c '! go mod download -json golang.org/x/text@v0.3.8 2>/dev/null'\n"
    )
    probe = f"localhost/anima/offline-test-probe:{uuid.uuid4().hex[:8]}"
    temporary_images.append(probe)
    built = podman(
        "build", "--format=docker", "--tag", probe, str(tmp_path), check=False
    )
    assert built.returncode == 0, built.stderr[-2000:]


def test_R168_offline_build_succeeds_and_names_what_is_missing_detects_violation(
    tmp_path, temporary_images
):
    """A dependencies image without one module fails the compile stage, and the error
    names the module: nothing is downloaded to make up for it."""
    (tmp_path / "Containerfile").write_text(
        f"FROM {GOLANG} AS cut\n"
        "COPY --from=dependencies /mod /deps/mod\n"
        f"RUN rm -rf /deps/mod/{MISSING}@* /deps/mod/cache/download/{MISSING}\n"
        "FROM scratch\n"
        "COPY --from=cut /deps/mod /mod\n"
    )
    broken = f"localhost/anima/offline-test-broken:{uuid.uuid4().hex[:8]}"
    temporary_images.append(broken)
    made = podman(
        "build",
        "--format=docker",
        "--build-context",
        f"dependencies=container-image://{dependencies_ref()}",
        "--tag",
        broken,
        str(tmp_path),
        check=False,
    )
    assert made.returncode == 0, made.stderr[-2000:]

    tag = f"localhost/anima/offline-test-verified:{uuid.uuid4().hex[:8]}"
    temporary_images.append(tag)
    built = build_verified(broken, tag)
    assert built.returncode != 0, "the build succeeded without the module"
    output = built.stderr + built.stdout
    # go names the module it wanted ("go: downloading <module> <version>") and says why it
    # did not get it ("module lookup disabled by GOPROXY=off").
    assert f"go: downloading {MISSING} " in output, output[-2000:]
    assert "module lookup disabled by GOPROXY=off" in output, output[-2000:]
