---
id: TASK-27
title: 'GAP-032: Static validation of invalid values in Quadlet'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - upstream
dependencies: []
ordinal: 27000
gaps:
  - GAP-032
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-032 (Quadlet): Quadlet's static validation does not catch an invalid value for some keys.

Impact: A unit with an invalid value passes the dry run and fails only when it is started (R52).

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The condition is gone, or the implementation of the engine image settles it.
- [ ] #2 Check: GAP-032 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-27, GAP-032: Static validation of invalid values in Quadlet. Role: implementer.

### Read first

- `gaps.toml` entry GAP-032, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The condition is gone, or the implementation of the engine image settles it.
- Check: GAP-032 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
