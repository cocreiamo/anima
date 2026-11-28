"""The resource envelopes of the engine's units. R203 to R206.

An envelope is a memory limit, a processor bound and a task limit. The declaration
is `engine/image/envelopes.toml`; the units are discovered from the engine's files,
never listed here. Each check is a function of its inputs; its companion test
(`<name>_detects_violation`) feeds it a deliberately wrong input.
"""

import copy
import importlib.machinery
import importlib.util
import json
import re
import subprocess
import sys

from repo_facts import load_toml
from sysml_model import ROOT, thresholds

DECLARATION = "engine/image/envelopes.toml"
ENVIRONMENT_DIRECTORY = "/run/anima/config/envelope"


# ---- discovery: the units the engine runs ------------------------------------


def discover_units(engine=ROOT / "engine", containerfile=None):
    """{unit: (kind, text)} for every unit the engine defines: a `.container` and a
    `.service` under its own name, an `.image` as `<name>-image` and a `.pod` as
    `<name>-pod` (Quadlet's names), and every service that the image enables. A
    target carries no process and is not a unit of this kind."""
    kinds = {"container": "", "service": "", "image": "-image", "pod": "-pod"}
    found = {}
    for suffix, tail in kinds.items():
        for path in sorted(engine.rglob(f"*.{suffix}")):
            found[path.stem + tail] = (suffix, path.read_text())
    containerfile = containerfile or engine / "image" / "Containerfile"
    for line in re.findall(r"systemctl enable ([^\\&\n]+)", containerfile.read_text()):
        for name in line.split():
            if name.endswith(".service") and name[: -len(".service")] not in found:
                found[name[: -len(".service")]] = ("enabled", "")
    return found


def keys(text, section=None):
    """{key: [values]} of the lines `Key=Value`, of one section or of all."""
    current, found = None, {}
    for line in text.splitlines():
        header = re.match(r"^\[(\w+)\]$", line.strip())
        if header:
            current = header.group(1)
        match = re.match(r"^([A-Za-z]+)=(.*)$", line)
        if match and (section is None or section == current):
            found.setdefault(match.group(1), []).append(match.group(2))
    return found


def unit_faults(declaration, units, max_exempt):
    """What is wrong with the envelopes of the units: a unit with no envelope, a
    bound of a unit that is missing or does not come from the declaration, a
    declared unit that does not exist, a bound that is not a positive whole
    number, and more exemptions than allowed."""
    faults = []
    envelopes = {e["unit"]: e for e in declaration.get("envelope", [])}
    hosts = {h["unit"]: h for h in declaration.get("host_unit", [])}
    classes = {c["name"]: c for c in declaration.get("class", [])}
    exempt = {x["unit"]: x for x in declaration.get("exempt", [])}
    declared = set(envelopes) | set(hosts) | set(exempt)
    for name in sorted(set(units) - declared):
        faults.append(f"{name}: a unit of the engine with no envelope")
    for name in sorted(declared - set(units)):
        faults.append(f"{name}: declared, but the engine has no such unit")
    if len(exempt) > max_exempt:
        faults.append(f"{len(exempt)} units without an envelope, at most {max_exempt}")
    for name, reason in ((n, x.get("reason")) for n, x in exempt.items()):
        if not reason:
            faults.append(f"{name}: exempt without a reason")
    for kind, table in (("envelope", envelopes), ("class", classes)):
        for name, entry in table.items():
            for bound in ("memory_mib", "cpu_percent", "tasks"):
                value = entry.get(bound)
                if type(value) is not int or value <= 0:
                    faults.append(f"{kind} {name}: {bound} is not a positive number")
    for name, entry in hosts.items():
        if entry.get("class") not in classes:
            faults.append(f"{name}: class {entry.get('class')} is not declared")
    for name, (kind, text) in units.items():
        if name in envelopes and kind == "container":
            faults += container_faults(name, text)
        elif name in hosts and kind in ("service", "image"):
            faults += host_faults(name, text, classes.get(hosts[name].get("class"), {}))
        elif name in envelopes or name in hosts:
            faults.append(f"{name}: declared as another kind of unit than it is")
    return faults


