---
id: TASK-80
title: Hold the services back until convergence when the image runs as a container
status: To Do
assignee: []
created_date: '2026-11-27T20:19:47Z'
labels:
  - engine
dependencies: []
ordinal: 80000
gaps: []
fork: none
role: implementer
owns:
  - engine/**
  - mise-tasks/engine/**
  - tests/system/**
  - docs/adr/0005-engine-image-and-runtime.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Today, when the image runs as a container, only the readiness target and the access rules gate what is served; the services themselves start before the configurator has finished. R40 says nothing is published and no connection taken until every place that holds state has reached its declared state. Close the gap between the two, and keep R40 pending until its test passes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R40_serves_only_when_converged
- [ ] #2 Check: ADR 0005 states what gates what, and it agrees with the test
<!-- AC:END -->

## Brief

Task: TASK-80, Hold the services back until convergence when the image runs as a container. Role: implementer.

### Read first

- R40 in `model/anima.sysml` and ADR 0005, section Converge, then become ready.

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/**
- mise-tasks/engine/**
- tests/system/**
- docs/adr/0005-engine-image-and-runtime.md

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R40_serves_only_when_converged
- Check: ADR 0005 states what gates what, and it agrees with the test

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
