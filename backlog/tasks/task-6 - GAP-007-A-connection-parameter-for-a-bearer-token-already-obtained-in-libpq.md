---
id: TASK-6
title: 'GAP-007: A connection parameter for a bearer token already obtained, in libpq'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - upstream
dependencies: []
ordinal: 6000
gaps:
  - GAP-007
fork: cocreiamo/anima-postgres
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-007 (libpq): No connection parameter accepts a bearer token that was already obtained. Only the device flow is built in.

Impact: Tests and scripts cannot log in with a token without an OAuth hook.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-postgres (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: libpq accepts a bearer token as a connection parameter.
- [ ] #2 Check: GAP-007 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-6, GAP-007: A connection parameter for a bearer token already obtained, in libpq. Role: implementer.

### Read first

- `gaps.toml` entry GAP-007, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-database-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: libpq accepts a bearer token as a connection parameter.
- Check: GAP-007 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
