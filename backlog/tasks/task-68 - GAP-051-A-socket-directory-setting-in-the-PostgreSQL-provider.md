---
id: TASK-68
title: 'GAP-051: A socket directory setting in the PostgreSQL provider'
status: To Do
assignee: []
created_date: '2026-11-27T19:35:23Z'
labels:
  - upstream
dependencies: []
ordinal: 68000
gaps:
  - GAP-051
fork: cocreiamo/anima-terraform-provider-postgresql
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-051 (terraform-provider-postgresql): the provider has no setting for the directory of a Unix socket; a connection over the local socket works only with an empty host and PGHOST.

Impact: the configurator's connection to the superuser depends on an environment variable that the provider reads implicitly.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-terraform-provider-postgresql (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the provider accepts the socket directory as a setting
- [ ] #2 Check: GAP-051 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-68, GAP-051: A socket directory setting in the PostgreSQL provider. Role: implementer.

### Read first

- `gaps.toml` entry GAP-051, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: the provider accepts the socket directory as a setting
- Check: GAP-051 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
