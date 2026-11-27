---
id: TASK-35
title: >-
  GAP-041: A key provider that depends on the secret store, for the run that
  configures it
status: To Do
assignee: []
created_date: '2026-11-27T18:18:42Z'
labels:
  - upstream
dependencies: []
ordinal: 35000
gaps:
  - GAP-041
fork: cocreiamo/anima-opentofu
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-041 (OpenTofu): A key provider that depends on the secret store cannot key the run that configures the secret store: the run fails before planning.

Impact: The state of the run that sets up the secret store cannot be keyed from the secret store.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-opentofu (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The state of that run is keyed by a provider that does not need the secret store, and a test shows the first start converges.
- [ ] #2 Check: GAP-041 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-35, GAP-041: A key provider that depends on the secret store, for the run that configures it. Role: implementer.

### Read first

- `gaps.toml` entry GAP-041, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The state of that run is keyed by a provider that does not need the secret store, and a test shows the first start converges.
- Check: GAP-041 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
