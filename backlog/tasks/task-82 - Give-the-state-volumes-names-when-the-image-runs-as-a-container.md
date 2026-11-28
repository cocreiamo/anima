---
id: TASK-82
title: Give the state volumes names when the image runs as a container
status: To Do
assignee: []
created_date: '2026-11-27T20:19:48Z'
labels:
  - engine
dependencies: []
ordinal: 82000
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
When the image runs as a container its state volumes are anonymous, so removing the container loses the state (the database and the secret store's data). Name them in the run command and say in the design what survives a removal.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a removed and re-created engine container keeps its state when the same named volumes are given
- [ ] #2 Check: `anima-image-design` and ADR 0005 say what is a volume
<!-- AC:END -->

## Brief

Task: TASK-82, Give the state volumes names when the image runs as a container. Role: implementer.

### Read first

- `mise-tasks/engine/up`, `engine/image/anima-state.conf` and `anima-image-design`.

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/**
- mise-tasks/engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: a removed and re-created engine container keeps its state when the same named volumes are given
- Check: `anima-image-design` and ADR 0005 say what is a volume

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
