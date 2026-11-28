"""PostgreSQL's own regression suite against the build of the database server."""

import subprocess

from conftest import CACHE, ROOT
from engine_logic import regress_tests_passed


def test_R21_upstream_regression_suite_passes():
    """`make check` of the upstream source tree, on the build that the shipped
    database server comes from, passes every test. The verdict is read from the
    result kept in the image, so a cached build gives it too (PM-008)."""
    result = subprocess.run(
        ["mise", "run", "engine:regress"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    # The result kept in the image, not the build output: a cached build is the same.
    log = (CACHE / "logs" / "regress.log").read_text()
    passed = regress_tests_passed(log)
    assert passed is not None and passed > 100, log[-2000:]
