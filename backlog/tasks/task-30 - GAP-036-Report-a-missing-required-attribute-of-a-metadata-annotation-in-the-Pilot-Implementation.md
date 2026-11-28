---
id: TASK-30
title: >-
  GAP-036: Report a missing required attribute of a metadata annotation in the
  Pilot Implementation
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - upstream
dependencies: []
ordinal: 30000
gaps:
  - GAP-036
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-036 (SysML v2 Pilot Implementation): The Pilot Implementation does not report a missing required attribute of a metadata annotation: a fitness-function marker without a trigger validates.

Impact: A marker without a trigger passes the model check.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The pilot implementation checks it. A test fails on a marker that has no valid trigger.
- [ ] #2 Check: GAP-036 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-30, GAP-036: Report a missing required attribute of a metadata annotation in the Pilot Implementation. Role: implementer.

### Read first

- `gaps.toml` entry GAP-036, and the skill of the component.

### Load these skills

- anima-tech-sysml-pilot, anima-specifying-requirements

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The pilot implementation checks it. A test fails on a marker that has no valid trigger.
- Check: GAP-036 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
