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
2. **Turnkey from day zero.** An adopter is never asked to install or manage an orchestrator (R50).
3. **The units are declared once in the image.** The start order and the readiness target are declared in the units (`After=`, `Requires=`, `BindsTo=`), and one target is the engine's readiness answer (R40, R41).
4. **A booted host upgrades atomically and rolls back; the data does not.** The operating system and the engine are replaced as a whole and can be returned to the previous version (R51). The volumes are not rolled back: data written since is kept and the previous version runs on it, which holds only because a version only expands (R43). Not: describing a rollback as undoing the data.
5. **The image carries its own init and container runtime.** Nothing is assumed of the host beyond what to boot, or a container engine that needs no daemon and no root (R29).
6. Unverified: **the engine image booted as an operating system.** Decided in ADR 0005 and not built; no disk image has been built from it, and the atomic upgrade and rollback of a booted host are not exercised (R50, R51).
7. Unverified: **the readiness target inside the container run.** The target was never reached in a spike because the health checks of the inner containers failed (GAP-034); the target is declared, not shown to work.

## Questions to answer before proposing

- Does the change work when the image is booted and when it is run as a container?
- Which units does it follow, and what does the readiness target wait for?
- Does a rollback of the operating system meet data that the previous version does not understand?
- Is the unit validated without starting it (R52)?

## Where the result goes

A decision amends ADR 0005. The units and the container file live in `engine/image/`; each capability's own units stay in its directory. The rule becomes a requirement and a test (`anima-specifying-requirements`); limits go to `gaps.toml`. Related skills: `anima-designing-for-production`, `anima-tech-podman-quadlet-bootc`.
