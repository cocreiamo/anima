---
id: TASK-79
title: Prove the engine on a booted machine
status: To Do
assignee: []
created_date: '2026-11-27T20:19:47Z'
labels:
  - engine
dependencies: []
ordinal: 79000
gaps: []
fork: none
role: implementer
owns:
  - engine/**
  - mise-tasks/engine/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Everything seen working ran with the engine image as a container. Boot a disk image built from it, and show the start, the readiness, the listen address of the booted way, the atomic upgrade and the rollback.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R50_engine_image_boots_as_operating_system
- [ ] #2 test_R51_booted_upgrade_atomic_and_reversible
- [ ] #3 Check: the booted way binds the services to the configured address (R30)
<!-- AC:END -->

## Brief

Task: TASK-79, Prove the engine on a booted machine. Role: implementer.

### Read first

- ADR 0005 and `anima-image-design`.

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/**
- mise-tasks/engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R50_engine_image_boots_as_operating_system
- test_R51_booted_upgrade_atomic_and_reversible
- Check: the booted way binds the services to the configured address (R30)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
