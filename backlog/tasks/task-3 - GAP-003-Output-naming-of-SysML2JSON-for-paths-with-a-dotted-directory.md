---
id: TASK-3
title: 'GAP-003: Output naming of SysML2JSON for paths with a dotted directory'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - upstream
dependencies: []
ordinal: 3000
gaps:
  - GAP-003
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-003 (SysML v2 Pilot Implementation): SysML2JSON names its output by cutting the input path at the first dot, so a path that contains a dotted directory writes the JSON somewhere else.

Impact: The exported file is not where the caller expects it.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: SysML2JSON writes the JSON next to the input whatever the path.
- [ ] #2 Check: GAP-003 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-3, GAP-003: Output naming of SysML2JSON for paths with a dotted directory. Role: implementer.

### Read first

- `gaps.toml` entry GAP-003, and the skill of the component.

### Load these skills

- anima-tech-sysml-pilot, anima-specifying-requirements

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: SysML2JSON writes the JSON next to the input whatever the path.
- Check: GAP-003 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
