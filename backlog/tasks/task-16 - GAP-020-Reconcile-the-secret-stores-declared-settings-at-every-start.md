---
id: TASK-16
title: 'GAP-020: Reconcile the secret store''s declared settings at every start'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 16000
gaps:
  - GAP-020
fork: cocreiamo/anima-openbao
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-020 (OpenBao): Self-initialization runs once only, on an empty storage. Policies and other declared settings of the secret store are not reconciled at later starts, and its declared profiles do not prune: a declaration that is removed leaves its object behind.

Impact: An upgrade that changes a policy or a secrets engine setting does not reach an installation that already exists (R37).

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-openbao (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The declared state of the secret store converges at every start, removals included, by OpenBao itself or by the configurator (ADR 0006).
- [ ] #2 Check: GAP-020 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-16, GAP-020: Reconcile the secret store's declared settings at every start. Role: implementer.

### Read first

- `gaps.toml` entry GAP-020, and the skill of the component.

### Load these skills

- anima-tech-openbao, anima-maintaining-a-fork, anima-secrets-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The declared state of the secret store converges at every start, removals included, by OpenBao itself or by the configurator (ADR 0006).
- Check: GAP-020 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
