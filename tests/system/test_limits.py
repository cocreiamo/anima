"""The resource envelopes in a running engine (R207 to R210).

What each container's own control group says is read from the engine's outer
side, never from the declaration the test compares it with.
"""

import json
import re
import shutil
import tomllib

from conftest import ROOT
from engine_logic import envelope_faults, heap_faults

DECLARATION = tomllib.loads((ROOT / "engine/image/envelopes.toml").read_text())
DECLARED = {
    e["unit"]: {k: e[k] for k in ("memory_mib", "cpu_percent", "tasks")}
    for e in DECLARATION["envelope"]
}
# The infrastructure container of a pod is the pod's: the declaration names it.
EXEMPT = {f"{x['unit'].removesuffix('-pod')}-infra" for x in DECLARATION["exempt"]}


def limits_seen(engine) -> dict:
    """{container: {memory, cpu, pids}}: the three files of each running inner
    container's payload control group, read in the engine."""
    code, names = engine.exec("podman", "ps", "--format", "{{.Names}}")
    assert code == 0, names
    seen = {}
    for name in names.split():
        code, path = engine.exec(
            "podman", "inspect", "--format", "{{.State.CgroupPath}}", name
        )
        if code != 0:  # a container that ended between the listing and now
            continue
        found = {}
        for key, file in (
            ("memory", "memory.max"),
            ("cpu", "cpu.max"),
            ("pids", "pids.max"),
        ):
            code, text = engine.exec("cat", f"/sys/fs/cgroup{path.strip()}/{file}")
            assert code == 0, (name, file, text)
            found[key] = text
        seen[name] = found
    return seen


def test_R207_every_container_runs_within_its_declared_envelope(engine):
    """Every container the engine runs, discovered from the engine, carries the
    memory limit, processor bound and task limit of its declared envelope in its
    own control group; swap is not available to it; none is unbounded."""
    seen = limits_seen(engine)
    assert {"database", "access", "secrets", "entry", "database-tls"} <= set(seen)
    faults = envelope_faults(DECLARED, seen, EXEMPT)
    assert not faults, faults
    for name in ("access", "database", "secrets"):
        path = engine.exec(
            "podman", "inspect", "--format", "{{.State.CgroupPath}}", name
        )[1]
        swap = engine.exec("cat", f"/sys/fs/cgroup{path.strip()}/memory.swap.max")[1]
        assert swap.strip() == "0", (name, swap)


def test_R208_identity_provider_heap_follows_its_envelope(engine):
    """The identity provider's effective maximum heap, asked of its own runtime
    with the options of the running container, is within what the declared
    envelope allows, and not a share of the host's memory."""
    envelope = next(e for e in DECLARATION["envelope"] if e["unit"] == "access")
    code, out = engine.inner(
        "access",
        "sh",
        "-c",
        "java $JAVA_OPTS_KC_HEAP $JAVA_OPTS_APPEND -XX:+PrintFlagsFinal -version",
    )
    assert code == 0, out
    heap = int(re.search(r"MaxHeapSize\s*=\s*(\d+)", out).group(1))
    host = (
        int(
            re.search(
                r"MemTotal:\s*(\d+) kB", engine.exec("cat", "/proc/meminfo")[1]
            ).group(1)
        )
        * 1024
    )
    faults = heap_faults(heap, envelope["memory_mib"], envelope["heap_percent"], host)
    assert not faults, faults
    assert "UseSerialGC" in out and re.search(r"UseSerialGC\s*=\s*true", out)


def test_R209_service_over_its_envelope_is_stopped_and_restarted_alone(
    own_engine, tmp_path
):
    """The entry's envelope is shrunk, by a drop-in that only a test has, below what
    it needs. Its limit kills it (the barrier is the kernel's kill, logged by the
    init system, not a time), its unit starts it again, the engine says that it is
    not ready and names it and the reason, and no other container is started again."""
    (tmp_path / "10-test.conf").write_text(
        "[Service]\nEnvironmentFile=\nEnvironmentFile=/etc/anima-test-envelope.env\n"
    )
    (tmp_path / "envelope.env").write_text(
        "ANIMA_MEMORY=4m\nANIMA_CPUS=1.00\nANIMA_PIDS=128\n"
    )
    engine = own_engine(
        "r209",
        binds={
            str(
                tmp_path / "10-test.conf"
            ): "/etc/systemd/system/entry.service.d/10-test.conf",
            str(tmp_path / "envelope.env"): "/etc/anima-test-envelope.env",
        },
    )
    others = ("database", "access", "secrets", "database-tls")

    def killed_and_restarted() -> bool:
        journal = engine.exec("journalctl", "--no-pager", "--unit=entry.service")[1]
        restarts = engine.unit_property("entry.service", "NRestarts")
        return (
            "OOM killer killed" in journal and restarts.isdigit() and int(restarts) >= 1
        )

    try:
        engine.wait_for(
            "the entry killed by its limit and started again",
            killed_and_restarted,
            400,
            2,
        )
    except TimeoutError as error:
        journal = engine.exec(
            "journalctl", "--no-pager", "--unit=entry.service", "--lines=40"
        )[1]
        raise AssertionError(
            f"{error}\n{engine.not_ready_report()}\n{journal}"
        ) from error
    # The other containers: wait until they are all up, then see they are not restarted.
    engine.wait_for(
        "the others are up",
        lambda: all(engine.active(f"{u}.service") for u in others),
        400,
        2,
    )
    started = {u: engine.inner_container_started_at(u) for u in others}
    code, answer = engine.exec("/usr/libexec/anima/ready")
    assert code != 0 and "entry.service" in answer, answer
    assert "memory limit" in answer, answer
    assert not engine.active("anima-ready.target")
    assert all(engine.active(f"{u}.service") for u in others)
    assert started == {u: engine.inner_container_started_at(u) for u in others}


def test_R210_override_reaches_the_running_container(own_engine, tmp_path):
    """An override written in the configuration is the limit the container sees at
    start, the database server's own settings follow it, and the effective
    envelopes the engine shows say so."""
    config = tmp_path / "config"
    shutil.copytree(ROOT / "config", config)
    mail = config / "mail" / "mail.toml"
    mail.write_text(mail.read_text() + "\n[resources]\nmemory_mib = 160\n")
    (config / "database").mkdir()
    (config / "database" / "database.toml").write_text(
        "[resources]\nmemory_mib = 1024\n"
    )
    engine = own_engine("r210", binds={str(config): "/etc/anima/config"})
    # Not R9's limit: this test is about the limits, and a loaded machine is slow.
    engine.wait_ready(limit=480)
    seen = limits_seen(engine)
    assert seen["mail"]["memory"].strip() == str(160 * 1048576)
    assert seen["database"]["memory"].strip() == str(1024 * 1048576)
    assert seen["access"]["memory"].strip() == str(
        DECLARED["access"]["memory_mib"] * 1048576
    )
    shown = json.loads(engine.exec("cat", "/run/anima/config/envelopes.json")[1])
    assert (
        shown["mail"]["memory_mib"] == 160 and shown["database"]["memory_mib"] == 1024
    )
    code, out = engine.inner(
        "database",
        "psql",
        "--host=/run/postgresql",
        "--username=postgres",
        "--no-psqlrc",
        "--tuples-only",
        "--command=show shared_buffers",
    )
    assert code == 0 and out.strip() == "204MB", out
