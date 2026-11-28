"""Work to do and what went wrong: the backlog and the postmortems.
R79, R80, R82 to R85, R166.

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


# ---- R200: waves are recorded and verified ----------------------------------------------

WAVE_ID = re.compile(r"R\d+")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
MAX_BLOCKS = 6


def wave_faults(register, tasks):
    """`register` is the parsed waves.toml; `tasks` the backlog's tasks."""
    faults = []
    waves = register.get("wave", [])
    ids = [w.get("id") for w in waves]
    if len(ids) != len(set(ids)):
        faults.append("a wave id is used twice")
    owner = {}
    for w in waves:
        name = w.get("id", "?")
        if not WAVE_ID.fullmatch(str(w.get("id", ""))):
            faults.append(f"{name}: the id is not R<n>")
        if w.get("branch") not in register.get("integration_branches", []):
            faults.append(f"{name}: its branch is not an integration branch")
        blocks = w.get("blocks", [])
        if not blocks or len(blocks) > MAX_BLOCKS:
            faults.append(
                f"{name}: {len(blocks)} blocks, at most {MAX_BLOCKS}, at least one"
            )
        for block in blocks:
            if owner.setdefault(block, name) != name:
                faults.append(f"{block} belongs to {owner[block]} and {name}")
        record = w.get("verification")
        if w.get("status") == "verified":
            if not isinstance(record, dict):
                faults.append(f"{name}: verified without a record")
            else:
                if not record.get("ran") or not all(record["ran"]):
                    faults.append(f"{name}: the record says nothing ran")
                if not record.get("where"):
                    faults.append(f"{name}: the record does not say where")
                if record.get("result") != "passed":
                    faults.append(f"{name}: the record's result is not passed")
                if not DATE.fullmatch(str(record.get("date", ""))):
                    faults.append(f"{name}: the record has no date")
        elif w.get("status") == "open":
            if record is not None:
                faults.append(f"{name}: open but carries a record")
        else:
            faults.append(f"{name}: status is neither open nor verified")
    for task in tasks:
        wave = task.get("wave")
        if wave not in (None, "none") and wave not in ids:
            faults.append(f"{task['file']}: names the wave {wave}, which is not listed")
    return faults


def test_R200_waves_are_recorded_and_verified():
    faults = wave_faults(load_toml("waves.toml"), read_tasks())
    assert not faults, faults


def test_R200_waves_are_recorded_and_verified_detects_violation():
    record = {
        "ran": ["mise run check"],
        "where": "here",
        "result": "passed",
        "date": "2026-11-28",
    }
    wave = {
        "id": "R1",
        "branch": "b",
        "blocks": ["R1.1"],
        "status": "verified",
        "verification": record,
    }
    register = {"integration_branches": ["b"], "wave": [wave]}
    task = {"file": "t.md", "wave": "R1"}
    assert wave_faults(register, [task]) == []

    def with_wave(**changes):
        return {**register, "wave": [{**wave, **changes}]}

    def without(key):
        return {k: v for k, v in record.items() if k != key}

    assert wave_faults(with_wave(verification=None), [])
    assert wave_faults(with_wave(verification=without("ran")), [])
    assert wave_faults(with_wave(verification={**record, "ran": []}), [])
    assert wave_faults(with_wave(verification=without("where")), [])
    assert wave_faults(with_wave(verification={**record, "result": "failed"}), [])
    assert wave_faults(with_wave(verification={**record, "date": "today"}), [])
    assert wave_faults(with_wave(status="open"), [])  # an open wave with a record
    assert wave_faults(with_wave(status="done"), [])
    assert wave_faults(with_wave(blocks=[f"R1.{i}" for i in range(7)]), [])
    assert wave_faults(with_wave(blocks=[]), [])
    assert wave_faults(with_wave(branch="other"), [])
    assert wave_faults({**register, "wave": [wave, wave]}, [])
    assert wave_faults({**register, "wave": [wave, {**wave, "id": "R2"}]}, [])
    assert wave_faults(register, [{**task, "wave": "R9"}])
    assert wave_faults(register, [{"file": "t.md"}]) == []


# ---- R202: the inventory of what the engine runs ----------------------------------------


def engine_unit_names(engine=ROOT / "engine"):
    """The units that the engine's own files define: `*.container` and `*.service`."""
    return {
        p.name.rsplit(".", 1)[0]
        for suffix in ("container", "service")
        for p in engine.rglob(f"*.{suffix}")
    }


