---
id: TASK-33
title: 'GAP-039: Record the index digest on the offline import of an OCI directory'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:42Z'
labels:
  - upstream
dependencies: []
ordinal: 33000
gaps:
  - GAP-039
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-039 (podman): The offline import of an inner image from an OCI directory records the per-architecture digest, not the index digest.

Impact: The digest pinned in the lock is not the digest the engine stores; a check that compares them fails.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The import records the digest that was pinned, or the lock holds both digests and a test compares each with the right one.
- [ ] #2 Check: GAP-039 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-33, GAP-039: Record the index digest on the offline import of an OCI directory. Role: implementer.

### Read first

- `gaps.toml` entry GAP-039, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The import records the digest that was pinned, or the lock holds both digests and a test compares each with the right one.
- Check: GAP-039 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
