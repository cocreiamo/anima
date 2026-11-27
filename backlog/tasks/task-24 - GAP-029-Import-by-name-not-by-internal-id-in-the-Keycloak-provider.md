---
id: TASK-24
title: 'GAP-029: Import by name, not by internal id, in the Keycloak provider'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - upstream
dependencies: []
ordinal: 24000
gaps:
  - GAP-029
fork: cocreiamo/anima-terraform-provider-keycloak
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-029 (terraform-provider-keycloak): The provider imports roles, scopes, clients and users only by internal id.

Impact: A lost state cannot be healed by declared imports: the internal ids are not known to the declaration.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-terraform-provider-keycloak (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The upstream project fixes it, or the contribution of our fork is merged.
- [ ] #2 Check: GAP-029 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-24, GAP-029: Import by name, not by internal id, in the Keycloak provider. Role: implementer.

### Read first

- `gaps.toml` entry GAP-029, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The upstream project fixes it, or the contribution of our fork is merged.
- Check: GAP-029 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