def inventory_faults(inventory, defined, declaration):
    """The inventory lists exactly the units the engine's files define, and every
    container unit has a declared envelope (engine/image/envelopes.toml, R203) not
    below what it was measured to need. The totals are R204's."""
    faults = []
    listed = inventory.get("unit", [])
    units = {u["name"]: u for u in listed}
    if len(units) != len(listed):
        faults.append("a unit is listed twice")
    faults += [f"{n} is defined and not listed" for n in sorted(defined - set(units))]
    faults += [f"{n} is listed and not defined" for n in sorted(set(units) - defined)]
    envelopes = {}
    for e in declaration.get("envelope", []):
        name = e["unit"]
        if name in envelopes:
            faults.append(f"{name}: declared twice")
        envelopes[name] = e
        if name not in units:
            faults.append(f"{name}: an envelope for no unit")
        # What the unit needs is what it was measured to use with the envelope's
        # own settings (`measured_after`), else what it used before (`measured`).
        unit = units.get(name, {})
        measured = unit.get("measured_after") or unit.get("measured", {})
        # The peak of a runtime that grows to whatever it may (an unbounded heap)
        # says what it took, not what it needs: its steady use is compared instead.
        key = (
            "memory_current_mib"
            if measured.get("peak_is_unbounded")
            else "memory_peak_mib"
        )
        if key in measured and e["memory_mib"] < measured[key]:
            faults.append(
                f"{name}: declared {e['memory_mib']} MiB, measured {key} {measured[key]}"
            )
        if not all(e.get(k) for k in ("memory_mib", "cpu_percent", "tasks")):
            faults.append(f"{name}: a bound of memory, CPU or tasks is missing")
    for name, unit in units.items():
        if unit["file"].endswith(".container") and name not in envelopes:
            faults.append(f"{name}: a container without a declared envelope")
    return faults


def test_R202_resource_inventory_covers_every_unit():
    faults = inventory_faults(
        load_toml("resources.toml"),
        engine_unit_names(),
        load_toml("engine/image/envelopes.toml"),
    )
    assert not faults, faults


def test_R202_resource_inventory_covers_every_unit_detects_violation():
    def unit(name, model="C, long-running"):
        return {
            "name": name,
            "file": f"engine/x/{name}.container",
            "process_model": model,
            "measured": {"memory_peak_mib": 10},
        }

    def envelope(name, memory):
        return {"unit": name, "memory_mib": memory, "cpu_percent": 100, "tasks": 8}

    inventory = {"unit": [unit("access"), unit("configure", "shell, one-shot")]}
    declaration = {"envelope": [envelope("access", 100), envelope("configure", 50)]}
    names = {"access", "configure"}
    assert inventory_faults(inventory, names, declaration) == []

    def declared(*envelopes):
        return {"envelope": list(envelopes)}

    two = declaration["envelope"]
    assert inventory_faults(inventory, names | {"b"}, declaration)
    assert inventory_faults(inventory, {"access"}, declaration)
    assert inventory_faults(inventory, names, declared(envelope("access", 5), two[1]))
    # An unbounded peak is not compared, the steady use is.
    unit_a = {
        **unit("access"),
        "measured": {
            "memory_peak_mib": 500,
            "memory_current_mib": 50,
            "peak_is_unbounded": True,
        },
    }
    other = inventory["unit"][1]
    assert inventory_faults({"unit": [unit_a, other]}, names, declaration) == []
    unit_b = {**unit_a, "measured": {**unit_a["measured"], "memory_current_mib": 500}}
    assert inventory_faults({"unit": [unit_b, other]}, names, declaration)
    # The measurement under the envelope's own settings is the one compared.
    after = {**unit_b, "measured_after": {"memory_peak_mib": 20}}
    assert inventory_faults({"unit": [after, other]}, names, declaration) == []
    assert inventory_faults(inventory, names, declared(two[0]))
    assert inventory_faults(inventory, names, declared(*two, two[0]))
    assert inventory_faults(inventory, names, declared(*two, envelope("z", 100)))
    assert inventory_faults(inventory, names, declared(envelope("access", 0), two[1]))


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
    """The tests of the repository, the system tests and those of the promotion, with the file
    that defines each (a guard may be a test that starts the engine)."""
    found = {}
    for directory in ("repository", "system", "promote"):
        for path in sorted((ROOT / "tests" / directory).glob("test_*.py")):
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


def limit_in_days(limits):
    """The limit, held in seconds in the model (GAP-035: the pilot does not check
    a unit, so the unit is asserted here), as a number of days."""
    value, unit = limits["maxTimeOpen"]
    assert unit == "s", f"maxTimeOpen is in {unit}, not in seconds"
    return value / 86400


