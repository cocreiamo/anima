---
id: TASK-13
title: 'GAP-015: Rollback of a failed self-initialization of the secret store'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 13000
gaps:
  - GAP-015
fork: cocreiamo/anima-openbao
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-015 (OpenBao): Self-initialization from declarative stanzas has no rollback: a failure leaves the storage unusable and the server then refuses to unseal.

Impact: A failed first start cannot be repaired in place; it needs an empty state (R36).

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-openbao (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: Self-initialization is transactional, or a failed one can be resumed.
- [ ] #2 Check: GAP-015 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-13, GAP-015: Rollback of a failed self-initialization of the secret store. Role: implementer.

### Read first

- `gaps.toml` entry GAP-015, and the skill of the component.

### Load these skills

- anima-tech-openbao, anima-maintaining-a-fork, anima-secrets-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: Self-initialization is transactional, or a failed one can be resumed.
- Check: GAP-015 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
