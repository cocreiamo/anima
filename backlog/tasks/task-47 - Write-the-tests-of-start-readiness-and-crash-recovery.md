---
id: TASK-47
title: Write the tests of start, readiness and crash recovery
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
updated_date: '2026-11-27T20:19:58Z'
labels:
  - pending-tests
dependencies: []
ordinal: 47000
gaps: []
fork: none
role: implementer
owns:
  - engine/image/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about an unattended start and a repeatable failed first start. The tests of serving only when converged (TASK-80), of a failing health check restarting its container, of recovery after an abrupt stop and of the readiness answer staying negative when the configurator fails are written or have their own task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R26_unattended_start
- [ ] #2 test_R36_failed_first_start_repeatable
<!-- AC:END -->

## Brief

Task: TASK-47, Write the tests of start, readiness and crash recovery. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-tech-testcontainers-podman, anima-specifying-requirements

### Own these paths

- engine/image/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R26_unattended_start
- test_R36_failed_first_start_repeatable

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
