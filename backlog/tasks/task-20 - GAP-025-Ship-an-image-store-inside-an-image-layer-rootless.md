---
id: TASK-20
title: 'GAP-025: Ship an image store inside an image layer, rootless'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
labels:
  - upstream
dependencies: []
ordinal: 20000
gaps:
  - GAP-025
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-025 (podman): A container-storage image store cannot be shipped inside an image layer, because of the overlay whiteout devices it contains. Inner images can only be shipped as an archive loaded at first start.

Impact: The engine image cannot carry its inner images ready to run: shipping them as an archive costs image size and start time (ADR 0005, R9).

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The spike for the bootc design settles how the engine image carries its inner images, and the cost is measured against the start time of R9.
- [ ] #2 Check: GAP-025 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-20, GAP-025: Ship an image store inside an image layer, rootless. Role: implementer.

### Read first

- `gaps.toml` entry GAP-025, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The spike for the bootc design settles how the engine image carries its inner images, and the cost is measured against the start time of R9.
- Check: GAP-025 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
