"""Generated files (R38): every file derived from another is generated and
committed, and a stale one fails the checks."""

import generators
from sysml_model import ROOT


def test_R38_derived_files_generated():
    stale = generators.stale(generators.outputs())
    assert not stale, f"out of date, run `mise run generate`: {stale}"


def test_R38_derived_files_generated_detects_violation(tmp_path):
    """The check reports a file that differs from its text and one that is
    missing, and nothing for a current file (in a directory of its own)."""
    (tmp_path / "current.txt").write_text("text\n")
    (tmp_path / "old.txt").write_text("old\n")
    files = {"current.txt": "text\n", "old.txt": "new\n", "absent.txt": "text\n"}
    assert generators.stale(files, tmp_path) == ["old.txt", "absent.txt"]
    assert generators.stale({"current.txt": "text\n"}, tmp_path) == []
    assert generators.ROOT == ROOT
