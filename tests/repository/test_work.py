"""Work to do and what went wrong: the backlog and the postmortems.
R79, R80, R82 to R85.

Each check is a function of its inputs; its companion test
(`<name>_detects_violation`) feeds it a deliberately wrong input.
"""

import ast
import re
from datetime import date

import agent_layer as al
from repo_facts import load_toml
from sysml_model import (
    NEGATIVE_SUFFIX,
    ROOT,
    thresholds,
    verifications,
)

# ---- The backlog: tasks as data ------------------------------------------------------

AC = re.compile(r"^- \[[ xX]\] #\d+ (.*)$", re.MULTILINE)


def read_tasks(directory=ROOT / "backlog" / "tasks"):
    """[{front matter..., "acceptance": [...], "sections": [...]}] of every task."""
    tasks = []
    for path in sorted(directory.glob("*.md")):
        fields, body = al.read_document(path)
        block = body.partition("<!-- AC:BEGIN -->")[2].partition("<!-- AC:END -->")[0]
        tasks.append(
            {
                **fields,
                "file": path.name,
                "acceptance": AC.findall(block),
                "sections": re.findall(r"^## (.+?)\s*$", body, re.MULTILINE),
            }
        )
    return tasks


# ---- R79: every open gap has a task ----------------------------------------------------


def gap_task_faults(gaps, tasks):
    """`gaps` is [{id, status}]. Every open gap is named by a task; a task that
    is an upstream contribution names a gap that exists."""
    ids = {g["id"] for g in gaps}
    named = {i for t in tasks for i in t.get("gaps", [])}
    faults = [
        f"{g['id']} is open and no task names it"
        for g in gaps
        if g["status"] == "open" and g["id"] not in named
    ]
    for task in tasks:
        listed = task.get("gaps", [])
        if "upstream" in task.get("labels", []) and not listed:
            faults.append(f"{task['file']}: an upstream task names no gap")
        faults += [
            f"{task['file']}: names {i}, which is not a gap"
            for i in listed
            if i not in ids
        ]
    return faults


def test_R79_every_open_gap_has_a_task():
    tasks = read_tasks()
    assert tasks, "the backlog has no task"
    faults = gap_task_faults(load_toml("gaps.toml")["gap"], tasks)
    assert not faults, faults


def test_R79_every_open_gap_has_a_task_detects_violation():
    gaps = [{"id": "GAP-001", "status": "open"}, {"id": "GAP-002", "status": "closed"}]
    task = {"file": "t.md", "labels": ["upstream"], "gaps": ["GAP-001"]}
    assert gap_task_faults(gaps, [task]) == []
    assert gap_task_faults(gaps, [])  # an open gap with no task
    assert gap_task_faults(gaps, [{**task, "gaps": []}])  # upstream names no gap
    assert gap_task_faults(gaps, [{**task, "gaps": ["GAP-001", "GAP-009"]}])
    # A closed gap needs no task.
    assert gap_task_faults(gaps[1:], [{"file": "t.md", "labels": [], "gaps": []}]) == []


# ---- R80: the acceptance of a task names verifications ----------------------------------


def task_faults(tasks, verification_names):
    faults = []
    for task in tasks:
        name = task["file"]
        if not task["acceptance"]:
            faults.append(f"{name}: no acceptance line")
        for line in task["acceptance"]:
            word = line.split()[0] if line.split() else ""
            if word.startswith("test_R"):
                if word not in verification_names:
                    faults.append(f"{name}: {word} is not a verification of the model")
            elif not line.startswith("Check: "):
                faults.append(f"{name}: {line!r} is neither a verification nor a check")
        for section in ("Description", "Acceptance Criteria", "Brief", "Report"):
            if section not in task["sections"]:
                faults.append(f"{name}: no section {section}")
    return faults


def test_R80_task_acceptance_names_verifications(model):
    faults = task_faults(read_tasks(), set(verifications(model)))
    assert not faults, faults


