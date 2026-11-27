"""What the repository's tools must not leave behind: a dirty fork, a file outside
the cache, bytecode beside the source. R89 to R91 and R108; each carries the postmortem
that records the event it guards (PM-002, PM-003, PM-004).
"""

import hashlib
import os
import subprocess
import zipfile

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
        n
        for n in names
        if "__pycache__" in n.split("/") or n.endswith((".pyc", ".pyo"))
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


# ---- R108: the pilot is fetched in one guarded place (PM-007) -------------------------------

FETCH = ROOT / "mise-tasks" / "model" / "fetch"
FETCH_GUARDS = ("flock", "mktemp -d", "sha256sum --check", "mv -T")


def fetch_sites(scripts):
    """The scripts (name -> text) that download or unpack the pilot. Exactly one
    may, and it must hold the guards that make parallel callers safe."""
    return sorted(
        name
        for name, text in scripts.items()
        if "SysML-v2-Pilot-Implementation" in text
        and ("curl" in text or "unzip" in text)
    )


def fetch_faults(scripts, fetch_name="model/fetch"):
    faults = []
    if fetch_sites(scripts) != [fetch_name]:
        faults.append(f"the pilot is fetched in {fetch_sites(scripts)}")
    text = scripts.get(fetch_name, "")
    faults += [f"{fetch_name} lacks {g}" for g in FETCH_GUARDS if g not in text]
    if text.find("sha256sum --check") > text.find("unzip -q"):
        faults.append("the checksum is verified after the unpacking")
    return faults


def pilot_scripts():
    return {
        str(p.relative_to(ROOT / "mise-tasks")): p.read_text()
        for p in (ROOT / "mise-tasks").rglob("*")
        if p.is_file() and p.suffix in ("", ".sh")
    }


def fake_pilot(tmp_path):
    """A stand-in for the download: a `curl` that waits and copies a small archive
    with the layout of the pilot's, and the environment that names its checksum.
    No network."""
    version = "9.9.9"
    archive = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr(f"sysml/jupyter-sysml-kernel-{version}-all.jar", "jar")
        z.writestr("sysml/sysml.library/Kernel Libraries/a.sysml", "x")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl = bin_dir / "curl"
    curl.write_text(
        '#!/usr/bin/env bash\nsleep 0.3\nwhile [ "$1" != "-o" ]; do shift; done\n'
        f'cp "{archive}" "$2"\n'
    )
    curl.chmod(0o755)
    return {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "MISE_PROJECT_ROOT": str(tmp_path / "root"),
        "SYSML_PILOT_RELEASE": "r",
        "SYSML_PILOT_VERSION": version,
        "SYSML_PILOT_SHA256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    }


def run_fetches(env, count):
    procs = [
        subprocess.Popen(
            [str(FETCH)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        for _ in range(count)
    ]
    return [(p.wait(), *p.communicate()) for p in procs]


def test_R108_pilot_fetched_in_one_guarded_place(tmp_path):
    """Proves, without the network: the download and unpack logic is in one
    script only and that script holds the guards (a reading of its text, which
    does not prove they work); and eight callers started together on an empty
    cache, with the download replaced by a stand-in, all succeed and leave one
    complete tree. It does not prove the real archive unpacks."""
    assert fetch_faults(pilot_scripts()) == []
    env = fake_pilot(tmp_path)
    results = run_fetches(env, 8)
    assert [code for code, _o, _e in results] == [0] * 8, results
    target = tmp_path / "root/.cache/sysml-pilot/9.9.9/sysml"
    assert (target / "jupyter-sysml-kernel-9.9.9-all.jar").is_file()
    assert (target / "sysml.library/Kernel%20Libraries").is_symlink()
    assert {o.decode().strip() for _c, o, _e in results} == {str(target)}
    left = [p.name for p in target.parent.iterdir() if p.name.startswith("fetch.")]
    assert left == []
    assert run_fetches(env, 1)[0][0] == 0  # idempotent


def test_R108_pilot_fetched_in_one_guarded_place_detects_violation(tmp_path):
    good = {"model/fetch": FETCH.read_text(), "model/check": "model/fetch\n"}
    assert fetch_faults(good) == []
    # A second copy of the download, and an unguarded fetch.
    assert fetch_faults(
        {**good, "model/check": "curl -o x SysML-v2-Pilot-Implementation\n"}
    )
    unguarded = good["model/fetch"].replace("flock", "true")
    assert fetch_faults({**good, "model/fetch": unguarded})
    # A wrong checksum leaves nothing in place.
    env = fake_pilot(tmp_path)
    env["SYSML_PILOT_SHA256"] = "0" * 64
    code, _out, _err = run_fetches(env, 1)[0]
    assert code != 0
    assert not (tmp_path / "root/.cache/sysml-pilot/9.9.9/sysml").exists()
