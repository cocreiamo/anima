---
name: anima-image-design
description: "Use when changing the engine image: its container file, its Quadlet units, its start order and readiness target, how it is booted or run as a container, or anything under engine/image/."
family: capability
paths:
  - engine/image/**
---

# Engine image design

The capability `image` (directory `engine/image/`): the engine delivered as one
image-based operating system with two ways to start it. The decisions are
taken; their home is ADR 0005. How podman, Quadlet and bootc behave is
`anima-tech-podman-quadlet-bootc`.

## Use this when

- Changing the engine's container file or the units that start the parts.
- Changing the start order or the readiness target.
- Deciding how the image is booted or run as a container.
- Touching anything under `engine/image/`.

## Rules

1. **One image, two ways to start it.** The engine image is an image-based operating system on a Fedora bootc base: boot it as the operating system of a machine (disk images from `bootc-image-builder`), or run it as a container. Not: a second image or a second declaration of the containers for one of the two ways.
2. **Turnkey from day zero.** An adopter is never asked to install or manage an orchestrator (R29).
3. **The units are declared once in the image.** The start order and the readiness target are declared in the units (`After=`, `Requires=`, `BindsTo=`), and one target is the engine's readiness answer (R40, R41).
4. **A booted host upgrades atomically and rolls back; the data does not.** The operating system and the engine are replaced as a whole and can be returned to the previous version (R51). The volumes are not rolled back: data written since is kept and the previous version runs on it, which holds only because a version only expands (R43). Not: describing a rollback as undoing the data.
5. **The image carries its own init and container runtime.** Nothing is assumed of the host beyond what to boot, or a container engine that needs no daemon and no root (R29).
6. Unverified: **the engine image booted as an operating system.** Decided in ADR 0005 and not built; no disk image has been built from it, and the atomic upgrade and rollback of a booted host are not exercised (R50, R51).
7. **The root of trust lives in its own declared volume,** apart from the database server's data and from the backups, so that a restore elsewhere needs the same root of trust and a backup never carries it (R20). Not: the root of trust inside the state volume, or in a backup.
8. **The readiness target holds in the container run.** Observed on 2026-11-27 by the system tests (R41, R97, R98; `anima-tech-podman-quadlet-bootc`): the target is reached, a failing check restarts its container, and the target stays unreached when the configurator fails. Not claimed: that the services are held back until convergence when the image runs as a container; today only the readiness target and the access rules gate (R40 stays pending, with a task).
9. **The listen address follows the way of starting, for the database server and the HTTP entry point; the identity provider never follows it.** Run as a container, the database server and the entry listen on every address of the container and the outer publish restricts it; booted, a unit binds them to the configured address; the identity provider listens on the pod's loopback in both ways (ADR 0008, R135) (`engine/image/anima-listen`, `anima-listen-container.service`, `anima-listen-host.service`, R30). Observed on 2026-11-27 for the container way and for the script and the condition of the booted way; Unverified: that the booted way works on a booted machine.
10. Unverified: **state volumes are anonymous when the image runs as a container.** Removing the container loses the state (the database, the secret store's data); a named volume is not yet declared. There is a task for it in the backlog.
11. Unverified: **services are held back until convergence when the image runs as a container.** Today the readiness target and the access rules gate; R40 is pending and has a task.

12. **The readiness answer says why it is negative.** The engine's health check is `engine/image/anima-ready`: it succeeds when the target is active and otherwise prints each part that is not, with its state and its own last lines, so that a failed certificate renewal reads "certificate renewal failed" where readiness is reported (R119). Observed on 2026-11-28. Not: a health check that only exits non-zero.

13. **A compile stage runs with the network off, on a dependencies image fetched once per fork commit.** Decided 2026-11-28 (class: a build that depends on inputs the repository does not hold, TASK-43, R178, R179). A converted container file has a stage `fetch` (the only one with the network: `go mod download` and `go mod verify`, nothing else, against the `go.sum` the fork carries, `-mod=readonly`, `GOTOOLCHAIN=local`), a stage `dependencies` (`FROM scratch`, the module cache alone) and compile stages whose every `RUN` is `--network=none` with `GOPROXY=off`, modules copied from `dependencies`. `mise run engine:build` builds `dependencies` as an image of its own (`localhost/anima/<name>-dependencies:<tag>`, tag from the fork's commit, its lock files and the container file) and passes it as `--build-context dependencies=container-image://<ref>`, which replaces the stage of the same name; the system tests' image cache holds it. A missing module fails the stage at once and the error names it. Ladder of TASK-43: a converted component's compile stage is at L2 (its base images and runtime packages are still fetched: GAP-060, TASK-96). Example: `engine/secrets/Containerfile`. Not: a compile stage that downloads, `-mod=mod`, `GONOSUMDB`, `GOTOOLCHAIN=auto`, or retries as the remedy.
14. **Every unit of the image has an envelope.** A container unit has `EnvironmentFile=/run/anima/config/envelope/<unit>.env` in `[Container]` and `[Service]` and one `PodmanArgs` line with `--memory`, `--memory-swap` (equal, so that swap is no way round the limit), `--cpus` and `--pids-limit` from it, and requires `anima-config.service` (without the file the unit does not start: absence is failure, not unbounded); a service or image unit of the host side carries `MemoryMax`, `CPUQuota` and `TasksMax` of its class. Observed on 2026-11-28: `MemoryMax` on a service does not reach the container's own cgroup, so the runtime inside does not see it, while `--memory` does; Quadlet has no key that takes a variable, hence `PodmanArgs`. The pod's infrastructure container is the one named exemption. Example: `engine/access/access.container`.

## Questions to answer before proposing

- Does the change work when the image is booted and when it is run as a container?
- Which units does it follow, and what does the readiness target wait for?
- Does a rollback of the operating system meet data that the previous version does not understand?
- Is the unit validated without starting it (R52)?

## Where the result goes

A decision amends ADR 0005. The units and the container file live in `engine/image/`; each capability's own units stay in its directory. The rule becomes a requirement and a test (`anima-specifying-requirements`); limits go to `gaps.toml`. Related skills: `anima-designing-for-production`, `anima-tech-podman-quadlet-bootc`.
