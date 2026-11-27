---
id: TASK-4
title: 'GAP-004: A CIS Benchmark for PostgreSQL 18 in pgdsat'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - upstream
dependencies: []
ordinal: 4000
gaps:
  - GAP-004
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-004 (pgdsat): pgdsat implements the CIS Benchmark for PostgreSQL 17. No benchmark is declared for PostgreSQL 18.

Impact: Some controls may not apply to the database server as written.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: A CIS Benchmark for PostgreSQL 18 exists and pgdsat implements it, or we decide on our own control list.
- [ ] #2 Check: GAP-004 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-4, GAP-004: A CIS Benchmark for PostgreSQL 18 in pgdsat. Role: implementer.

### Read first

- `gaps.toml` entry GAP-004, and the skill of the component.

### Load these skills

- anima-adopting-a-component, anima-database-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: A CIS Benchmark for PostgreSQL 18 exists and pgdsat implements it, or we decide on our own control list.
- Check: GAP-004 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
