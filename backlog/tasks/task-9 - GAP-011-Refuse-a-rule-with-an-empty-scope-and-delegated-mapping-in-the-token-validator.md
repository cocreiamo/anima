---
id: TASK-9
title: >-
  GAP-011: Refuse a rule with an empty scope and delegated mapping in the token
  validator
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 9000
gaps:
  - GAP-011
fork: cocreiamo/anima-pg-oidc-validator
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-011 (pg_oidc_validator): A rule with an empty scope and delegated mapping admits any valid token of the issuer.

Impact: A misconfigured rule would let every identity of the realm in.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-pg-oidc-validator (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The validator refuses an empty scope when the mapping is delegated.
- [ ] #2 Check: GAP-011 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-9, GAP-011: Refuse a rule with an empty scope and delegated mapping in the token validator. Role: implementer.

### Read first

- `gaps.toml` entry GAP-011, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The validator refuses an empty scope when the mapping is delegated.
- Check: GAP-011 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
