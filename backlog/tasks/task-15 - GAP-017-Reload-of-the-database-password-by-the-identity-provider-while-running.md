---
id: TASK-15
title: >-
  GAP-017: Reload of the database password by the identity provider while
  running
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - upstream
dependencies: []
ordinal: 15000
gaps:
  - GAP-017
fork: cocreiamo/anima-keycloak
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-017 (Keycloak): Keycloak does not reload its database password while running.

Impact: The identity provider's database password cannot be rotated under a running process; it must be restarted.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-keycloak (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: Keycloak reloads the database password without a restart.
- [ ] #2 Check: GAP-017 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-15, GAP-017: Reload of the database password by the identity provider while running. Role: implementer.

### Read first

- `gaps.toml` entry GAP-017, and the skill of the component.

### Load these skills

- anima-tech-keycloak, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: Keycloak reloads the database password without a restart.
- Check: GAP-017 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
