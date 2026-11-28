---
id: TASK-12
title: 'GAP-014: Carry the person in the statement log line'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 12000
gaps:
  - GAP-014
fork: cocreiamo/anima-postgres
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-014 (PostgreSQL): A statement log line carries only the role, not the person; the person is found by joining with the authentication line of the same session.

Impact: Audit by person needs a join of two log lines.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-postgres (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The log line of a statement can carry the system user of the session.
- [ ] #2 Check: GAP-014 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-12, GAP-014: Carry the person in the statement log line. Role: implementer.

### Read first

- `gaps.toml` entry GAP-014, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-database-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The log line of a statement can carry the system user of the session.
- Check: GAP-014 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
