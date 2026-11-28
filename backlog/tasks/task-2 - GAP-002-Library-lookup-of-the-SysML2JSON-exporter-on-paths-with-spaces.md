---
id: TASK-2
title: 'GAP-002: Library lookup of the SysML2JSON exporter on paths with spaces'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - upstream
dependencies: []
ordinal: 2000
gaps:
  - GAP-002
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-002 (SysML v2 Pilot Implementation): The SysML2JSON exporter looks library files up by URL-encoded path and fails on the spaces in the directory names of its own library.

Impact: The JSON export of the model, which the traceability test reads, fails without a workaround.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: SysML2JSON resolves its own library without aliases.
- [ ] #2 Check: GAP-002 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-2, GAP-002: Library lookup of the SysML2JSON exporter on paths with spaces. Role: implementer.

### Read first

- `gaps.toml` entry GAP-002, and the skill of the component.

### Load these skills

- anima-tech-sysml-pilot, anima-specifying-requirements

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: SysML2JSON resolves its own library without aliases.
- Check: GAP-002 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
