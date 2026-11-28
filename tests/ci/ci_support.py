"""Helpers of the integration tests of the commands that the workflows call.

Each command is run as a workflow runs it, `mise run ci:<name>`, against the real
tool that it drives: podman, git, jq, the copy tool in its pinned image, and a
throwaway registry started on this machine from its pinned image
(`components.toml`, the entry `distribution`). Only the platform's own API (`gh`)
has no stand-in: its tests put a stub `gh` first on the PATH, which says so where
it is used.
"""

import json
import os
import shutil
import subprocess
import tempfile
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def register_entry(name):
    register = tomllib.loads((ROOT / "components.toml").read_text())
    entries = register["component"] + register.get("tool_image", [])
    return next(c for c in entries if c["name"] == name)


def reference(name):
    """The pinned reference of an image of the register, by digest."""
    entry = register_entry(name)
    return f"{entry['image']}@{entry['digest']}"


def run(args, env=None, cwd=None, input_text=None, check=False, timeout=600):
    result = subprocess.run(
        args,
        cwd=cwd or ROOT,
        env=env if env is not None else os.environ.copy(),
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"{args} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}"
        )
    return result


def task(name, *arguments, env=None, cwd=None):
    """Runs `mise run ci:<name> <arguments>` with the environment given on top of
    this one."""
    merged = os.environ.copy()
    # Inside a workflow these name the job's own files: never write to them.
    for own in ("GITHUB_OUTPUT", "GITHUB_STEP_SUMMARY", "GITHUB_ENV", "GITHUB_PATH"):
        merged.pop(own, None)
    merged.update(env or {})
    return run(
        ["mise", "run", "--quiet", f"ci:{name}", *arguments], env=merged, cwd=cwd
    )


def stub_command(directory, name, script):
    """A command first on the PATH that a test writes, for the one tool that has no
    local stand-in. Returns the environment that puts it first."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text("#!/usr/bin/env bash\n" + script)
    path.chmod(0o755)
    return {"PATH": f"{directory}:{os.environ['PATH']}"}


def recorder_command(directory, name, record):
    """A copy of the fixture `gh-recorder` first on the PATH, writing what it was
    called with, and the credential it was given, to `record`. Returns the
    environment that puts it first."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIXTURES / "gh-recorder", directory / name)
    return {"PATH": f"{directory}:{os.environ['PATH']}", "GH_RECORD": str(record)}


# ---- a registry of this machine ---------------------------------------------------------------


class Store:
    """A throwaway registry in a container of its own, published on the loopback."""

    def __init__(self):
        self.name = f"anima-ci-test-store-{os.getpid()}"
        run(
            [
                "podman",
                "run",
                "--detach",
                "--rm",
                "--name",
                self.name,
                "--publish",
                "127.0.0.1::5000",
                reference("distribution"),
            ],
            check=True,
        )
        port = run(["podman", "port", self.name, "5000"], check=True).stdout
        self.host = f"127.0.0.1:{port.strip().rsplit(':', 1)[1]}"
        self.built = []
        for _ in range(100):
            try:
                urllib.request.urlopen(f"http://{self.host}/v2/", timeout=2).close()
                return
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(0.2)
        raise AssertionError("the registry did not answer")

    def close(self):
        run(["podman", "rm", "--force", "--time", "0", self.name])
        for image in self.built:
            run(["podman", "rmi", "--force", image])

    def push(self, repository, tag, content):
        """Builds a small image holding `content` and pushes it as repository:tag.
        Returns its digest (hex)."""
        local = f"localhost/anima-ci-test/{repository.replace('/', '-')}:{os.urandom(4).hex()}"
        with tempfile.TemporaryDirectory() as context:
            Path(context, "Containerfile").write_text("FROM scratch\nCOPY f /f\n")
            Path(context, "f").write_text(content)
            run(
                ["podman", "build", "--format", "oci", "--tag", local, context],
                check=True,
            )
        self.built.append(local)
        run(
            [
                "podman",
                "push",
                "--tls-verify=false",
                "--format",
                "oci",
                local,
                f"docker://{self.host}/{repository}:{tag}",
            ],
            check=True,
        )
        return self.digest(repository, tag)

    def digest(self, repository, reference):
        """The digest (hex) that the registry holds for a tag or a digest, or None."""
        request = urllib.request.Request(
            f"http://{self.host}/v2/{repository}/manifests/{reference}",
            method="HEAD",
            headers={
                "Accept": "application/vnd.oci.image.manifest.v1+json,"
                "application/vnd.oci.image.index.v1+json,"
                "application/vnd.docker.distribution.manifest.v2+json"
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.headers["Docker-Content-Digest"].removeprefix("sha256:")
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise

    def tags(self, repository):
        try:
            with urllib.request.urlopen(
                f"http://{self.host}/v2/{repository}/tags/list", timeout=10
            ) as response:
                return sorted(json.load(response)["tags"] or [])
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return []
            raise