def test_R85_postmortem_not_open_too_long(model):
    limit = limit_in_days(thresholds(model)["R85"])
    wrong = open_too_long(read_postmortems(), date.today(), limit)
    assert not wrong, wrong


def test_R85_postmortem_not_open_too_long_detects_violation():
    assert limit_in_days({"maxTimeOpen": (1209600, "s")}) == 14
    try:
        limit_in_days({"maxTimeOpen": (14, "B")})
    except AssertionError:
        pass
    else:
        raise AssertionError("a limit in another unit was accepted")
    pms = [_pm(status="open", date="2026-11-01")]
    assert open_too_long(pms, date(2026, 11, 10), 14) == []
    assert open_too_long(pms, date(2026, 11, 20), 14)
    assert open_too_long([_pm(date="2026-01-01")], date(2026, 11, 20), 14) == []


# ---- R166: a postmortem names its root cause, its class and the options -----------------------

ROOTED_SECTIONS = (
    "Root cause",
    "Class and earlier occurrences",
    "Design options",
    "Decision on the options",
)


def rooted_faults(pms, first):
    """Every postmortem numbered `first` or later has the four sections, none empty."""
    faults = []
    for pm in pms:
        number = int(pm["id"].split("-")[1])
        if number < first:
            continue
        parts = re.split(r"^## ", pm["body"], flags=re.MULTILINE)[1:]
        sections = {p.split("\n", 1)[0].strip(): p.split("\n", 1)[-1] for p in parts}
        for name in ROOTED_SECTIONS:
            text = re.sub(r"<!--.*?-->", "", sections.get(name, ""), flags=re.DOTALL)
            if not text.strip():
                faults.append(f"{pm['id']}: section '{name}' is missing or empty")
    return faults


def test_R166_postmortem_names_root_and_class_options(model):
    first, _unit = thresholds(model)["R166"]["firstRootedPostmortem"]
    faults = rooted_faults(read_postmortems(), int(first))
    assert not faults, faults


def test_R166_postmortem_names_root_and_class_options_detects_violation():
    full = "".join(f"## {n}\n\ntext\n\n" for n in ROOTED_SECTIONS)
    old = _pm(id="PM-013", body="## Overview\n\nx\n")
    assert rooted_faults([old], 14) == []  # history is not rewritten
    assert rooted_faults([_pm(id="PM-014", body=full)], 14) == []
    assert rooted_faults([_pm(id="PM-014", body="## Overview\n\nx\n")], 14)
    assert rooted_faults([_pm(id="PM-014", body=full.replace("text", "", 1))], 14)
    assert rooted_faults(
        [_pm(id="PM-015", body=full.replace("Design options", "X"))], 14
    )
    assert rooted_faults(
        [_pm(id="PM-014", body=full.replace("text", "<!-- c -->", 1))], 14
    )


# ---- R167: a spike says why no test inside the task answers its question -------------------

WHY_NO_TEST = re.compile(
    r"^- Why a test inside the task cannot answer it:[ \t]*(\S.*)$", re.MULTILINE
)


def spike_faults(tasks):
    """Every task of role spike has the line, with a reason, in its brief."""
    return [
        f"{t['file']}: a spike task does not say why no test inside the task can answer it"
        for t in tasks
        if t.get("role") == "spike" and not WHY_NO_TEST.search(t.get("body", ""))
    ]


def test_R167_spike_brief_states_why_no_test_answers():
    tasks = []
    for path in sorted((ROOT / "backlog" / "tasks").glob("*.md")):
        fields, body = al.read_document(path)
        tasks.append({**fields, "file": path.name, "body": body})
    faults = spike_faults(tasks)
    assert not faults, faults


def test_R167_spike_brief_states_why_no_test_answers_detects_violation():
    line = "- Why a test inside the task cannot answer it: nothing exists to test"
    spike = {"file": "t.md", "role": "spike", "body": f"### Decision\n\n{line}\n"}
    assert spike_faults([spike]) == []
    assert spike_faults([{**spike, "body": "### Decision\n\n- x\n"}])
    assert spike_faults(
        [{**spike, "body": "- Why a test inside the task cannot answer it:   \n"}]
    )
    assert spike_faults(
        [{**spike, "body": "- Why a test inside the task cannot answer it:\n- y"}]
    )
    assert spike_faults([{**spike, "role": "implementer"}]) == []
