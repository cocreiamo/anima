"""Fixtures of the system tests: the engine image started once per session.

Testcontainers talks to podman's own API service, started for this session on a
socket with a short path (AF_UNIX paths are limited to 108 bytes). No Docker
daemon and no host service is assumed.

The Testcontainers reaper (Ryuk) is DISABLED: it needs the API socket mounted
into a privileged container, and rootless podman refuses that without
privileges. The fixture removes what it started in a `finally` instead; a
session killed with SIGKILL can leave the engine container behind (its name
starts with `anima-system-test-`).
"""

import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache" / "engine"

# R9: ready within this many seconds of starting. One constant, read by every test.
READY_LIMIT_SECONDS = 180


OFFLINE_MODULES = {"test_inputs.py"}


def pytest_collection_modifyitems(config, items):
    """System tests start the engine: run them only through `mise run engine:test`."""
    if os.environ.get("ANIMA_SYSTEM_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="system test: run `mise run engine:test`")
    for item in items:
        # Modules listed here start no container and run in every `pytest` run.
        if Path(str(item.fspath)).name in OFFLINE_MODULES:
            continue
        if "tests/system" in str(item.fspath).replace("\\", "/"):
            item.add_marker(skip)


@pytest.fixture(scope="session")
def podman_service():
    """podman's API service for the session, and DOCKER_HOST pointing at it."""
    runtime = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
    sock = Path(runtime) / f"anima-tc-{os.getpid()}.sock"
    sock.unlink(missing_ok=True)
    service = subprocess.Popen(
        ["podman", "system", "service", "--time=0", f"unix://{sock}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(100):
        if sock.exists():
            break
        time.sleep(0.1)
    else:
        service.kill()
        raise RuntimeError("podman system service did not create its socket")
    os.environ["DOCKER_HOST"] = f"unix://{sock}"
    os.environ["TESTCONTAINERS_RYUK_DISABLED"] = "true"
    try:
        yield f"unix://{sock}"
    finally:
        service.terminate()
        service.wait(timeout=20)
        sock.unlink(missing_ok=True)


def engine_image() -> str:
    ref = CACHE / "engine.ref"
    if not ref.exists():
        pytest.fail("no engine image: run `mise run engine:image`")
    return ref.read_text().strip()


class Engine:
    """A started engine container, as the tests see it."""

    def __init__(self, container, started_at: float):
        self.container = container
        self.started_at = started_at
        self.ready_after: float | None = None

    @property
    def name(self) -> str:
        return self.container.get_wrapped_container().name

    def exec(self, *command: str, user: str | None = None) -> tuple[int, str]:
        """Run a command in the engine container (outer)."""
        args = ["podman", "exec"]
        if user:
            args += ["--user", user]
        result = subprocess.run(
            [*args, self.name, *command], capture_output=True, text=True, check=False
        )
        return result.returncode, result.stdout + result.stderr

    def inner(self, container: str, *command: str) -> tuple[int, str]:
        """Run a command inside a container of the engine's pod."""
        return self.exec("podman", "exec", container, *command)

    def health(self) -> str:
        code, out = self.exec_host(
            "podman", "inspect", "--format", "{{.State.Health.Status}}", self.name
        )
        return out.strip() if code == 0 else "unknown"

    @staticmethod
    def exec_host(*command: str) -> tuple[int, str]:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout + result.stderr

    def wait_ready(self, limit: float = READY_LIMIT_SECONDS) -> float:
        """Wait for the engine's own health check (the readiness answer)."""
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            if self.health() == "healthy":
                self.ready_after = time.monotonic() - self.started_at
                return self.ready_after
            time.sleep(2)
        raise TimeoutError(
            f"engine not ready within {limit} s (health: {self.health()})"
        )

    def wait_for(self, what: str, check, limit: float = 90.0, every: float = 1.0):
        """Poll `check()` (returns a truthy value) until it holds or `limit` passes."""
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            value = check()
            if value:
                return value
            time.sleep(every)
        raise TimeoutError(f"{what}: not true within {limit} s")

    def active(self, unit: str) -> bool:
        return self.exec("systemctl", "is-active", "--quiet", unit)[0] == 0

    def unit_property(self, unit: str, prop: str) -> str:
        out = self.exec("systemctl", "show", unit, f"--property={prop}", "--value")[1]
        return out.strip()

    def inner_container_started_at(self, name: str) -> str:
        code, out = self.exec(
            "podman", "inspect", "--format", "{{.State.StartedAt}}", name
        )
        return out.strip() if code == 0 else ""

    def kill(self) -> None:
        """An abrupt stop: SIGKILL to the engine's first process and everything in it."""
        code, out = self.exec_host("podman", "kill", self.name)
        assert code == 0, out

    def start_again(self) -> None:
        """The same start command after an abrupt stop: start the same container."""
        code, out = self.exec_host("podman", "start", self.name)
        assert code == 0, out
        self.started_at = time.monotonic()
        self.ready_after = None

    def logs(self) -> str:
        return self.exec_host("podman", "logs", "--tail", "40", self.name)[1]


def start_engine(
    name_suffix: str,
    publish_address: str = "127.0.0.1",
    binds: dict[str, str] | None = None,
    env: dict[str, str] | None = None,
) -> Engine:
    """Start the engine image as the documented `podman run` line does.

    `binds` maps a host path to a path in the engine container (read only): the
    tests use it to put a systemd drop-in over one unit of a second engine.
    """
    from testcontainers.core.container import DockerContainer

    container = (
        DockerContainer(engine_image())
        .with_name(f"anima-system-test-{name_suffix}-{os.getpid()}")
        .with_kwargs(cap_add=["SYS_ADMIN", "SYS_PTRACE"])
    )
    # Testcontainers types a published port as `int`; the API takes (address, port).
    container.ports["5432"] = (publish_address, None)  # type: ignore[assignment]
    container.ports["8080"] = (publish_address, None)  # type: ignore[assignment]
    # The example configuration of the repository with its local profile: the
    # configurator needs the adopter's identities, and the local profile selects
    # the stand-ins.
    binds = dict(binds or {})
    if "/etc/anima/config" not in binds.values():
        binds[str(ROOT / "config")] = "/etc/anima/config"
    env = {"ANIMA_PROFILE": "local", **(env or {})}
    container.with_envs(**env)
    for host, inside in binds.items():
        container.with_volume_mapping(host, inside, "ro")
    started = time.monotonic()
    container.start()
    return Engine(container, started)


@pytest.fixture(scope="session")
def engine(podman_service):
    """The engine, started once and ready (R9 and R41 are tested on it)."""
    if shutil.which("podman") is None:
        pytest.fail("podman is required")
    running = start_engine("main")
    try:
        running.wait_ready()
        yield running
    finally:
        running.container.stop()


@pytest.fixture
def own_engine(podman_service, request):
    """A factory of engines that one test breaks on purpose; each is removed with
    its volumes at the end of the test."""
    started: list[Engine] = []

    def make(
        suffix: str,
        binds: dict[str, str] | None = None,
        env: dict[str, str] | None = None,
    ) -> Engine:
        running = start_engine(f"{suffix}", binds=binds, env=env)
        started.append(running)
        return running

    yield make
    for running in started:
        running.container.stop()