def container_faults(name, text):
    """A container unit passes the three bounds from the unit's own env file, which
    the configuration reader writes from the declaration."""
    faults = []
    args = " ".join(keys(text, "Container").get("PodmanArgs", []))
    for what, flag in (
        ("memory limit", "--memory=${ANIMA_MEMORY}"),
        ("memory and swap limit", "--memory-swap=${ANIMA_MEMORY}"),
        ("CPU bound", "--cpus=${ANIMA_CPUS}"),
        ("task limit", "--pids-limit=${ANIMA_PIDS}"),
    ):
        if flag not in args.split():
            faults.append(f"{name}: no {what} (PodmanArgs lacks {flag})")
    path = f"{ENVIRONMENT_DIRECTORY}/{name}.env"
    for section in ("Container", "Service"):
        if path not in keys(text, section).get("EnvironmentFile", []):
            faults.append(f"{name}: [{section}] does not read {path}")
    for key in ("Memory", "MemoryMax", "CPUQuota", "TasksMax", "PidsLimit"):
        if key in keys(text):
            faults.append(f"{name}: {key}= repeats a number the declaration holds")
    return faults


def host_faults(name, text, cls):
    """A unit of the host side carries its class's numbers in its own file."""
    faults = []
    service = keys(text, "Service")
    expected = {
        "MemoryMax": f"{cls.get('memory_mib')}M",
        "CPUQuota": f"{cls.get('cpu_percent')}%",
        "TasksMax": str(cls.get("tasks")),
    }
    for key, value in expected.items():
        found = service.get(key)
        if not found:
            faults.append(f"{name}: no {key}=")
        elif found != [value]:
            faults.append(f"{name}: {key}={found[0]}, the declaration says {value}")
    return faults


def test_R203_every_unit_has_its_declared_envelope(model):
    limit, unit = thresholds(model)["R203"]["maxUnitsWithoutEnvelope"]
    assert unit is None
    faults = unit_faults(load_toml(DECLARATION), discover_units(), limit)
    assert not faults, faults


def test_R203_every_unit_has_its_declared_envelope_detects_violation():
    declaration = load_toml(DECLARATION)
    units = discover_units()
    assert unit_faults(declaration, units, 1) == []
    # A unit of the engine that nothing declares.
    stranger = {**units, "stranger": ("container", "[Container]\n")}
    assert any("stranger" in f for f in unit_faults(declaration, stranger, 1))
    # A declaration of a unit the engine does not have.
    fewer = {k: v for k, v in units.items() if k != "mail"}
    assert any(
        "mail" in f and "no such" in f for f in unit_faults(declaration, fewer, 1)
    )
    # Each bound missing from a container unit is named.
    text = units["access"][1]
    for flag, what in (
        ("--memory=${ANIMA_MEMORY}", "memory limit"),
        ("--cpus=${ANIMA_CPUS}", "CPU bound"),
        ("--pids-limit=${ANIMA_PIDS}", "task limit"),
    ):
        broken = {**units, "access": ("container", text.replace(flag, ""))}
        assert any(
            "access" in f and what in f for f in unit_faults(declaration, broken, 1)
        ), what
    # A number written by hand beside the declaration.
    handwritten = {**units, "access": ("container", text + "\nMemory=4g\n")}
    assert any("Memory=" in f for f in unit_faults(declaration, handwritten, 1))
    # A host unit without a bound, and one that differs from its class.
    host = units["anima-config"][1]
    for key in ("MemoryMax", "CPUQuota", "TasksMax"):
        broken = re.sub(rf"^{key}=.*\n", "", host, flags=re.MULTILINE)
        unbound = {**units, "anima-config": ("service", broken)}
        assert any(key in f for f in unit_faults(declaration, unbound, 1)), key
    other = re.sub(r"MemoryMax=\w+", "MemoryMax=9999M", host)
    assert unit_faults(declaration, {**units, "anima-config": ("service", other)}, 1)
    # More exemptions than the threshold allows.
    assert any("without an envelope" in f for f in unit_faults(declaration, units, 0))
    # A bound that is not a positive whole number.
    wrong = copy.deepcopy(declaration)
    wrong["envelope"][0]["memory_mib"] = 0
    assert unit_faults(wrong, units, 1)
    wrong["envelope"][0]["memory_mib"] = "unlimited"
    assert unit_faults(wrong, units, 1)


