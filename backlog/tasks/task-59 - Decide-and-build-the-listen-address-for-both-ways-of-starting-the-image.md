---
id: TASK-59
title: Decide and build the listen address for both ways of starting the image
status: To Do
assignee: []
created_date: '2026-11-27T18:18:46Z'
labels:
  - engine
dependencies: []
ordinal: 59000
gaps: []
fork: none
role: implementer
owns:
  - engine/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The listen-address installation parameter must hold when the image runs as a container (the outer publish restricts it) and when it is booted (the services themselves must bind to it). The units do not yet do the second, so a booted machine would expose the ports on every interface and R30 would not hold. This is the open design point of `anima-image-design`, rule 9.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a design is decided by the founder and written in ADR 0005 or its successor
- [ ] #2 Check: the services bind to the configured address when booted, shown by a test of the booted image
- [ ] #3 test_R30_nothing_reachable_by_default
<!-- AC:END -->

## Brief

Task: TASK-59, Decide and build the listen address for both ways of starting the image. Role: implementer.

### Read first

- ADR 0005, section 'One pod, loopback inside', and `anima-image-design`.

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-configuration-design

### Own these paths

- engine/**

### Do not touch

- third_party/**, generated files, lock files

### Acceptance

- Check: a design is decided by the founder and written in ADR 0005 or its successor
- Check: the services bind to the configured address when booted, shown by a test of the booted image
- test_R30_nothing_reachable_by_default

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
