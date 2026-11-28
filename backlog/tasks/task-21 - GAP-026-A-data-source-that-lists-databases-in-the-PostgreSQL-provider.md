---
id: TASK-21
title: 'GAP-026: A data source that lists databases in the PostgreSQL provider'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
labels:
  - upstream
dependencies: []
ordinal: 21000
gaps:
  - GAP-026
fork: cocreiamo/anima-terraform-provider-postgresql
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-026 (terraform-provider-postgresql): The provider has no data source that lists databases.

Impact: An extension in every existing database cannot be declared: the list of databases is not known to the declaration.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-terraform-provider-postgresql (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The upstream project fixes it, or the contribution of our fork is merged.
- [ ] #2 Check: GAP-026 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-21, GAP-026: A data source that lists databases in the PostgreSQL provider. Role: implementer.

### Read first

- `gaps.toml` entry GAP-026, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The upstream project fixes it, or the contribution of our fork is merged.
- Check: GAP-026 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
