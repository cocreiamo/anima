"""Helpers of the configurator's tests: paths and the results of the proof."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIGURE = ROOT / "engine" / "configure"
RESULTS = ROOT / ".cache" / "configure" / "proof" / "results.txt"
IDENTITIES = Path(__file__).parent / "identities"

sys.path.insert(0, str(CONFIGURE))


def read_results(path=RESULTS):
    """Scenario results: name -> (status, detail)."""
    results = {}
    if path.exists():
        for line in path.read_text().splitlines():
            name, _, rest = line.partition(" ")
            status, _, detail = rest.partition(" ")
            results[name] = (status, detail)
    return results


def passed(results, *names):
    """Assert that every named scenario ran and passed."""
    missing = [n for n in names if n not in results]
    failed = {n: results[n] for n in names if n in results and results[n][0] != "PASS"}
    assert not missing, f"scenarios that did not run: {missing}"
    assert not failed, f"scenarios that failed: {failed}"
