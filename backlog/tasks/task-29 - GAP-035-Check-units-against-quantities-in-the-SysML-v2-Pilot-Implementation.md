---
id: TASK-29
title: 'GAP-035: Check units against quantities in the SysML v2 Pilot Implementation'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - upstream
dependencies: []
ordinal: 29000
gaps:
  - GAP-035
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-035 (SysML v2 Pilot Implementation): The Pilot Implementation does not check that the unit of a value fits the quantity of the attribute: a number of bytes bound to a duration validates.

Impact: A threshold with a wrong unit passes the model check.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The pilot implementation checks it. A test asserts the unit name of every threshold it reads (R55).
- [ ] #2 Check: GAP-035 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-29, GAP-035: Check units against quantities in the SysML v2 Pilot Implementation. Role: implementer.

### Read first

- `gaps.toml` entry GAP-035, and the skill of the component.

### Load these skills

- anima-tech-sysml-pilot, anima-specifying-requirements

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The pilot implementation checks it. A test asserts the unit name of every threshold it reads (R55).
- Check: GAP-035 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
