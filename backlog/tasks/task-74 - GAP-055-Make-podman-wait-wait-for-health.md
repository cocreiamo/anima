---
id: TASK-74
title: 'GAP-055: Make podman wait wait for health'
status: To Do
assignee: []
created_date: '2026-11-27T20:19:46Z'
labels:
  - upstream
dependencies: []
ordinal: 74000
gaps:
  - GAP-055
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-055 (podman): `podman wait --condition=healthy` returns at once with -1 on the host's version.

Impact: a script that waits with it goes on at once.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: make podman wait wait for health is fixed upstream or settled by the engine
- [ ] #2 Check: GAP-055 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-74, GAP-055: Make podman wait wait for health. Role: implementer.

### Read first

- `gaps.toml` entry GAP-055.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the project is changed in its own repository, not here

### Acceptance

- Check: make podman wait wait for health is fixed upstream or settled by the engine
- Check: GAP-055 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
