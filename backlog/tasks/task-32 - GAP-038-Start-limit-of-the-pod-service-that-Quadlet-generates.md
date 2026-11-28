---
id: TASK-32
title: 'GAP-038: Start limit of the pod service that Quadlet generates'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:42Z'
labels:
  - upstream
dependencies: []
ordinal: 32000
gaps:
  - GAP-038
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-038 (Quadlet): The pod service that Quadlet generates has Restart=on-failure with the default start limit, reaches the start limit within a second, and every container unit then fails with result 'dependency'.

Impact: The cause of a failing pod is hidden behind failures of every container unit; the first look at a container unit misleads.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: Quadlet's pod service does not reach its start limit within a second, or the engine's units set the limit explicitly and a test shows the cause is visible.
- [ ] #2 Check: GAP-038 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-32, GAP-038: Start limit of the pod service that Quadlet generates. Role: implementer.

### Read first

- `gaps.toml` entry GAP-038, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: Quadlet's pod service does not reach its start limit within a second, or the engine's units set the limit explicitly and a test shows the cause is visible.
- Check: GAP-038 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
