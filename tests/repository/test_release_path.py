"""The workflows that verify the engine image and release it. R24, R114, R115 and R125.

The checks read the text of the workflows (a workflow cannot be run here); that
GitHub runs them as written is shown only by their first runs on `main`
(`anima-branching-and-releasing`). Each check is a function of its inputs and
has a `_detects_violation` companion that feeds it a deliberately wrong one.
"""

import json
import re
import tomllib

from sysml_model import ROOT

WORKFLOWS = ROOT / ".github" / "workflows"
SYSTEM_TESTS = WORKFLOWS / "system-tests.yml"
PROMOTE = WORKFLOWS / "promote.yml"
MISE = ROOT / "mise.toml"
ENGINE_TEST = ROOT / "mise-tasks" / "engine" / "test"


# ---- reading a workflow without a YAML library ------------------------------------------------


def jobs(text):
    """{job id: text of the job}, for a workflow written with two-space indentation."""
    found, current = {}, None
    in_jobs = False
    for line in text.splitlines():
        if re.fullmatch(r"jobs:\s*", line):
            in_jobs = True
        elif in_jobs and re.match(r"\S", line):
            in_jobs = False
        elif in_jobs and (m := re.fullmatch(r"  ([\w-]+):\s*", line)):
            current = m.group(1)
            found[current] = ""
            continue
        if in_jobs and current:
            found[current] += line + "\n"
    return found


def steps(job):
    """The steps of a job, each as its own text."""
    body = job.split("\n    steps:\n", 1)[-1] if "\n    steps:\n" in job else ""
    return [s for s in re.split(r"^      - ", body, flags=re.MULTILINE)[1:]]


def needs(job):
    m = re.search(r"^    needs:\s*\[?([^\]\n]*)\]?\s*$", job, re.MULTILINE)
    return {n.strip() for n in m.group(1).split(",")} if m else set()


def job_permissions(job):
    m = re.search(r"^    permissions:\s*(\{\})?\n((?:      .*\n)*)", job, re.MULTILINE)
    if not m:
        return None
    return dict(re.findall(r"^\s+([\w-]+):\s*(\w+)", m.group(2), re.MULTILINE))


def triggers(text):
    m = re.search(r"^on:\n((?:  .*\n|\n)+)", text, re.MULTILINE)
    return set(re.findall(r"^  ([\w_]+):", m.group(1), re.MULTILINE)) if m else set()


def run_text(step):
    return step.split("run:", 1)[1] if "run:" in step else ""


# ---- R114: the system tests report under one name, relevant change or not --------------------

# One path that each kind of change the check must notice takes, and two that it must not.
RELEVANT = [
    "engine/image/Containerfile",
    "third_party/postgres",
    ".gitmodules",
    "config/access/realm.tf",
    "tests/system/conftest.py",
    "mise-tasks/engine/image",
    "components.toml",
    ".github/workflows/system-tests.yml",
]
IRRELEVANT = ["README.md", "skills/anima-image-design.md", "model/anima.sysml"]


def relevant_pattern(text):
    m = re.search(r"^\s+RELEVANT:\s*'([^']*)'", text, re.MULTILINE)
    return re.compile(m.group(1)) if m else None