def test_R80_task_acceptance_names_verifications_detects_violation():
    sections = ["Description", "Acceptance Criteria", "Brief", "Report"]
    task = {"file": "t.md", "acceptance": ["test_R1_x"], "sections": sections}
    known = {"test_R1_x"}
    assert task_faults([task], known) == []
    assert task_faults([{**task, "acceptance": ["Check: it runs"]}], known) == []
    assert task_faults([{**task, "acceptance": []}], known)
    assert task_faults([{**task, "acceptance": ["test_R9_gone"]}], known)
    assert task_faults([{**task, "acceptance": ["It works"]}], known)
    assert task_faults([{**task, "sections": sections[:3]}], known)
    # A long title is written by the tool as a folded block scalar with a colon in it.
    folded = al.parse_yaml(
        "id: TASK-1\ntitle: >-\n  GAP-1: a long\n  title\nstatus: To Do"
    )
    assert folded["title"] == "GAP-1: a long title" and folded["status"] == "To Do"


# ---- Postmortems --------------------------------------------------------------------------

PM_KEYS = {"id", "date", "title", "class", "status", "guards", "recurrences"}
STATUSES = ("closed-by-design", "guarded", "mitigated", "open")
# Strongest first: design, then test, then the mitigations.
STRENGTH = {"design": 5, "test": 4, "scenario": 3, "detection": 2, "rule": 1}
STATUS_OF = {
    5: "closed-by-design",
    4: "guarded",
    3: "mitigated",
    2: "mitigated",
    1: "mitigated",
}


def read_postmortems(directory=ROOT / "docs" / "postmortems"):
    found = []
    for path in sorted(directory.glob("PM-*.md")):
        fields, body = al.read_document(path)
        found.append({**fields, "file": path.name, "body": body})
    return found


def shape_faults(pms):
    """Keys, id and file name, status values, guard shape, unique ids."""
    faults = []
    ids = [p.get("id") for p in pms]
    if len(ids) != len(set(ids)):
        faults.append("an id is used twice")
    for pm in pms:
        name = pm["file"]
        if set(pm) - {"file", "body"} != PM_KEYS:
            faults.append(f"{name}: keys are not {sorted(PM_KEYS)}")
            continue
        if not re.fullmatch(r"PM-\d{3}", pm["id"]) or not name.startswith(
            pm["id"] + "-"
        ):
            faults.append(f"{name}: the id does not match the file name")
        if pm["status"] not in STATUSES:
            faults.append(f"{name}: status {pm['status']} is not one of {STATUSES}")
        for guard in pm["guards"]:
            if not isinstance(guard, dict) or set(guard) != {"kind", "ref", "added"}:
                faults.append(f"{name}: a guard needs kind, ref and added")
            elif guard["kind"] not in STRENGTH:
                faults.append(f"{name}: guard kind {guard['kind']} is unknown")
    return faults


# ---- R82: the guards exist ------------------------------------------------------------------


def guard_faults(pm, read, tests):
    """`read(path)` is the text of a repository file or None; `tests` is
    {test name: path of the file that defines it} with the companions included."""
    faults = []
    pid = pm["id"]
    for guard in pm["guards"]:
        kind, ref = guard["kind"], guard["ref"]
        label = f"{pid} {kind} {ref}"
        if kind == "design":
            adr = next(
                (
                    t
                    for p in sorted((ROOT / "docs" / "adr").glob(f"{ref}-*.md"))
                    if (t := p.read_text())
                ),
                None,
            )
            if adr is None:
                faults.append(f"{label}: no such decision record")
            elif pid not in adr:
                faults.append(f"{label}: the record does not carry {pid}")
        elif kind == "test":
            path = tests.get(ref)
            if path is None or ref + NEGATIVE_SUFFIX not in tests:
                faults.append(f"{label}: no such test with its negative case")
            elif pid not in (read(path) or ""):
                faults.append(f"{label}: the test file does not carry {pid}")
        elif kind == "scenario":
            text = read("docs/evaluation/scenarios.md") or ""
            section = re.search(
                rf"^## {re.escape(ref)}\b(.*?)(?=^## |\Z)",
                text,
                re.MULTILINE | re.DOTALL,
            )
            if section is None:
                faults.append(f"{label}: no such scenario")
            elif pid not in section[1]:
                faults.append(f"{label}: the scenario does not carry {pid}")
        else:  # rule and detection: a file of the repository that carries the id
            text = read(ref)
            if text is None:
                faults.append(f"{label}: no such file")
            elif pid not in text:
                faults.append(f"{label}: the file does not carry {pid}")
    return faults


