"""What the repository's tools must not leave behind: a dirty fork, a file outside
the cache, bytecode beside the source. R89 to R91; each carries the postmortem
that records the event it guards (PM-002, PM-003, PM-004).
"""

import subprocess

from repo_facts import outside_snapshot, repository_files, submodule_commits
from sysml_model import ROOT

# ---- R89: the forks are clean (PM-002) ----------------------------------------------------


def dirty_forks(paths, root=ROOT):
    """The checked-out forks whose working tree has a change (PM-002: a formatter
    once rewrote a file of a fork). A fork that is not checked out is left out."""
    dirty = []
    for path in paths:
        if not (root / path / ".git").exists():
            continue
        status = subprocess.run(
            ["git", "-C", str(root / path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        if status.strip():
            dirty.append(path)
    return dirty


def test_R89_submodule_working_trees_clean():
    paths = list(submodule_commits())
    assert paths, "no fork is declared"
    dirty = dirty_forks(paths)
    assert not dirty, f"forks with changes in their working tree: {dirty}"


def test_R89_submodule_working_trees_clean_detects_violation(tmp_path):
    fork = tmp_path / "fork"
    fork.mkdir()
    subprocess.run(["git", "init", "-q", str(fork)], check=True)
    assert dirty_forks(["fork"], tmp_path) == []
    (fork / "changed.toml").write_text("a = 1\n")
    assert dirty_forks(["fork"], tmp_path) == ["fork"]
    assert dirty_forks(["absent"], tmp_path) == []  # not checked out


# ---- R90: an export writes nothing outside the cache (PM-003) -----------------------------


def created_outside(before, after):
    """Files that appeared in the directories above the repository (PM-003: the
    exporter once wrote its output into the main checkout)."""
    return sorted(after - before)


def test_R90_export_writes_nothing_outside_cache(model, outside_before):
    """`model` has exported the model by now; the session started before it. On a
    warm cache the export does not run and this holds trivially: the check bites
    on a cold cache, for instance in continuous integration and after any edit
    of the model that is exported for the first time."""
    created = created_outside(outside_before, outside_snapshot())
    assert not created, f"files created above the repository: {created}"


def test_R90_export_writes_nothing_outside_cache_detects_violation(tmp_path):
    above = tmp_path / "above"
    above.mkdir()
    before = outside_snapshot(above / "repo", levels=1)
    (above / "stray.json").write_text("{}")
    after = outside_snapshot(above / "repo", levels=1)
    assert created_outside(before, after) == [str(above / "stray.json")]
    assert created_outside(before, before) == []


# ---- R91: no bytecode outside the cache (PM-004) --------------------------------------------


def bytecode_files(names):
    return sorted(
        n for n in names if "__pycache__" in n.split("/") or n.endswith((".pyc", ".pyo"))
    )


def test_R91_no_bytecode_outside_cache():
    """The cache directory is ignored, so it is not listed: any bytecode listed
    here was written beside the source (PM-004: Python run outside `mise`)."""
    names = [name for name, _path in repository_files()]
    assert names
    found = bytecode_files(names)
    assert not found, f"bytecode outside .cache/: {found}"


def test_R91_no_bytecode_outside_cache_detects_violation():
    assert bytecode_files(["a.py", "tests/x.md"]) == []
    assert bytecode_files(["tests/repository/__pycache__/m.cpython-312.pyc"])
    assert bytecode_files(["m.pyc"])
