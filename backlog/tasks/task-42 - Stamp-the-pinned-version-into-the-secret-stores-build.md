---
id: TASK-42
title: Stamp the pinned version into the secret store's build
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
updated_date: '2026-11-27T18:55:54Z'
labels:
  - engine
  - build
dependencies: []
ordinal: 42000
fork: none
role: implementer
gaps: []
owns:
  - engine/secrets/**
  - mise-tasks/engine/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The secret store built from source with the plain Go build reports a placeholder development version, not the version pinned in components.toml. A person or a check cannot confirm from the running system which release it is. This is a defect of our own build, not of something adopted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the secret store built into the engine image reports the version pinned in components.toml
<!-- AC:END -->

## Brief

Task: TASK-42, Stamp the pinned version into the secret store's build. Role: implementer.

### Read first

- `components.toml` (the pinned version) and the container file of the secret store.

### Load these skills

- anima-secrets-design, anima-tech-openbao, anima-tech-podman-quadlet-bootc

### Own these paths

- engine/secrets/**
- mise-tasks/engine/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the secret store built into the engine image reports the version pinned in components.toml

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
