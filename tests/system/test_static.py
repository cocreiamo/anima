"""Checks of the engine's declarations that do not start the engine."""

import subprocess

from conftest import ROOT

GENERATOR = "/usr/lib/systemd/system-generators/podman-system-generator"
BAD_UNIT_SCRIPT = (
    "mkdir /tmp/u && printf '[Container]\\nImagee=x\\n' >/tmp/u/bad.container"
    f" && QUADLET_UNIT_DIRS=/tmp/u {GENERATOR} --dryrun 2>&1"
)


def test_R52_engine_parts_validated_without_starting():
    """Quadlet's dry run and `systemd-analyze verify`, inside a container of the engine image."""
    result = subprocess.run(
        ["mise", "run", "engine:units-check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "ok   anima-ready.target" in output
    for unit in ("database", "access", "secrets", "anima-pod"):
        assert f"ok   {unit}.service" in output, output
    # The checker must fail on a broken unit: prove it on a copy with an unknown key.
    broken = subprocess.run(
        [
            "podman",
            "run",
            "--rm",
            "--entrypoint",
            "/bin/bash",
            (ROOT / ".cache/engine/engine.ref").read_text().strip(),
            "-c",
            BAD_UNIT_SCRIPT,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "unsupported key" in (broken.stdout + broken.stderr).lower()
