---
id: TASK-43
title: 'GAP-050: Make the builds of the inner images reproducible'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - gap
  - engine
dependencies: []
ordinal: 43000
gaps:
  - GAP-050
fork: none
role: implementer
owns:
  - engine/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-050 (engine image): The builds of the inner images are not reproducible: the database server's image installs distribution packages at build time with no snapshot pin, and the identity provider's build downloads from the Java and JavaScript package registries.

Impact: The same pinned sources do not produce the same image bit for bit, so building again cannot check what was promoted (R47, `anima-branching-and-releasing` rule 6).

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: Distribution packages are taken from a dated snapshot and build-time downloads are pinned or vendored, and the verification of R47 passes.
- [ ] #2 Check: GAP-050 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-43, GAP-050: Make the builds of the inner images reproducible. Role: implementer.

### Read first

- `gaps.toml` entry GAP-050, and the skill of the component.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design, anima-branching-and-releasing

### Own these paths

- engine/**

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: Distribution packages are taken from a dated snapshot and build-time downloads are pinned or vendored, and the verification of R47 passes.
- Check: GAP-050 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
