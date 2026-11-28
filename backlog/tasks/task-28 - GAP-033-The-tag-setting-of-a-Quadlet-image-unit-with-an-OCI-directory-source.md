---
id: TASK-28
title: 'GAP-033: The tag setting of a Quadlet image unit with an OCI directory source'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - upstream
dependencies: []
ordinal: 28000
gaps:
  - GAP-033
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-033 (Quadlet): In an image unit the tag setting is ignored when the source is an OCI directory: the name is derived from the OCI reference.

Impact: A tag written in such a unit has no effect; the image is identified by its digest only, and the dependent unit tries to pull from https://localhost/ and fails when the reference does not carry the full final name.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The condition is gone, or the implementation of the engine image settles it.
- [ ] #2 Check: GAP-033 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-28, GAP-033: The tag setting of a Quadlet image unit with an OCI directory source. Role: implementer.

### Read first

- `gaps.toml` entry GAP-033, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The condition is gone, or the implementation of the engine image settles it.
- Check: GAP-033 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
