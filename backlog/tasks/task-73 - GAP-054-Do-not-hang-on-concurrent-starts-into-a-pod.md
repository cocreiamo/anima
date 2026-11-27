---
id: TASK-73
title: 'GAP-054: Do not hang on concurrent starts into a pod'
status: To Do
assignee: []
created_date: '2026-11-27T20:19:46Z'
labels:
  - upstream
dependencies: []
ordinal: 73000
gaps:
  - GAP-054
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-054 (podman): concurrent starts of containers into one pod, with the cleanup of an exiting container, hung the nested podman.

Impact: the engine's containers cannot start at the same time.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: do not hang on concurrent starts into a pod is fixed upstream or settled by the engine
- [ ] #2 Check: GAP-054 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-73, GAP-054: Do not hang on concurrent starts into a pod. Role: implementer.

### Read first

- `gaps.toml` entry GAP-054.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the project is changed in its own repository, not here

### Acceptance

- Check: do not hang on concurrent starts into a pod is fixed upstream or settled by the engine
- Check: GAP-054 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