# ---- R204: the total of the defaults -----------------------------------------


def engine_memory(declaration, with_optional, floors=False):
    """The memory that the units which run at the same time can use (MiB): the
    defaults (or, with `floors`, the floors of those that may be lowered) of the
    units marked `concurrent`, those marked `optional` only when asked, and the
    allowance for the operating system."""
    total = declaration["engine"]["operating_system_allowance_mib"]
    for e in declaration["envelope"]:
        if not e.get("concurrent") or (e.get("optional") and not with_optional):
            continue
        total += (
            e.get("memory_floor_mib", e["memory_mib"]) if floors else e["memory_mib"]
        )
    return total


def total_faults(declaration, limit, limit_with_optional, adopter):
    faults = []
    for label, with_optional, bound in (
        ("the engine", False, limit),
        ("the engine with the mail stand-in", True, limit_with_optional),
    ):
        total = engine_memory(declaration, with_optional)
        if total > bound:
            faults.append(f"{label}: defaults sum to {total} MiB, the limit is {bound}")
    stated = (
        adopter.get("default_engine_memory_mib"),
        adopter.get("floor_engine_memory_mib"),
    )
    derived = (
        engine_memory(declaration, False),
        engine_memory(declaration, False, floors=True),
    )
    if stated != derived:
        faults.append(f"the adopter-facing numbers are {stated}, derived {derived}")
    return faults


def test_R204_engine_total_stays_within_its_limit(model):
    limits = thresholds(model)["R204"]
    assert limits["maxEngineMemory"][1] is None
    faults = total_faults(
        load_toml(DECLARATION),
        limits["maxEngineMemory"][0],
        limits["maxEngineMemoryWithMailStandIn"][0],
        load_toml("resources.toml").get("adopter", {}),
    )
    assert not faults, faults


def test_R204_engine_total_stays_within_its_limit_detects_violation():
    declaration = load_toml(DECLARATION)
    default = engine_memory(declaration, False)
    with_mail = engine_memory(declaration, True)
    adopter = {
        "default_engine_memory_mib": default,
        "floor_engine_memory_mib": engine_memory(declaration, False, floors=True),
    }
    assert total_faults(declaration, default, with_mail, adopter) == []
    assert total_faults(declaration, default - 1, with_mail, adopter)
    assert total_faults(declaration, default, with_mail - 1, adopter)
    assert total_faults(
        declaration, default, with_mail, {**adopter, "floor_engine_memory_mib": 1}
    )
    bigger = copy.deepcopy(declaration)
    bigger["envelope"][0]["memory_mib"] += 1024
    assert total_faults(bigger, default, with_mail, adopter)


# ---- R205: each service's own knobs come from its envelope -------------------


