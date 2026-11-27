---
id: TASK-26
title: 'GAP-031: A read-only root filesystem together with podman secrets'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - gap
dependencies: []
ordinal: 26000
gaps:
  - GAP-031
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-031 (podman): A read-only root filesystem together with podman secrets failed.

Impact: A container that holds a secret cannot be given a read-only root filesystem as a hardening step.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The condition is gone, or the implementation of the engine image settles it.
- [ ] #2 Check: GAP-031 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-26, GAP-031: A read-only root filesystem together with podman secrets. Role: implementer.

### Read first

- `gaps.toml` entry GAP-031, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The condition is gone, or the implementation of the engine image settles it.
- Check: GAP-031 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
