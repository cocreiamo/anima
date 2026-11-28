"""What the repository's tools must not leave behind: a dirty fork, a file outside
the cache, bytecode beside the source. R89 to R91, R108 and R110; each carries the postmortem
that records the event it guards (PM-002, PM-003, PM-004).
"""

import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

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


# ---- R108: the export of the model runs once for one input -----------------------------------

EXPORT = ROOT / "mise-tasks" / "model" / "export"
EXPORT_GUARDS = ("flock", "mv -T")


def export_faults(text):
    """The export script holds the lock, looks at the cache again after taking
    it, and starts the JVM only after that second look."""
    faults = [f"model/export lacks {g}" for g in EXPORT_GUARDS if g not in text]
    first = text.find('if [ -f "$cached/model.json" ]')
    second = text.find('if [ ! -f "$cached/model.json" ]')
    lock = text.find("flock")
    if first < 0 or lock < first:
        faults.append("the fast path does not come before the lock")
    if second < lock or text.find("java ") < second:
        faults.append("the cache is not looked at again under the lock")
    return faults


def fake_export_root(tmp_path, script_text, fail_first=False):
    """A project root with the export script under test, a stand-in for the
    fetch, and a `java` that waits, counts its runs and writes a model.json.
    No JVM and no network."""
    root = tmp_path / "root"
    (root / "mise-tasks/model").mkdir(parents=True)
    export = root / "mise-tasks/model/export"
    export.write_text(script_text)
    export.chmod(0o755)
    fetch = root / "mise-tasks/model/fetch"
    fetch.write_text(f'#!/usr/bin/env bash\necho "{tmp_path}/pilot"\n')
    fetch.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    runs = tmp_path / "runs"
    java = bin_dir / "java"
    fail = f'[ "$(wc -l < "{runs}")" -gt 1 ] || exit 1\n' if fail_first else ""
    java.write_text(
        f'#!/usr/bin/env bash\necho x >> "{runs}"\nsleep 0.5\n{fail}echo "[]" > model.json\n'
    )
    java.chmod(0o755)
    model = tmp_path / "m.sysml"
    model.write_text("package P {}\n")
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "MISE_PROJECT_ROOT": str(root),
        "SYSML_PILOT_VERSION": "9.9.9",
    }
    return export, env, model, runs


