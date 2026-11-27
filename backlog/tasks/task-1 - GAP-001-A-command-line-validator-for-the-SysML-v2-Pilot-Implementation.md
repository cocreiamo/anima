---
id: TASK-1
title: 'GAP-001: A command-line validator for the SysML v2 Pilot Implementation'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - upstream
dependencies: []
ordinal: 1000
gaps:
  - GAP-001
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-001 (SysML v2 Pilot Implementation): There is no command-line validator. Its interactive shell reads a model on standard input and always exits 0, even when the model has errors.

Impact: A model error would not fail a build by itself.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The pilot implementation offers a validator whose exit status reports errors and warnings.
- [ ] #2 Check: GAP-001 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-1, GAP-001: A command-line validator for the SysML v2 Pilot Implementation. Role: implementer.

### Read first

- `gaps.toml` entry GAP-001, and the skill of the component.

### Load these skills

- anima-tech-sysml-pilot, anima-specifying-requirements

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The pilot implementation offers a validator whose exit status reports errors and warnings.
- Check: GAP-001 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
