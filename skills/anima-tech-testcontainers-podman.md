---
name: anima-tech-testcontainers-podman
description: "Use when writing or debugging a system test in Anima that starts containers with Testcontainers for Python on rootless podman: the API service, DOCKER_HOST, the reaper image, the socket path limit, cleanup."
family: technology
paths:
  - tests/system/**
---

# Testcontainers on rootless podman

How Testcontainers for Python behaves against rootless podman with no Docker
daemon. The test layout is in `anima-specifying-requirements`.

## Use this when

- Writing or changing a test that starts the system or a part of it in a container.
- Wiring the session that starts podman's API service for those tests.
- Debugging a "cannot connect to the Docker daemon" or a socket error.

## Rules

1. **Start podman's own API service for the session, on a short absolute socket.** Example: `tests/system/conftest.py` starts `podman system service` on a socket named by the process id under `$XDG_RUNTIME_DIR`. Observed on 2026-11-27 with Testcontainers 4.15.0 and rootless podman 4.9.3: the test started a container, read from it, and nothing was left behind. Not: a long path; an AF_UNIX path is limited to 108 bytes and podman rejects a relative `unix://` URL, so not under a long `.cache/` path (GAP-022).
2. **Point Testcontainers at it with `DOCKER_HOST=unix://<that socket>`, and wait for the socket (`[ -S "$SOCK" ]`) before starting the tests.** Not: expecting a daemon to exist; none does.
3. **Stop the service and delete the socket afterwards, in a trap.** Example: `trap 'kill $SVC; wait $SVC; rm -f "$SOCK"' EXIT`.
4. **With the reaper, run it privileged and give it the socket; without it, disable it.** Example: `TESTCONTAINERS_RYUK_PRIVILEGED=true` and `TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=<that socket>`; or `TESTCONTAINERS_RYUK_DISABLED=true`. Not: expecting the reaper to reach the socket unprivileged; rootless podman needed it privileged because it mounts the socket.
5. **Pin the reaper image by digest or disable it.** Not: expecting the reaper image to be fixed; Testcontainers pulls it at a version it chooses (GAP-022).
6. **Write the test with the ordinary API.** Example: `DockerContainer(image).with_exposed_ports(…).waiting_for(HttpWaitStrategy(…))`; it needs no podman-specific code.
7. Unverified: behaviour on a CI runner other than the machine of the spike; containers that need more privileges than the spike's (an engine image run as a container needs both `--cap-add SYS_ADMIN` and `--cap-add SYS_PTRACE`, see `anima-tech-podman-quadlet-bootc`); what the reaper cleans up after a test that fails midway (the spike's test passed).

## Questions to answer before proposing

- Is the socket path short and absolute, and is the service stopped afterwards?
- Is the reaper pinned by digest or disabled?
- Does the test need privileges the spike did not use?
- What did you run on this machine, and what on a CI runner?

## Where the result goes

The test layout is in `anima-specifying-requirements`; the tests go to `tests/system/` (`anima-repository-conventions`, ADR 0005). Limits go to `gaps.toml` (GAP-022). Related skills: `anima-specifying-requirements`, `anima-tech-podman-quadlet-bootc`, `anima-adopting-a-component`.
