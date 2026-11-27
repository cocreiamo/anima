---
id: TASK-8
title: 'GAP-010: Refuse a token without an expiry claim in the token validator'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 8000
gaps:
  - GAP-010
fork: cocreiamo/anima-pg-oidc-validator
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-010 (pg_oidc_validator): A token without an expiry claim is accepted.

Impact: A token that never expires is a permanent credential.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-pg-oidc-validator (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The validator refuses a token without an expiry claim.
- [ ] #2 Check: GAP-010 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-8, GAP-010: Refuse a token without an expiry claim in the token validator. Role: implementer.

### Read first

- `gaps.toml` entry GAP-010, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The validator refuses a token without an expiry claim.
- Check: GAP-010 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
