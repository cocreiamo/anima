---
id: TASK-17
title: 'GAP-022: Podman''s own API for Testcontainers'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
updated_date: '2026-11-27T18:55:56Z'
labels:
  - gap
  - testing
dependencies: []
ordinal: 17000
gaps:
  - GAP-022
fork: none
role: implementer
owns:
  - tests/system/**
  - components.toml
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-022 (Testcontainers): Testcontainers assumes a Docker-compatible API; the tests start podman's own API service on a short absolute socket, and the reaper image Testcontainers pulls is not pinned by digest.

The remedy is ours: the wiring of our system tests and the pin of the reaper image; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the tests start the API service on a short absolute socket path, and the reaper image is pinned by digest in components.toml (tool images) or the reaper is disabled
- [ ] #2 Check: GAP-022 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-17, GAP-022: Podman's own API for Testcontainers. Role: implementer.

### Read first

- `gaps.toml` entry GAP-022, and the skill of the component.

### Load these skills

- anima-tech-testcontainers-podman, anima-specifying-requirements

### Own these paths

- tests/system/**
- components.toml
- gaps.toml

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the tests start the API service on a short absolute socket path, and the reaper image is pinned by digest in components.toml (tool images) or the reaper is disabled
- Check: GAP-022 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
