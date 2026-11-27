---
id: TASK-11
title: 'GAP-013: Do not log a FATAL for the discovery round of a token login in libpq'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 11000
gaps:
  - GAP-013
fork: cocreiamo/anima-postgres
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-013 (libpq): The discovery round of libpq makes every token login log one FATAL first, before the login that succeeds.

Impact: The server log of a healthy system holds a FATAL line for each token login, which hides real failures.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-postgres (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: libpq no longer opens a connection that the server must refuse, or the server does not log it as FATAL.
- [ ] #2 Check: GAP-013 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-11, GAP-013: Do not log a FATAL for the discovery round of a token login in libpq. Role: implementer.

### Read first

- `gaps.toml` entry GAP-013, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-database-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: libpq no longer opens a connection that the server must refuse, or the server does not log it as FATAL.
- Check: GAP-013 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
