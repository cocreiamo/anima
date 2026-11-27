---
id: TASK-41
title: 'GAP-048: Mask the base-image units that fail harmlessly in a container'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - gap
  - engine
dependencies: []
ordinal: 41000
gaps:
  - GAP-048
fork: none
role: implementer
owns:
  - engine/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-048 (bootc): The units that the base image ships and that fail harmlessly in a container (the bootloader update, the policy kit, the out-of-memory daemon, the resolver and one mount of the network file system) are not yet masked in the engine image, so a container run of it reports failed units.

Impact: A run as a container is not clean: a reader or a check that looks at failed units sees noise, and a real failure is harder to see.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The engine image masks them, and a container run of it reports no failed unit that is not a real fault.
- [ ] #2 Check: GAP-048 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-41, GAP-048: Mask the base-image units that fail harmlessly in a container. Role: implementer.

### Read first

- `gaps.toml` entry GAP-048, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- engine/**

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The engine image masks them, and a container run of it reports no failed unit that is not a real fault.
- Check: GAP-048 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
