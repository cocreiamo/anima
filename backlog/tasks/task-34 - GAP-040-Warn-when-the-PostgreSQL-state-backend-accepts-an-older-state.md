---
id: TASK-34
title: 'GAP-040: Warn when the PostgreSQL state backend accepts an older state'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:42Z'
labels:
  - upstream
dependencies: []
ordinal: 34000
gaps:
  - GAP-040
fork: cocreiamo/anima-opentofu
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-040 (OpenTofu): The PostgreSQL state backend accepts an older state without any warning.

Impact: A lost or stale state is applied as if it were current: roles, mounts and the realm fail with already exists, policies and connections are silently overwritten, and a certificate authority created by the configurator was silently duplicated.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-opentofu (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The backend refuses or warns on an older state, or the configurator checks the state's serial against a recorded one before it applies.
- [ ] #2 Check: GAP-040 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-34, GAP-040: Warn when the PostgreSQL state backend accepts an older state. Role: implementer.

### Read first

- `gaps.toml` entry GAP-040, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The backend refuses or warns on an older state, or the configurator checks the state's serial against a recorded one before it applies.
- Check: GAP-040 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