def system_test_faults(text):
    """What would keep the check from reporting under one name on every change, or
    from running when it must."""
    faults = []
    missing = {"pull_request", "merge_group", "push"} - triggers(text)
    if missing:
        faults.append(f"not triggered by {sorted(missing)}")
    if not re.search(r"^permissions:\s*\{\}\s*$", text, re.MULTILINE):
        faults.append("no empty top-level permissions")
    found = jobs(text)
    named = [
        j
        for j, b in found.items()
        if re.search(r"^    name: System tests\s*$", b, re.MULTILINE)
    ]
    if len(named) != 1:
        faults.append("not exactly one job named 'System tests'")
        return faults
    job = found[named[0]]
    if re.search(r"^    if:", job, re.MULTILINE) or needs(job):
        faults.append("the job is skipped or waits: it would not report")
    if job_permissions(job) != {"contents": "read"}:
        faults.append("the job holds more than contents: read")
    pattern = relevant_pattern(job)
    if pattern is None:
        faults.append("no RELEVANT pattern")
    else:
        faults += [f"{p} is not relevant" for p in RELEVANT if not pattern.search(p)]
        faults += [f"{p} is relevant" for p in IRRELEVANT if pattern.search(p)]
    parts = steps(job)
    if not parts or "id: changes" not in parts[0]:
        faults.append("the first step does not decide whether the change is relevant")
    gate = "steps.changes.outputs.relevant == 'true'"
    for part in parts[1:]:
        if re.search(r"if: failure\(\)", part):
            continue
        if gate not in part:
            faults.append(f"a step runs whatever the change: {part.splitlines()[0]}")
    tests = [p for p in parts if "mise run engine:test" in run_text(p)]
    if len(tests) != 1:
        faults.append("the system tests are not run exactly once")
    if not any("actions/cache/restore@" in p for p in parts):
        faults.append("the inner images are not restored")
    saves = [p for p in parts if "actions/cache/save@" in p]
    if len(saves) != 1 or "github.event_name == 'push'" not in saves[0]:
        faults.append("the cache is not saved from pushes only")
    logs = [p for p in parts if "actions/upload-artifact@" in p]
    if (
        len(logs) != 1
        or ".cache/engine/logs" not in logs[0]
        or "failure()" not in logs[0]
    ):
        faults.append("the engine logs are not kept on failure")
    return faults


def test_R114_system_tests_report_under_one_name():
    """Proves the text of the workflow: triggers, one job always run, steps gated on
    the decision of the first, the patterns. It does not prove that GitHub names the
    check as the ruleset will need, nor that a pull request reads the cache."""
    assert system_test_faults(SYSTEM_TESTS.read_text()) == []


def test_R114_system_tests_report_under_one_name_detects_violation():
    good = SYSTEM_TESTS.read_text()
    assert system_test_faults(good) == []
    assert system_test_faults(good.replace("  merge_group:\n", ""))
    assert system_test_faults(good.replace("name: System tests", "name: Other"))
    assert system_test_faults(
        good.replace(
            "    name: System tests\n", "    name: System tests\n    if: false\n"
        )
    )
    assert system_test_faults(good.replace("contents: read", "contents: write"))
    assert system_test_faults(good.replace("engine/|", ""))
    assert system_test_faults(good.replace("^(", "^(README|"))
    assert system_test_faults(
        good.replace("steps.changes.outputs.relevant == 'true'", "true")
    )
    assert system_test_faults(good.replace("github.event_name == 'push'", "true"))
    assert system_test_faults(good.replace("actions/cache/restore@", "actions/other@"))


# ---- R125: the cache of the inner images is refreshed when they changed, and only then -------


def cache_faults(text):
    """What would keep the cache of the inner images from being refreshed when the
    inner images changed (a cache is immutable: only a new key stores a new one), or
    would refresh it when they did not, or would make the save fail."""
    faults = []
    parts = steps(jobs(text).get("system-tests", ""))
    by_id = {m.group(1): p for p in parts if (m := re.search(r"id: (\w+)", p))}
    restore, pack = by_id.get("restore", ""), by_id.get("pack", "")
    saves = [p for p in parts if "actions/cache/save@" in p]
    if not restore or not pack or len(saves) != 1:
        return ["the restore, pack or save step is missing"]
    key = "key: system-tests-engine-${{ steps.key.outputs.value }}"
    if key not in restore or key not in saves[0]:
        faults.append("restore and save do not use the key of the inner images")
    if not re.search(
        r"restore-keys:\s*system-tests-engine-\s*$", restore, re.MULTILINE
    ):
        faults.append(
            "a changed set of inner images does not restore the nearest cache"
        )
    if "steps.restore.outputs.cache-hit != 'true'" not in pack:
        faults.append("the archive is saved although the key already holds it")
    if "steps.pack.outcome == 'success'" not in saves[0]:
        faults.append("the cache is saved without a new archive")
    loads = [p for p in parts if "podman load" in run_text(p)]
    if len(loads) != 1 or not re.search(
        r"^\s*rm -f ~/engine-cache/images\.tar\s*$", run_text(loads[0]), re.MULTILINE
    ):
        faults.append(
            "the restored archive is not removed after loading: podman save refuses to"
            " write over an existing archive"
        )
    elif parts.index(loads[0]) > parts.index(pack):
        faults.append("the restored archive is removed after the new one is saved")
    return faults


