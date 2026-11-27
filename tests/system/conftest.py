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


def pytest_collection_modifyitems(config, items):
    """System tests start the engine: run them only through `mise run engine:test`."""
    if os.environ.get("ANIMA_SYSTEM_TESTS") == "1":
        return
    skip = pytest.mark.skip(reason="system test: run `mise run engine:test`")
    for item in items:
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
        deadline = self.started_at + limit
        while time.monotonic() < deadline:
            if self.health() == "healthy":
                self.ready_after = time.monotonic() - self.started_at
                return self.ready_after
            time.sleep(2)
        raise TimeoutError(
            f"engine not ready within {limit} s (health: {self.health()})"
        )


def start_engine(name_suffix: str, publish_address: str = "127.0.0.1") -> Engine:
    from testcontainers.core.container import DockerContainer

    container = (
        DockerContainer(engine_image())
        .with_name(f"anima-system-test-{name_suffix}-{os.getpid()}")
        .with_kwargs(cap_add=["SYS_ADMIN", "SYS_PTRACE"])
        .with_bind_ports(5432, (publish_address, None))
        .with_bind_ports(8080, (publish_address, None))
    )
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
