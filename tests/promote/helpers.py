"""Helpers of the promotion's integration tests."""

import os
import subprocess
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = ROOT / "mise-tasks" / "promote"
DOCKER_MANIFEST = "application/vnd.docker.distribution.manifest.v2+json"
OCI_MANIFEST = "application/vnd.oci.image.manifest.v1+json"
MANIFEST_TYPES = f"{DOCKER_MANIFEST}, {OCI_MANIFEST}"


def pinned(name):
    """`image@digest` of an entry of the register."""
    register = tomllib.loads((ROOT / "components.toml").read_text())
    (entry,) = [
        e
        for e in register.get("component", []) + register.get("tool_image", [])
        if e["name"] == name
    ]
    return f"{entry['image']}@{entry['digest']}"


def podman(*args, check=True):
    return subprocess.run(
        ["podman", *args], check=check, capture_output=True, text=True
    )


@dataclass
class Registry:
    name: str
    host: str

    def url(self, path):
        return f"http://{self.host}{path}"

    def digest(self, repository, tag):
        """What the registry says it holds for a tag, asked over HTTP: independent of
        every command under test. None when it holds nothing."""
        request = urllib.request.Request(
            self.url(f"/v2/{repository}/manifests/{tag}"),
            method="HEAD",
            headers={"Accept": MANIFEST_TYPES},
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as answer:
                return answer.headers["Docker-Content-Digest"]
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise

    def stop(self):
        podman("rm", "--force", "--time", "0", self.name, check=False)


@dataclass
class Image:
    ref: str
    id: str


def run_task(name, *args, env=None):
    """Run a command of `mise-tasks/promote/` as a workflow step does; its
    standard output is what a step appends to its outputs."""
    return subprocess.run(
        [str(TASKS / name), *args],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "MISE_PROJECT_ROOT": str(ROOT), **(env or {})},
    )


def outputs(result):
    """`key=value` lines of a command's standard output."""
    return dict(
        line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
    )