def test_R125_cache_of_inner_images_refreshed_when_they_changed():
    """(PM-010) Proves the text of the workflow. That the cache is refreshed is shown only by
    the first push to `main` that changes the inner images after it was merged."""
    assert cache_faults(SYSTEM_TESTS.read_text()) == []


def test_R125_cache_of_inner_images_refreshed_when_they_changed_detects_violation():
    good = SYSTEM_TESTS.read_text()
    assert cache_faults(good) == []
    assert cache_faults(good.replace("          rm -f ~/engine-cache/images.tar\n", ""))
    assert cache_faults(good.replace("cache-hit != 'true'", "cache-hit == 'true'"))
    assert cache_faults(good.replace("steps.pack.outcome == 'success'", "true"))
    assert cache_faults(
        good.replace("          restore-keys: system-tests-engine-\n", "")
    )
    assert cache_faults(
        good.replace(
            "key: system-tests-engine-${{ steps.key.outputs.value }}\n          restore-keys",
            "key: system-tests-engine\n          restore-keys",
        )
    )


# ---- R24 and R115: the promotion verifies, then publishes what it verified -------------------

PROMOTE_FAULT_TARGETS = ("verify", "publish", "promote")


def promotion_jobs(text):
    found = jobs(text)
    return {name: found.get(name) for name in PROMOTE_FAULT_TARGETS}


def release_path_faults(workflow, mise, engine_test):
    """What would let a version be released, or main-green move, from a commit that
    did not pass every verification, system tests included (R24)."""
    faults = []
    found = promotion_jobs(workflow)
    if not all(found.values()):
        return [f"missing job: {[n for n, b in found.items() if not b]}"]
    if triggers(workflow) != {"schedule", "workflow_dispatch"}:
        faults.append("promoted by something other than the schedule and a dispatch")
    verify = found["verify"]
    if "mise run promote:verify" not in "".join(run_text(s) for s in steps(verify)):
        faults.append("the verify job does not run promote:verify")
    if "contents: write" in verify or "packages: write" in verify:
        faults.append("the verify job can write")
    task = re.search(
        r'^\[tasks\."promote:verify"\]\n(.*?)(?=^\[|\Z)', mise, re.MULTILINE | re.DOTALL
    )
    if not task or "engine:test" not in task.group(1):
        faults.append("promote:verify does not run the system tests")
    # The system tests are skipped unless the task that runs them asks for them.
    if (
        "ANIMA_SYSTEM_TESTS=1" not in engine_test
        or "pytest tests/system" not in engine_test
    ):
        faults.append("engine:test would skip the system tests or not run them")
    for name, job in jobs(workflow).items():
        moves = "git/refs" in job or "gh release create" in job
        if moves and (name == "verify" or "verify" not in needs(job)):
            faults.append(
                f"{name} moves main-green or releases without waiting for verify"
            )
    if "needs.verify.outputs.sha" not in found["promote"]:
        faults.append("the promotion does not move the commit that was verified")
    return faults


def test_R24_release_only_from_verified_commit():
    """Proves the text of the promotion workflow and of the task it runs: nothing
    moves main-green or releases before the job that runs every verification, system
    tests included. It does not prove a run: that is the first run on main."""
    faults = release_path_faults(
        PROMOTE.read_text(), MISE.read_text(), ENGINE_TEST.read_text()
    )
    assert faults == []


