"""PostgreSQL's own regression suite against the build of the database server."""

import re
import subprocess

from conftest import CACHE, ROOT


def test_R21_upstream_regression_suite_passes():
    """`make check` of the upstream source tree, on the build that the shipped
    database server comes from, passes every test."""
    result = subprocess.run(
        ["mise", "run", "engine:regress"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout[-3000:] + result.stderr[-3000:]
    log = (CACHE / "logs" / "regress.log").read_text()
    match = re.search(r"All (\d+) tests passed", log)
    assert match and int(match.group(1)) > 100, log[-2000:]
