"""The secret store builds with the network off, and a missing dependency is named. R179 (TASK-43).

These tests build (the stages are cached by `mise run engine:build`, which the
system tests run first, so the build of a stage that did not change costs
seconds): the compile stages of engine/secrets/Containerfile run with
`--network=none` and read their modules only from the dependencies image
(`.cache/engine/secrets-dependencies.ref`). A copy of that image with one module
removed must fail the build at once, naming the module. The temporary images are
removed afterwards.
"""

import re
import shutil
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


def build_verified(
    tag: str, source: str = "third_party/openbao"
) -> subprocess.CompletedProcess:
    """Build the stage that checks the modules offline, from a dependencies image."""
    return podman(
        "build",
        "--format=docker",
        "--file",
        CONTAINERFILE,
        "--target",
        "verified",
        "--build-context",
        f"openbao={source}",
        "--build-context",
        f"dependencies=container-image://{dependencies_ref()}",
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


def test_R179_offline_build_succeeds_and_names_what_is_missing(
    tmp_path, temporary_images
):
    """The dependencies image is enough: the stage that verifies the modules and
    lists every package of the build, with the network off, succeeds."""
    tag = f"localhost/anima/offline-test-verified:{uuid.uuid4().hex[:8]}"
    temporary_images.append(tag)
    built = build_verified(tag)
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


def test_R179_offline_build_succeeds_and_names_what_is_missing_detects_violation(
    tmp_path, temporary_images
):
    """A dependency that the dependencies image does not hold fails the compile stage,
    and the error names it: nothing is downloaded to make up for it. The dependency is
    made missing by asking, in a copy of the fork's source, for the next patch version
    of a module the image holds (go.sum gets lines for it, as `go get` would write):
    the cache is not copied, so the stage that checks the modules reuses its layers."""
    source = tmp_path / "openbao"
    shutil.copytree(
        ROOT / "third_party/openbao",
        source,
        symlinks=True,
        ignore=shutil.ignore_patterns(".git"),
    )
    mod = (source / "go.mod").read_text()
    wanted = re.search(rf"{re.escape(MISSING)} (v\d+\.\d+)\.(\d+)\n", mod)
    assert wanted, f"go.mod does not require {MISSING}"
    newer = f"{wanted.group(1)}.{int(wanted.group(2)) + 1}"
    (source / "go.mod").write_text(mod.replace(wanted.group(0), f"{MISSING} {newer}\n"))
    with (source / "go.sum").open("a") as lock:
        hash_ = "h1:" + "A" * 43 + "="
        lock.write(f"{MISSING} {newer} {hash_}\n{MISSING} {newer}/go.mod {hash_}\n")

    tag = f"localhost/anima/offline-test-verified:{uuid.uuid4().hex[:8]}"
    temporary_images.append(tag)
    built = build_verified(tag, str(source))
    assert built.returncode != 0, "the build succeeded without the module"
    output = built.stderr + built.stdout
    # go names the module and the version it wanted and says why it did not get it:
    # "go: <module>@<version>: module lookup disabled by GOPROXY=off".
    expected = f"go: {MISSING}@{newer}: module lookup disabled by GOPROXY=off"
    assert expected in output, output[-2000:]
