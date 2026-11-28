---
id: TASK-10
title: 'GAP-012: Specific refusal messages in the token validator'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 10000
gaps:
  - GAP-012
fork: cocreiamo/anima-pg-oidc-validator
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-012 (pg_oidc_validator): The refusal messages are generic, and a refusal for signature or issuer carries no identity.

Impact: A refused login is hard to diagnose and cannot be attributed to a person in the log.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-pg-oidc-validator (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: A refusal says why and, where the token can be read, whom it was for.
- [ ] #2 Check: GAP-012 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-10, GAP-012: Specific refusal messages in the token validator. Role: implementer.

### Read first

- `gaps.toml` entry GAP-012, and the skill of the component.

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: A refusal says why and, where the token can be read, whom it was for.
- Check: GAP-012 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
