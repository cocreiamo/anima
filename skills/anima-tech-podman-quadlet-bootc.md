---
name: anima-tech-podman-quadlet-bootc
description: "Use when writing, building, validating or running the engine image in Anima with podman, Quadlet units and a bootc base: rootless builds, shipping inner images, running the image as a container, start order and readiness gating, static validation of units, health checks."
family: technology
paths:
  - engine/image/**
  - engine/**/*.container
  - engine/**/*.image
  - engine/**/*.pod
  - engine/**/Containerfile
  - mise-tasks/engine/**
---

# podman, Quadlet and bootc: the engine image

How the engine image, an image-based operating system with systemd and Quadlet
units that also runs as a container, behaves when built and run. The design is
ADR 0005; the product's rules are in `anima-designing-for-production`.

## Use this when

- Writing a `.container`, `.pod` or `.image` unit, or an engine `Containerfile`.
- Shipping the inner images (database server, identity provider, secret store).
- Running the engine image as a container in a test.
- Validating units without starting them.
- Deciding how readiness and start order are expressed.

## Rules

1. **Build rootless in the Docker image format.** Example: `podman build --format docker -t <name> -f <Containerfile> <dir>`; `bootc container lint` as a `RUN` passes inside the build. Observed on 2026-11-27 with rootless podman 4.9.3 on the host and a Fedora bootc base shipping podman 6.2.0 and systemd 262.1. Example: `mise-tasks/engine/image`. Not: the OCI format, which prints "HEALTHCHECK is not supported for OCI image format and will be ignored".
2. **Ship inner images as an OCI directory copied by digest.** Example: in a build stage `skopeo copy --preserve-digests docker://…@sha256:… oci:/out/images:<full final name>`, then `COPY --from=… /out/images /usr/lib/anima/images`; at first start a Quadlet image unit imports it offline with `Image=oci:/usr/lib/anima/images:<full final name>`. The images are on disk twice afterwards. Not: baking an image store into a rootless build; overlay whiteouts are character devices ("cannot create special file … Operation not permitted"), and `--cap-add SYS_ADMIN` and `--isolation chroot` did not help (GAP-025).
3. **Give the OCI reference the full final name.** Not: relying on `ImageTag=`; with an `oci:` source it is ignored and the name comes from the OCI reference, so the dependent unit tries to pull from `https://localhost/` and fails (GAP-033).
4. **Keep both digests in the lock.** Not: assuming the pinned digest is what is stored; the import records the per-architecture digest, not the index digest (GAP-039).
5. **Run the engine image as a container with two added capabilities, a volume for the inner storage and the published ports on the loopback.** Example: `podman run -d --cap-add SYS_ADMIN --cap-add SYS_PTRACE -v <volume>:/var/lib/containers -p 127.0.0.1:<port>:<port> <image>`; systemd as first process needs no other flag (the base's `CMD` is `/sbin/init`; add `STOPSIGNAL SIGRTMIN+3`). `SYS_ADMIN` is for the nested mounts. `SYS_PTRACE` is because the inner container runtime opens the namespace files of the target process (`/proc/<pid>/ns/mnt`) when it executes a command in an inner container, a check that needs the capability; a health check is such a command. No full privilege is needed (observed on 2026-11-27: with both, a container became healthy through its declared checks). Not: starting with no flags; without `SYS_ADMIN` the inner pod fails ("mount `proc` to `proc`: Operation not permitted") and the import fails ("lchown /etc/gshadow: invalid argument"); the inner storage on the outer overlay fails too. Not: `SYS_ADMIN` alone; every `podman exec` into an inner container then fails ("Failed to read pidfile"; the runtime's own log says "openat /proc/<pid>/ns/mnt: Permission denied") and so does every health check (GAP-034).
6. **Mask the units that fail harmlessly in a container.** Not: expecting a clean boot; `bootloader-update`, `polkit`, `systemd-oomd`, `systemd-resolved` and `var-lib-nfs-rpc_pipefs.mount` fail. Unverified: they are not yet masked in the image, so a container run of it still reports them failed (GAP-048).
7. **Express readiness by gating.** With `Notify=healthy` a container unit stays activating until it is healthy, and units ordered after it (`Requires=`, `After=`) stay inactive; a target that `BindsTo=` all of them and is `After=` them stays inactive until then, and a published port refuses connections until then. Keys used: `HealthStartupCmd`, `HealthStartupInterval`, `HealthStartupRetries`, `HealthCmd`, `HealthInterval`, `HealthRetries`, `HealthOnFailure=kill`, `Notify=healthy`; podman wires them as transient systemd timers. Not: health checks without systemd, which are scheduled by systemd timers, so with no systemd no check ever runs; `podman kube play` ignores readiness probes and removes a volume claim when it tears down (GAP-019, closed).
8. **Validate units statically inside a container of the image, with no network.** Example: set `QUADLET_UNIT_DIRS=<dir>`; run `/usr/lib/systemd/system-generators/podman-system-generator --dryrun`; run the generator into a directory (`… /tmp/gen /tmp/gen /tmp/gen`); then `systemd-analyze verify /tmp/gen/<unit>.service` on each unit (`mise-tasks/engine/units-check`). It catches an unknown key ("unsupported key"), "Failed to parse Restart=sometimes" and "Unit missing.service not found". Not: expecting a bad value to be caught; `HealthOnFailure=explode` passes both tools (GAP-032), and `systemd-analyze --generators=true verify` prints "No configuration found." and checks nothing.
9. **Read the pod service's journal first when a pod fails.** Not: expecting the container units to show the cause; the generated pod service has `Restart=on-failure` with the default start limit, reaches "start-limit-hit" within a second, and every container unit then fails with result 'dependency' (GAP-038).
10. **Health checks do what the units promise in the nested container, with the two capabilities of rule 5.** Observed on 2026-11-27 by the system tests (`mise run engine:test`, skipped by `check`): a container became healthy through its declared checks, the readiness target `anima-ready.target` was reached (R41), a failing check restarted its container (`HealthOnFailure=kill` with `Restart=always`, R97), and the target stayed inactive when the configurator failed (R98, run alone). Example: `tests/system/test_engine.py`. Not: the earlier finding that checks never passed; that was the missing second capability (GAP-034, closed).
11. **Bring the readiness target back with an upholding drop-in.** `BindsTo=` stops the target when a part leaves the active state, and nothing starts it again when the part is back. Example: `engine/image/anima-ready-upheld.conf` is a drop-in of `multi-user.target` with `Upholds=anima-ready.target`, and the parts have `StartLimitIntervalSec=0`. Not: a target that stays down after a restarted part.
12. **Order the starts of the containers of a pod, and let a run-to-completion unit retry.** Observed on 2026-11-27: concurrent `podman run` into one pod together with the cleanup of an exiting container hung the nested podman (a futex wait). Example: `engine/access/access.container` lists every other unit in `After=` so that the identity provider starts last, and `engine/database/database-prepare.container` has `Restart=on-failure`.
13. **Wait for health by reading the health state.** Observed on 2026-11-27 with podman 4.9.3 on the host: `podman wait --condition=healthy` returned at once with -1. Example: `mise-tasks/engine/wait` polls `podman inspect --format '{{.State.Health.Status}}'`. Not: `podman wait --condition=healthy` on that version.
14. **Do not set a hostname in the host's UTS namespace and do not use a relative or long socket path.** A Unix socket path is limited to 108 bytes and podman rejects a relative socket URL. A hostname cannot be set in the host's namespace.
15. **Allow time for a stop.** Observed on 2026-11-27: `podman stop -t 60` of the engine took 41 s with a clean database shutdown. Not: a short stop timeout.
16. **A pod stops when a run-to-completion container ends first, unless its exit policy is set to continue.** Example: `ExitPolicy=continue` in the `.pod` unit. Not: the default, which the generated pod uses (`--exit-policy stop`): when the configurator or the database initialisation exits and no other container runs yet, the pod stops and every unit of it cascades down; the configurator "unit that runs to completion" depends on this setting.
17. **Do not give `Tmpfs=` a user id.** Example: `Mount=type=tmpfs,destination=<dir>,tmpfs-mode=1777` (a unit under `engine/`). Not: `Tmpfs=<dir>:uid=1000`; the container runtime rejects it ("unknown mount option uid").
18. **A build must depend on the files it copies, not only on its container file.** Example: the sources of the build task list every file that a `COPY` takes (the units, the configuration, the scripts). Not: a task up to date because only the container file is unchanged; a changed configuration then stays out of the image and the old one stays inside (PM-005, R99).
19. **Observe the state after a command that waits on the container runtime; do not trust its exit code, and read a build's verdict from what it keeps.** Observed on 2026-11-28 (PM-008): `podman kill` answered 125 ("timed out waiting for file .../exits/<id>") and the removal of a container answered 500 ("given PID did not die within timeout") under heavy load; whether the container was stopped is a separate fact, read with `podman inspect --format '{{json .State}}'`. A build with every layer cached does not run a step again and prints nothing of it, and a pipe to `tee | tail` in a `RUN` hides the exit status of the command before it. Example: `Engine.kill` in `tests/system/conftest.py`; `mise-tasks/engine/regress` reads `/tmp/regress.log` out of the built image. Not: asserting the exit code of `kill`, `stop` or `start`; grepping the build output for a test result.
20. Unverified: `bootc-image-builder`, a read-only root (it failed together with podman secrets, GAP-031), a TPM or `systemd-creds`, and a rootless inner podman under `systemctl --user`. Logically bound images work only on a booted host with root podman (read in the documentation, not run).

## Questions to answer before proposing

- Which unit orders after which, and what does each health setting check?
- Does the unit work when the image runs as a container and when it is booted?
- Is the image reference pinned by digest, and is the stored digest the one pinned?
- What did you run in a container of the image, and what did you only read?
- Which of the open gaps above does the unit meet?

## Where the result goes

Units and the container file go to `engine/image/` and `engine/<capability>/`. The decision amends ADR 0005 (and `anima-repository-conventions` for the toolchain). Limits go to `gaps.toml` (GAP-025, GAP-031 to GAP-034, GAP-038, GAP-039). Related skills: `anima-image-design`, `anima-designing-for-production`, `anima-tech-testcontainers-podman`.
