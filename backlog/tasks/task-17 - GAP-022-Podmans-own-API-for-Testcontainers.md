---
id: TASK-17
title: 'GAP-022: Podman''s own API for Testcontainers'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
labels:
  - upstream
dependencies: []
ordinal: 17000
gaps:
  - GAP-022
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-022 (Testcontainers): Testcontainers assumes a Docker-compatible API. A spike confirmed that a test can start the system through podman's own API service, started for the session with `podman system service` on a Unix socket and `DOCKER_HOST` pointing at it, with no daemon and no host service, and that it leaves nothing behind. Two limits remain. A Unix socket path is limited to 108 bytes and podman rejects a relative socket URL, so the socket cannot live under a long `.cache/` path. Testcontainers also pulls its own reaper image, at a version it chooses.

Impact: The socket of the API service needs a short absolute path, and the reaper image is a container image that is not pinned by digest unless it is pinned or disabled.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The tests start the API service on a short absolute socket path, and the reaper image is pinned by digest in components.toml (tool images) or the reaper is disabled.
- [ ] #2 Check: GAP-022 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-17, GAP-022: Podman's own API for Testcontainers. Role: implementer.

### Read first

- `gaps.toml` entry GAP-022, and the skill of the component.

### Load these skills

- anima-tech-testcontainers-podman

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The tests start the API service on a short absolute socket path, and the reaper image is pinned by digest in components.toml (tool images) or the reaper is disabled.
- Check: GAP-022 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