def load_config_tool():
    path = str(ROOT / "engine/image/anima-config")
    loader = importlib.machinery.SourceFileLoader("anima_config", path)
    spec = importlib.util.spec_from_loader("anima_config", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def number(text):
    return int(re.match(r"\d+", text).group())


def knob_faults(declaration, inventory, tool):
    """The knobs of every service, derived at its default and at its floor, must
    exist for its runtime and fit inside its limit."""
    faults = []
    runtime = {u["name"]: u["process_model"] for u in inventory["unit"]}
    for envelope in declaration["envelope"]:
        name = envelope["unit"]
        model = runtime.get(name, "")
        for label, memory in (
            ("default", envelope["memory_mib"]),
            ("floor", envelope.get("memory_floor_mib")),
        ):
            if memory is None:
                continue
            values = {"memory_mib": memory, "cpu_percent": 100, "tasks": 64}
            derived = tool.native_settings(envelope, values)
            env, conf = derived["env"], derived["conf"]
            where = f"{name} at its {label} ({memory} MiB)"
            if env.get("ANIMA_MEMORY") != f"{memory}m":
                faults.append(f"{where}: the memory limit is not the envelope's")
            if "Go" in model:
                if "GOMEMLIMIT" not in env:
                    faults.append(f"{where}: a Go program with no soft memory limit")
                elif number(env["GOMEMLIMIT"]) >= memory:
                    faults.append(f"{where}: GOMEMLIMIT is not below the limit")
            if "JVM" in model:
                if (
                    "JAVA_OPTS_KC_HEAP" not in env
                    or "-Xmx" not in env["JAVA_OPTS_KC_HEAP"]
                ):
                    faults.append(
                        f"{where}: a JVM whose heap is not bounded explicitly"
                    )
                else:
                    heap = number(env["JAVA_OPTS_KC_HEAP"].split("-Xmx")[1])
                    if heap * 2 > memory:
                        faults.append(
                            f"{where}: heap {heap} MiB is over half the limit"
                        )
                pool = number(env.get("KC_DB_POOL_MAX_SIZE", "0"))
                other = declaration_database(declaration)
                if not 0 < pool <= number(other["max_connections"]) - 3:
                    faults.append(
                        f"{where}: pool {pool} does not fit the connection limit"
                    )
            if "PostgreSQL" in model:
                if not conf:
                    faults.append(
                        f"{where}: no memory settings for the database server"
                    )
                else:
                    shared = number(conf["shared_buffers"])
                    work = number(conf["maintenance_work_mem"]) * number(
                        conf["autovacuum_max_workers"]
                    )
                    if (shared + work) * 2 > memory:
                        faults.append(
                            f"{where}: buffers {shared + work} MiB over half the limit"
                        )
                    if "max_connections" not in conf:
                        faults.append(f"{where}: no connection limit")
    return faults


def declaration_database(declaration):
    envelope = next(e for e in declaration["envelope"] if e["unit"] == "database")
    return {"max_connections": str(envelope["max_connections"])}


def test_R205_service_knobs_derive_from_the_envelope():
    faults = knob_faults(
        load_toml(DECLARATION), load_toml("resources.toml"), load_config_tool()
    )
    assert not faults, faults


def test_R205_service_knobs_derive_from_the_envelope_detects_violation():
    tool = load_config_tool()
    declaration = load_toml(DECLARATION)
    inventory = load_toml("resources.toml")
    assert knob_faults(declaration, inventory, tool) == []

    def without(unit, field):
        copied = copy.deepcopy(declaration)
        envelope = next(e for e in copied["envelope"] if e["unit"] == unit)
        del envelope[field]
        return copied

    # A Go program with no soft limit would be able to grow to the whole limit.
    assert knob_faults(without("secrets", "go_memlimit_percent"), inventory, tool)
    assert knob_faults(without("access", "heap_percent"), inventory, tool)
    assert knob_faults(without("database", "shared_buffers_percent"), inventory, tool)
    big = copy.deepcopy(declaration)
    next(e for e in big["envelope"] if e["unit"] == "access")["heap_percent"] = 90
    assert knob_faults(big, inventory, tool)
    big = copy.deepcopy(declaration)
    next(e for e in big["envelope"] if e["unit"] == "database")[
        "shared_buffers_percent"
    ] = 80
    assert knob_faults(big, inventory, tool)
    big = copy.deepcopy(declaration)
    next(e for e in big["envelope"] if e["unit"] == "access")["db_pool_max"] = 500
    assert knob_faults(big, inventory, tool)
    big = copy.deepcopy(declaration)
    next(e for e in big["envelope"] if e["unit"] == "mail")["go_memlimit_percent"] = 100
    assert knob_faults(big, inventory, tool)


# ---- R206: overrides are configuration; the absence of a limit cannot be written


def run_tool(tmp_path, base=None):
    """Run the configuration reader on a temporary configuration; returns (code,
    message, run directory)."""
    config, run, defaults = tmp_path / "config", tmp_path / "run", tmp_path / "defaults"
    config.mkdir(parents=True)
    defaults.mkdir()
    for name, text in (base or {}).items():
        (config / name).parent.mkdir(parents=True, exist_ok=True)
        (config / name).write_text(text)
    environment = {
        "ANIMA_DEFAULTS_DIR": str(defaults),
        "ANIMA_CONFIG_DIR": str(config),
        "ANIMA_CONFIG_RUN_DIR": str(run),
        "ANIMA_ENVELOPES_FILE": str(ROOT / DECLARATION),
        "ANIMA_PROFILE_FILE": str(tmp_path / "none"),
        "PATH": "/usr/bin:/bin",
    }
    result = subprocess.run(
        [sys.executable, str(ROOT / "engine/image/anima-config")],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr, run


def env_file(run, unit):
    lines = (run / "envelope" / f"{unit}.env").read_text().splitlines()
    return dict(line.split("=", 1) for line in lines)


def test_R206_override_is_configuration_and_visible(tmp_path):
    declaration = load_toml(DECLARATION)
    # Nothing written: every container unit gets all three bounds, from the declaration.
    code, out, run = run_tool(tmp_path / "defaults")
    assert code == 0, out
    for envelope in declaration["envelope"]:
        values = env_file(run, envelope["unit"])
        assert values["ANIMA_MEMORY"] == f"{envelope['memory_mib']}m"
        assert values["ANIMA_PIDS"] == str(envelope["tasks"])
        assert float(values["ANIMA_CPUS"]) == envelope["cpu_percent"] / 100
    # An adopter gives the identity provider more room: the limit, the heap that
    # follows it and the visible effective envelope all change.
    base = {"access/access.toml": "[resources]\nmemory_mib = 1024\ncpu_percent = 300\n"}
    code, out, run = run_tool(tmp_path / "override", base)
    assert code == 0, out
    values = env_file(run, "access")
    assert values["ANIMA_MEMORY"] == "1024m" and values["ANIMA_CPUS"] == "3.00"
    assert "-Xmx440m" in values["JAVA_OPTS_KC_HEAP"]
    shown = json.loads((run / "envelopes.json").read_text())
    assert (
        shown["access"]["memory_mib"] == 1024 and shown["database"]["memory_mib"] == 768
    )
    effective = json.loads((run / "effective.json").read_text())
    assert effective["access"]["resources"]["memory_mib"] == 1024
    # The database server's memory settings follow its envelope.
    base = {"database/database.toml": "[resources]\nmemory_mib = 1024\n"}
    code, out, run = run_tool(tmp_path / "database", base)
    assert code == 0, out
    assert "shared_buffers = '204MB'" in (run / "envelope/database.conf").read_text()


def test_R206_override_is_configuration_and_visible_detects_violation(tmp_path):
    """A limit cannot be removed: zero, a negative number, a word, a decimal, a
    boolean, a value below the floor and a value past the ceiling are each refused,
    naming the file and the setting, and nothing is written."""
    cases = {
        "memory_mib = 0": "access.resources.memory_mib",
        "memory_mib = -1": "access.resources.memory_mib",
        'memory_mib = "unlimited"': "access.resources.memory_mib",
        'memory_mib = "max"': "access.resources.memory_mib",
        "memory_mib = 1.5": "access.resources.memory_mib",
        "memory_mib = true": "access.resources.memory_mib",
        "memory_mib = 100": "floor",
        "memory_mib = 99999999999": "above",
        "cpu_percent = 0": "access.resources.cpu_percent",
        "tasks = 0": "access.resources.tasks",
        'tasks = "unlimited"': "access.resources.tasks",
        "memoryy_mib = 700": "unknown setting",
    }
    for number_, (line, expected) in enumerate(cases.items()):
        base = {"access/access.toml": f"[resources]\n{line}\n"}
        code, out, run = run_tool(tmp_path / str(number_), base)
        assert code == 1, (line, out)
        assert expected in out and "access.toml" in out or "unknown" in out, (line, out)
        assert not run.exists(), (line, list(run.iterdir()))
