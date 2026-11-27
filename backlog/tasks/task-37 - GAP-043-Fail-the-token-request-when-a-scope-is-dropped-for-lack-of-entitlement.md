---
id: TASK-37
title: >-
  GAP-043: Fail the token request when a scope is dropped for lack of
  entitlement
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - upstream
dependencies: []
ordinal: 37000
gaps:
  - GAP-043
fork: cocreiamo/anima-keycloak
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-043 (Keycloak): A scope that the user is not entitled to is dropped silently from the token: the token request does not fail.

Impact: A missing scope is found only by decoding the token; a test that only checks that a token is issued passes.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-keycloak (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The token request fails or warns when a requested scope is not granted, or a test of ours checks the claim for every role.
- [ ] #2 Check: GAP-043 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-37, GAP-043: Fail the token request when a scope is dropped for lack of entitlement. Role: implementer.

### Read first

- `gaps.toml` entry GAP-043, and the skill of the component.

### Load these skills

- anima-tech-keycloak, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The token request fails or warns when a requested scope is not granted, or a test of ours checks the claim for every role.
- Check: GAP-043 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