def start_exports(export, env, model, count):
    return [
        subprocess.Popen(
            [str(export), str(model)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        for _ in range(count)
    ]


def finish(procs):
    return [(p.wait(), *p.communicate()) for p in procs]


def run_exports(export, env, model, count):
    return finish(start_exports(export, env, model, count))


def test_R108_export_runs_once_for_one_input(tmp_path):
    """Proves, with a stand-in for the JVM and the fetch: six callers started
    together on an empty export cache start one run between them, all succeed
    and print the same file; a caller that finds the cache starts none; if the
    first run fails the next tries for itself and succeeds. It does not prove
    the real exporter."""
    assert export_faults(EXPORT.read_text()) == []
    # The scenario of the failing first run is independent of the first: its
    # callers start now, in a root of their own, and are looked at last.
    other = tmp_path / "other"
    other.mkdir()
    o_export, o_env, o_model, o_runs = fake_export_root(other, EXPORT.read_text(), True)
    failing = start_exports(o_export, o_env, o_model, 3)
    export, env, model, runs = fake_export_root(tmp_path, EXPORT.read_text())
    results = run_exports(export, env, model, 6)
    assert [code for code, _o, _e in results] == [0] * 6, results
    assert len(runs.read_text().splitlines()) == 1
    assert len({o for _c, o, _e in results}) == 1
    cached = Path(results[0][1].decode().strip())
    assert cached.is_file()
    left = [p.name for p in cached.parents[1].iterdir() if p.name.startswith("run.")]
    assert left == []
    assert run_exports(export, env, model, 1)[0][0] == 0
    assert len(runs.read_text().splitlines()) == 1  # the fast path
    # The first run fails: one of the waiting callers runs it again.
    results = finish(failing)
    assert sorted(code for code, _o, _e in results) == [0, 0, 1], results
    assert len(o_runs.read_text().splitlines()) == 2


def test_R108_export_runs_once_for_one_input_detects_violation(tmp_path):
    text = EXPORT.read_text()
    assert export_faults("java x\n")
    unlocked = text.replace("flock 9", "true")
    assert export_faults(unlocked)
    export, env, model, runs = fake_export_root(tmp_path, unlocked)
    run_exports(export, env, model, 6)
    assert len(runs.read_text().splitlines()) > 1


# ---- R191: the export reads every file of the model, and its cache key covers them ----------


def directory_export_faults(script_text, tmp_path, only=None):
    """Export a directory of files with the script under test, with a stand-in
    for the JVM that lists the files it is given, and change the directory: the
    export reads every file; the same files give the same cache entry and no new
    run; a changed, added, renamed or removed file gives another entry. `only`
    limits the changes made, for a check that needs one."""
    export, env, _model, runs = fake_export_root(tmp_path, script_text)
    seen = tmp_path / "seen"
    java = tmp_path / "bin" / "java"
    java.write_text(
        "#!/usr/bin/env bash\n"
        f'echo x >> "{runs}"\n'
        f'find model -type f -name "*.sysml" | LC_ALL=C sort >> "{seen}"\n'
        'echo "[]" > model.json\n'
    )
    tree = tmp_path / "tree"
    (tree / "requirements" / "day0").mkdir(parents=True)
    (tree / "anima.sysml").write_text("package Anima {}\n")
    requirement = tree / "requirements" / "day0" / "R1-first.sysml"
    requirement.write_text("package R1 {}\n")
    (tree / "README.md").write_text("not a model file\n")

    def run():
        done = subprocess.run(
            [str(export), str(tree)],
            check=False,
            env=env,
            capture_output=True,
            text=True,
        )
        assert done.returncode == 0, done.stderr
        return done.stdout.strip(), len(runs.read_text().splitlines())

    faults = []
    first, count = run()
    if seen.read_text().splitlines() != [
        "model/anima.sysml",
        "model/requirements/day0/R1-first.sysml",
    ]:
        faults.append(f"the export did not read every file: {seen.read_text()}")
    if run() != (first, count):
        faults.append("the same files did not give the same entry without a run")
    changes = {
        "changed": lambda: requirement.write_text("package R1 { part x; }\n"),
        "added": lambda: (
            tree / "requirements" / "day0" / "R2-second.sysml"
        ).write_text("package R2 {}\n"),
        "renamed": lambda: requirement.rename(requirement.with_name("R1-other.sysml")),
        "removed": lambda: (
            tree / "requirements" / "day0" / "R2-second.sysml"
        ).unlink(),
    }
    before_path, before = first, count
    for what, change in changes.items():
        if only is not None and what not in only:
            continue
        change()
        path, after = run()
        if path == before_path or after != before + 1:
            faults.append(f"a {what} file did not give another cache entry")
        before_path, before = path, after
    return faults


def test_R191_export_reads_every_file_of_the_model(tmp_path):
    """Proves, with a stand-in for the JVM, that the export script reads a
    directory of files as one input and keys its cache on all of them. That the
    pilot resolves packages across files is shown by the export of the model
    itself, which every other test reads."""
    assert directory_export_faults(EXPORT.read_text(), tmp_path) == []


def test_R191_export_reads_every_file_of_the_model_detects_violation(tmp_path):
    text = EXPORT.read_text()
    # A key that covers only the root file: a changed requirement leaves the
    # cache stale.
    hashed = "find . -type f -name '*.sysml' -print0 | LC_ALL=C sort -z"
    assert text.count(hashed) == 1
    root_only = text.replace(hashed, "find . -type f -name 'anima.sysml' -print0")
    assert directory_export_faults(root_only, tmp_path, only=("changed",))
    # A copy of the root file alone.
    (tmp_path / "again").mkdir()
    assert directory_export_faults(
        text.replace(
            "-name '*.sysml' -print0 \\\n                | tar",
            "-name 'anima.sysml' -print0 \\\n                | tar",
        ),
        tmp_path / "again",
        only=(),
    )


# ---- R110: releases stay patch-only until the founder decides otherwise ---------------------

RELEASE_CONFIG = ROOT / ".github" / "release-please-config.json"


def release_faults(config):
    """What in a release-please configuration would let a version leave the 0.0
    series: the first release is not 0.0.1, a later one is not always a patch
    bump, or a setting pins or relaxes the bump."""
    faults = []
    if config.get("initial-version") != "0.0.1":
        faults.append("initial-version is not 0.0.1")
    if config.get("versioning") != "always-bump-patch":
        faults.append("versioning is not always-bump-patch")
    for key in ("release-as", "bump-minor-pre-major", "bump-patch-for-minor-pre-major"):
        if key in config:
            faults.append(f"{key} is set")
    for package in config.get("packages", {}).values():
        if any(k in package for k in ("release-as", "initial-version", "versioning")):
            faults.append("a package overrides the versioning")
    return faults


def test_R110_releases_stay_patch_only():
    """Proves the configuration file keeps the first release at 0.0.1 and the
    strategy at always-bump-patch. It reads the file; that release-please obeys
    it is shown only by the release pull request it opens."""
    assert release_faults(json.loads(RELEASE_CONFIG.read_text())) == []


def test_R110_releases_stay_patch_only_detects_violation():
    good = json.loads(RELEASE_CONFIG.read_text())
    assert release_faults(good) == []
    assert release_faults({**good, "initial-version": "1.0.0"})
    assert release_faults({k: v for k, v in good.items() if k != "versioning"})
    assert release_faults({**good, "versioning": "default"})
    assert release_faults({**good, "release-as": "0.0.1"})
    assert release_faults({**good, "packages": {".": {"versioning": "default"}}})


# ---- R112: a run of format and a run of test exclude each other (PM-006) --------------------

FORMAT = ROOT / "mise-tasks" / "format"
TEST = ROOT / "mise-tasks" / "test"
FORMAT_COMMANDS = ("mise", "ruff", "buildifier", "prettier", "taplo")


def overlaps(events):
    """The moments at which a format run and a test run were in progress together.
    `events` are (nanoseconds, "start" or "end", "format" or "test") from one shared
    log."""
    alive = {"format": 0, "test": 0}
    found = []
    for t, what, who in sorted(events):
        alive[who] += 1 if what == "start" else -1
        if what == "start" and alive["format"] and alive["test"]:
            found.append(t)
    return found


def stub_tools(tmp_path):
    """Stand-ins for the formatters and the test runner that log when they start and
    end and take a moment between, and the environment that points the tasks at a
    root of their own. No network, nothing of the repository is touched."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "log"
    for name, who in [(c, "format") for c in FORMAT_COMMANDS] + [("uv", "test")]:
        tool = bin_dir / name
        tool.write_text(
            "#!/usr/bin/env bash\n"
            f'echo "$(date +%s%N) start {who}" >> "{log}"\n'
            "sleep 0.4\n"
            f'echo "$(date +%s%N) end {who}" >> "{log}"\n'
        )
        tool.chmod(0o755)
    root = tmp_path / "root"
    root.mkdir()
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "MISE_PROJECT_ROOT": str(root),
    }
    return env, log


def run_together(env, log, format_script, test_script, tests=1):
    """Start one format run and `tests` test runs at once; returns the exit codes
    and the events logged by the stand-ins."""
    root = env["MISE_PROJECT_ROOT"]
    procs = [subprocess.Popen([str(format_script)], env=env, cwd=root)]
    procs += [
        subprocess.Popen([str(test_script)], env=env, cwd=root) for _ in range(tests)
    ]
    codes = [p.wait() for p in procs]
    events = []
    for line in log.read_text().splitlines():
        t, what, who = line.split()
        events.append((int(t), what, who))
    return codes, events


def unguarded_copy(tmp_path):
    """The two tasks with the lock taken out: what a change that dropped it would be."""
    copies = []
    for script in (FORMAT, TEST):
        copy = tmp_path / "unguarded" / script.name
        copy.parent.mkdir(exist_ok=True)
        text = "\n".join(
            "true" if "flock" in line else line
            for line in script.read_text().splitlines()
        )
        copy.write_text(text + "\n")
        copy.chmod(0o755)
        copies.append(copy)
    return copies


def test_R112_format_and_test_exclude_each_other(tmp_path):
    """Proves that one format run started together with test runs never overlaps
    with them in time: the tasks run with stand-ins for the formatters and the test
    runner that log their start and end. It does not prove that the real formatters
    or pytest are the commands inside the lock, nor that a run started by hand
    outside `mise run` takes it."""
    env, log = stub_tools(tmp_path)
    codes, events = run_together(env, log, FORMAT, TEST, tests=3)
    assert codes == [0] * 4, codes
    # Both kinds really ran, so that no overlap is not for want of a run.
    assert {who for _t, _w, who in events} == {"format", "test"}
    assert overlaps(events) == []


def test_R112_format_and_test_exclude_each_other_detects_violation(tmp_path):
    assert overlaps([(1, "start", "format"), (2, "start", "test"), (3, "end", "test")])
    assert overlaps(
        [(1, "start", "test"), (2, "start", "format"), (3, "end", "format")]
    )
    assert not overlaps(
        [(1, "start", "format"), (2, "end", "format"), (3, "start", "test")]
    )
    # The same tasks without the lock do overlap.
    env, log = stub_tools(tmp_path)
    format_copy, test_copy = unguarded_copy(tmp_path)
    codes, events = run_together(env, log, format_copy, test_copy)
    assert codes == [0, 0]
    assert overlaps(events)