def repository_read(path):
    full = ROOT / path
    return full.read_text() if full.is_file() else None


def written_test_functions():
    found = {}
    for path in sorted((ROOT / "tests" / "repository").glob("test_*.py")):
        for name in defined_function_names_of(path):
            found[name] = str(path.relative_to(ROOT))
    return found


def defined_function_names_of(path):
    return {
        n.name
        for n in ast.walk(ast.parse(path.read_text()))
        if isinstance(n, ast.FunctionDef)
    }


def test_R82_postmortem_guards_exist():
    pms = read_postmortems()
    assert pms, "no postmortem"
    faults = shape_faults(pms)
    for pm in pms:
        faults += guard_faults(pm, repository_read, written_test_functions())
    assert not faults, faults


def test_R82_postmortem_guards_exist_detects_violation():
    files = {
        "agents/x.md": "a rule (PM-001)",
        "docs/evaluation/scenarios.md": "## S-1 x\n\nPM-001\n",
    }
    tests = {"test_R1_a": "t.py", "test_R1_a" + NEGATIVE_SUFFIX: "t.py"}
    files["t.py"] = "# PM-001\n"

    def faults(kind, ref, pid="PM-001"):
        pm = {"id": pid, "guards": [{"kind": kind, "ref": ref, "added": "2026-11-27"}]}
        return guard_faults(pm, files.get, tests)

    assert faults("rule", "agents/x.md") == []
    assert faults("rule", "agents/missing.md")
    assert faults("rule", "agents/x.md", pid="PM-002")
    assert faults("detection", "agents/x.md") == []
    assert faults("test", "test_R1_a") == []
    assert faults("test", "test_R1_a", pid="PM-002")
    assert faults("test", "test_R9_gone")
    assert faults("test", "test_R1_a") == []
    assert faults("scenario", "S-1") == []
    assert faults("scenario", "S-2")
    assert faults("scenario", "S-1", pid="PM-002")
    assert faults("design", "9999")
    assert shape_faults([{"file": "PM-001-x.md", "id": "PM-001"}])
    assert shape_faults([_pm(), _pm()])
    assert shape_faults([_pm(status="done")])
    assert shape_faults([_pm(guards=[{"kind": "magic", "ref": "x", "added": "d"}])])
    assert shape_faults([_pm(guards=[{"kind": "rule", "ref": "x"}])])
    assert shape_faults([_pm()]) == []


def _pm(**change):
    pm = {
        "file": "PM-001-x.md",
        "body": "",
        "id": "PM-001",
        "date": "2026-11-27",
        "title": "t",
        "class": "c",
        "status": "mitigated",
        "guards": [{"kind": "rule", "ref": "x", "added": "2026-11-27"}],
        "recurrences": [],
    }
    return {**pm, **change}


# ---- R83: the status agrees with the guards -----------------------------------------------


def status_faults(pm):
    kinds = {g["kind"] for g in pm["guards"]}
    top = max((STRENGTH[k] for k in kinds), default=0)
    expected = STATUS_OF.get(top, "open")
    faults = []
    if pm["status"] != expected:
        faults.append(
            f"{pm['id']}: status is {pm['status']}, its guards say {expected}"
        )
    if "judgement" in pm["class"].lower() and pm["status"] in (
        "closed-by-design",
        "guarded",
    ):
        faults.append(f"{pm['id']}: an error of judgement is at most mitigated")
    return faults