def test_R24_release_only_from_verified_commit_detects_violation():
    good, mise, task = PROMOTE.read_text(), MISE.read_text(), ENGINE_TEST.read_text()
    assert release_path_faults(good, mise, task) == []
    assert release_path_faults(good, mise, task.replace("ANIMA_SYSTEM_TESTS=1", ""))
    assert release_path_faults(
        good, mise, task.replace("pytest tests/system", "pytest tests/repository")
    )
    assert release_path_faults(
        good.replace("mise run promote:verify", "true"), mise, task
    )
    assert release_path_faults(
        good.replace("    needs: [verify, publish]", "    needs: []"), mise, task
    )
    assert release_path_faults(
        good.replace("  workflow_dispatch:", "  pull_request:"), mise, task
    )
    assert release_path_faults(good, mise.replace("engine:test", "check"), task)
    assert release_path_faults(
        good.replace("needs.verify.outputs.sha", "github.sha"), mise, task
    )
    assert release_path_faults(good.replace("  publish:", "  other:"), mise, task)


def publish_faults(workflow):
    """What would let the promotion publish something other than the image that was
    built and passed in the same run, or under a moving name (R115)."""
    faults = []
    found = promotion_jobs(workflow)
    if not all(found.values()):
        return [f"missing job: {[n for n, b in found.items() if not b]}"]
    verify, publish = found["verify"], found["publish"]
    if re.search(r"latest", workflow):
        faults.append("a moving name is mentioned")
    if (
        "verify" not in needs(publish)
        or "needs.verify.outputs.publish == 'true'" not in publish
    ):
        faults.append("publish does not wait for verify and its decision")
    writers = [
        n for n, b in jobs(workflow).items() if "packages" in (job_permissions(b) or {})
    ]
    if writers != ["publish"] or job_permissions(publish).get("packages") != "write":
        faults.append(f"packages: write is held by {writers}, not by publish alone")
    commands = "".join(run_text(s) for s in steps(publish))
    for forbidden in ("podman build", "mise run", "buildah", "git checkout"):
        if forbidden in commands:
            faults.append(f"publish builds or runs the repository: {forbidden}")
    if "actions/checkout@" in publish or "actions/cache" in publish:
        faults.append("publish checks out or restores a cache")
    if "podman load" not in commands or "needs.verify.outputs.image-id" not in publish:
        faults.append("publish does not load the archive and check its id")
    if not re.search(r"podman push .*--digestfile", commands):
        faults.append("the image is not pushed with its digest recorded")
    if not re.search(r"ghcr\.io/cocreiamo/anima:\$\{?VERSION\}?", commands):
        faults.append("the image is not pushed under its version")
    push = steps(publish)[-1]
    if (
        "existing=true" not in push
        or "{{.Digest}}" not in push
        or "exit 0" not in push
        or push.index("exit 0") > push.index("podman push")
    ):
        faults.append(
            "an existing tag is not left alone and released at its own digest"
        )
    if "EXISTING" not in found["promote"]:
        faults.append(
            "the release notes do not say that the image was published earlier"
        )
    if "reference" not in publish or "@" not in commands:
        faults.append("the image is not identified by digest")
    verify_commands = "".join(run_text(s) for s in steps(verify))
    if "podman save" not in verify_commands:
        faults.append("verify does not archive the image it tested")
    if "podman load" in verify_commands or "engine-cache" in workflow:
        faults.append("the image is restored from a cache")
    caches = re.findall(
        r"actions/cache(?:/restore)?@.*?\n(?:.*\n)*?\s+path: (\S+)", workflow
    )
    if "cache/restore" in workflow or any(p != ".cache/sysml-pilot" for p in caches):
        faults.append("the promotion restores a cache other than the model validator's")
    return faults


def test_R115_promotion_publishes_only_what_it_verified():
    """Proves the text of the workflow: one job holds the permission to write
    packages, loads the archive that the verifying job made and compares its id,
    pushes it under the version with its digest recorded, and names no moving tag.
    It does not prove that the registry accepts it: that is the first release."""
    assert publish_faults(PROMOTE.read_text()) == []


