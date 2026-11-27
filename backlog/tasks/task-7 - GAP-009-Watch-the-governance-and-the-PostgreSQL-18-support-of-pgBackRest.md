---
id: TASK-7
title: 'GAP-009: Watch the governance and the PostgreSQL 18 support of pgBackRest'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - gap
dependencies: []
ordinal: 7000
gaps:
  - GAP-009
fork: cocreiamo/anima-pgbackrest
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-009 (pgBackRest): The repository was archived in April 2026, then resumed under a coalition of sponsors with releases in October 2026, so its governance is young. PostgreSQL 18 support: the release notes announce experimental support in 2.55.0 (2025-04-21) and finalize the PostgreSQL 18 catalog number in 2.57.0; they do not state that the experimental label was lifted. The pinned source knows the PostgreSQL 18 version and, since 2.59.0, PostgreSQL 19 betas.

Impact: The backup tool of the database server depends on a project whose continuity is not yet proven, and its PostgreSQL 18 support is to be confirmed by our own restore test (R20).

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The restore test of R20 passes on PostgreSQL 18 and the project has kept a regular release cadence for a year.
- [ ] #2 Check: GAP-009 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-7, GAP-009: Watch the governance and the PostgreSQL 18 support of pgBackRest. Role: implementer.

### Read first

- `gaps.toml` entry GAP-009, and the skill of the component.

### Load these skills

- anima-adopting-a-component, anima-database-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The restore test of R20 passes on PostgreSQL 18 and the project has kept a regular release cadence for a year.
- Check: GAP-009 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