def test_R83_postmortem_status_agrees_with_guards():
    faults = [f for pm in read_postmortems() for f in status_faults(pm)]
    assert not faults, faults


def test_R83_postmortem_status_agrees_with_guards_detects_violation():
    def guard(kind):
        return {"kind": kind, "ref": "x", "added": "2026-11-27"}

    assert status_faults(_pm()) == []
    assert status_faults(_pm(status="guarded"))  # only a rule
    assert status_faults(_pm(status="open"))  # has a guard
    assert status_faults(_pm(status="mitigated", guards=[guard("test")]))
    assert status_faults(_pm(status="guarded", guards=[guard("test")])) == []
    assert status_faults(_pm(status="closed-by-design", guards=[guard("test")]))
    assert status_faults(_pm(status="open", guards=[])) == []
    judged = _pm(**{"class": "error of judgement"})
    assert status_faults(judged) == []
    assert status_faults({**judged, "status": "guarded", "guards": [guard("test")]})
    assert status_faults(
        {**judged, "status": "closed-by-design", "guards": [guard("design")]}
    )


# ---- R84: a recurrence needs a stronger guard -----------------------------------------------


def recurrence_faults(pm):
    """For each recurrence after the first: a guard added on or after it, stronger
    than the strongest guard added before it."""
    faults = []
    recurrences = sorted(pm["recurrences"])
    for when in recurrences[1:]:
        before = max(
            (STRENGTH[g["kind"]] for g in pm["guards"] if g["added"] < when), default=0
        )
        if not any(
            g["added"] >= when and STRENGTH[g["kind"]] > before for g in pm["guards"]
        ):
            faults.append(f"{pm['id']}: the recurrence of {when} has no stronger guard")
    return faults


def test_R84_postmortem_recurrence_needs_stronger_guard():
    faults = [f for pm in read_postmortems() for f in recurrence_faults(pm)]
    assert not faults, faults


def test_R84_postmortem_recurrence_needs_stronger_guard_detects_violation():
    def guard(kind, added):
        return {"kind": kind, "ref": "x", "added": added}

    twice = ["2026-11-01", "2026-11-10"]
    assert recurrence_faults(_pm(recurrences=[])) == []
    assert recurrence_faults(_pm(recurrences=["2026-11-01"])) == []  # the first is free
    guards = [guard("rule", "2026-10-01")]
    assert recurrence_faults(_pm(recurrences=twice, guards=guards))  # not stronger
    guards = [guard("rule", "2026-10-01"), guard("scenario", "2026-11-10")]
    assert recurrence_faults(_pm(recurrences=twice, guards=guards)) == []
    guards = [guard("scenario", "2026-10-01"), guard("rule", "2026-11-10")]
    assert recurrence_faults(_pm(recurrences=twice, guards=guards))  # weaker, later


# ---- R85: not open too long ------------------------------------------------------------------


def open_too_long(pms, today, limit):
    return [
        f"{pm['id']}: open since {pm['date']}"
        for pm in pms
        if pm["status"] == "open"
        and (today - date.fromisoformat(pm["date"])).days > limit
    ]


def test_R85_postmortem_not_open_too_long(model):
    limit = thresholds(model)["R85"]["maxDaysOpen"][0]
    wrong = open_too_long(read_postmortems(), date.today(), limit)
    assert not wrong, wrong


def test_R85_postmortem_not_open_too_long_detects_violation():
    pms = [_pm(status="open", date="2026-11-01")]
    assert open_too_long(pms, date(2026, 11, 10), 14) == []
    assert open_too_long(pms, date(2026, 11, 20), 14)
    assert open_too_long([_pm(date="2026-01-01")], date(2026, 11, 20), 14) == []
