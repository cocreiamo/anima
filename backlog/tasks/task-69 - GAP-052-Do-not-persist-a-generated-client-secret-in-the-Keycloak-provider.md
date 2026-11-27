---
id: TASK-69
title: 'GAP-052: Do not persist a generated client secret in the Keycloak provider'
status: To Do
assignee: []
created_date: '2026-11-27T19:35:23Z'
labels:
  - upstream
dependencies: []
ordinal: 69000
gaps:
  - GAP-052
fork: cocreiamo/anima-terraform-provider-keycloak
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-052 (terraform-provider-keycloak): the provider persists the generated secret of a confidential client in the state unless the write-only attribute is used.

Impact: a client declared without the write-only attribute would put a secret into the state.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-terraform-provider-keycloak (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the provider does not persist a generated client secret, or a check refuses a confidential client without the write-only attribute
- [ ] #2 Check: GAP-052 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-69, GAP-052: Do not persist a generated client secret in the Keycloak provider. Role: implementer.

### Read first

- `gaps.toml` entry GAP-052, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-tech-keycloak, anima-maintaining-a-fork

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: the provider does not persist a generated client secret, or a check refuses a confidential client without the write-only attribute
- Check: GAP-052 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