def test_R115_promotion_publishes_only_what_it_verified_detects_violation():
    good = PROMOTE.read_text()
    assert publish_faults(good) == []
    assert publish_faults(good + "      - run: echo " + "late" + "st\n")
    assert publish_faults(good.replace("packages: write", "packages: read"))
    assert publish_faults(
        good.replace(
            "      contents: read\n", "      contents: read\n      packages: write\n", 1
        )
    )
    assert publish_faults(good.replace("podman load", "podman build"))
    assert publish_faults(
        good.replace("needs.verify.outputs.image-id", "needs.verify.outputs.sha")
    )
    assert publish_faults(good.replace("--digestfile", "--quiet"))
    assert publish_faults(good.replace("            exit 0\n", ""))
    assert publish_faults(good.replace("existing=true", "existing=false"))
    assert publish_faults(good.replace("{{.Digest}}", "{{.Id}}"))
    assert publish_faults(good.replace("EXISTING", "OTHER"))
    assert publish_faults(good.replace("anima:$VERSION", "anima:main"))
    assert publish_faults(
        good.replace("needs.verify.outputs.publish == 'true'", "true")
    )
    assert publish_faults(good.replace("podman save", "podman images"))
    cache = (
        "      - uses: actions/cache/restore@55cc8345863c7cc4c66a329aec7e433d2d1c52a9 # v6.1.0\n"
        "        with:\n          path: ~/engine-cache\n          key: k\n"
    )
    assert publish_faults(
        good.replace("      - id: pilot", cache + "      - id: pilot")
    )


# ---- R155: what the release tool writes is not formatted by us and is licensed (PM-012) -------

RELEASE_CONFIG = ROOT / ".github" / "release-please-config.json"
PRETTIER_IGNORE = ROOT / ".prettierignore"
REUSE = ROOT / "REUSE.toml"


def written_files(config):
    """The files the release tool writes besides the manifest: one changelog per package."""
    if config.get("skip-changelog"):
        return []
    found = []
    for path, package in config.get("packages", {}).items():
        base = "" if path == "." else path.rstrip("/") + "/"
        found.append(base + package.get("changelog-path", "CHANGELOG.md"))
    return found


def release_file_faults(files, prettier_ignore, reuse):
    """Each written file that the formatter would check, or that no licensing annotation covers."""
    ignored = {
        line.strip().rstrip("/")
        for line in prettier_ignore.splitlines()
        if line.strip() and not line.startswith("#")
    }
    annotated = [
        glob
        for a in reuse.get("annotations", [])
        for glob in ([a["path"]] if isinstance(a["path"], str) else a["path"])
    ]
    faults = []
    for f in files:
        if f not in ignored:
            faults.append(f"{f} is checked by the formatter")
        if "**" not in annotated and f not in annotated:
            faults.append(f"{f} has no licensing annotation")
    return faults


def test_R155_files_written_by_the_release_tool_are_not_formatted_and_are_licensed():
    """The tool writes its changelog in its own layout, which Prettier rejects
    (PM-012), so the release pull request could not pass the required check."""
    files = written_files(json.loads(RELEASE_CONFIG.read_text()))
    assert files
    reuse = tomllib.loads(REUSE.read_text())
    assert release_file_faults(files, PRETTIER_IGNORE.read_text(), reuse) == []


def test_R155_files_written_by_the_release_tool_are_not_formatted_and_are_licensed_detects_violation():
    reuse = {"annotations": [{"path": "**"}]}
    assert release_file_faults(["CHANGELOG.md"], "# x\nthird_party\n", reuse)
    assert release_file_faults(["CHANGELOG.md"], "CHANGELOG.md\n", {"annotations": []})
    assert not release_file_faults(["CHANGELOG.md"], "CHANGELOG.md\n", reuse)
    assert written_files({"packages": {".": {}}}) == ["CHANGELOG.md"]
    assert written_files({"packages": {"a": {"changelog-path": "N.md"}}}) == ["a/N.md"]
