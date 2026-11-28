---
id: TASK-26
title: 'GAP-031: A read-only root filesystem together with podman secrets'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
updated_date: '2026-11-27T19:35:30Z'
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
GAP-031 (podman): a read-only root filesystem together with podman secrets fails when the secrets directory is not a temporary filesystem; it works when /run/secrets is one (observed on 2026-11-27 with the configurator).

Impact: a container that holds a secret and has a read-only root filesystem needs a temporary filesystem on its secrets directory.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: GAP-031 is updated in gaps.toml (status, upstream link)
- [ ] #2 Check: podman creates the mount point of a secret on a read-only root without a temporary filesystem, or every unit of the engine that holds a secret carries that filesystem
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

- Check: GAP-031 is updated in gaps.toml (status, upstream link)
- Check: podman creates the mount point of a secret on a read-only root without a temporary filesystem, or every unit of the engine that holds a secret carries that filesystem

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
