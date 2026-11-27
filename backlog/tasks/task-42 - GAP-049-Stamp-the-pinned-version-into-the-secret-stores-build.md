---
id: TASK-42
title: 'GAP-049: Stamp the pinned version into the secret store''s build'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - gap
  - engine
dependencies: []
ordinal: 42000
gaps:
  - GAP-049
fork: none
role: implementer
owns:
  - engine/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-049 (openbao): The secret store built from source with the plain Go build reports a placeholder development version, not the version of the component pinned in components.toml.

Impact: The version a running secret store reports differs from the pinned one, so a person or a check cannot confirm from the running system which release it is.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The build of the secret store's image stamps the pinned version, or upstream's own build is used for the image.
- [ ] #2 Check: GAP-049 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-42, GAP-049: Stamp the pinned version into the secret store's build. Role: implementer.

### Read first

- `gaps.toml` entry GAP-049, and the skill of the component.

### Load these skills

- anima-secrets-design, anima-tech-openbao

### Own these paths

- engine/**

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The build of the secret store's image stamps the pinned version, or upstream's own build is used for the image.
- Check: GAP-049 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
