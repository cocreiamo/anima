---
id: TASK-31
title: 'GAP-037: Prefixed byte units in the SysML v2 standard library'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:42Z'
labels:
  - upstream
dependencies: []
ordinal: 31000
gaps:
  - GAP-037
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-037 (SysML v2 Pilot Implementation): The standard library has no prefixed byte units such as the megabyte.

Impact: A limit in megabytes needs a unit defined in the model.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The pilot implementation checks it. The model defines the unit with a conversion by prefix when it needs one; none is needed today.
- [ ] #2 Check: GAP-037 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-31, GAP-037: Prefixed byte units in the SysML v2 standard library. Role: implementer.

### Read first

- `gaps.toml` entry GAP-037, and the skill of the component.

### Load these skills

- anima-tech-sysml-pilot, anima-specifying-requirements

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The pilot implementation checks it. The model defines the unit with a conversion by prefix when it needs one; none is needed today.
- Check: GAP-037 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
