---
id: TASK-5
title: 'GAP-006: Check the audience of a token in the token validator'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:38Z'
labels:
  - upstream
dependencies: []
ordinal: 5000
gaps:
  - GAP-006
fork: cocreiamo/anima-pg-oidc-validator
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-006 (pg_oidc_validator): The audience (aud) of a token is not checked. Confirmed in the 1.1.0 source: a token issued to another client of the same realm opened a session.

Impact: A token issued for another client of the same issuer is accepted unless the role's scope was not granted to that client.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-pg-oidc-validator (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The validator checks the audience of a token.
- [ ] #2 Check: GAP-006 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-5, GAP-006: Check the audience of a token in the token validator. Role: implementer.

### Read first

- `gaps.toml` entry GAP-006, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The validator checks the audience of a token.
- Check: GAP-006 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
