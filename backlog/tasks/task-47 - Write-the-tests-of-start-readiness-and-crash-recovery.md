---
id: TASK-47
title: Write the tests of start, readiness and crash recovery
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
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
The verifications about an unattended start, a repeatable failed first start, serving only when converged, recovery after an abrupt stop with the same start, a failing health check restarting its container, and the readiness answer staying negative when the configurator fails. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R26_unattended_start
- [ ] #2 test_R36_failed_first_start_repeatable
- [ ] #3 test_R40_serves_only_when_converged
- [ ] #4 test_R42_abrupt_stop_recovers_with_same_start
- [ ] #5 test_R97_failing_health_check_restarts_container
- [ ] #6 test_R98_readiness_negative_when_configurator_fails
<!-- AC:END -->

## Brief

Task: TASK-47, Write the tests of start, readiness and crash recovery. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-tech-testcontainers-podman

### Own these paths

- engine/image/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R26_unattended_start
- test_R36_failed_first_start_repeatable
- test_R40_serves_only_when_converged
- test_R42_abrupt_stop_recovers_with_same_start
- test_R97_failing_health_check_restarts_container
- test_R98_readiness_negative_when_configurator_fails

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
