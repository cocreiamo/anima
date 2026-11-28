---
id: TASK-25
title: 'GAP-030: Use the official image of the configurator as a base image'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:41Z'
labels:
  - upstream
dependencies: []
ordinal: 25000
gaps:
  - GAP-030
fork: cocreiamo/anima-opentofu
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-030 (OpenTofu): The official image of the configurator refuses to be used as a base image.

Impact: The image of the configurator cannot be extended with our providers and files; it is built from the pinned source instead.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-opentofu (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The condition is gone, or the implementation of the engine image settles it.
- [ ] #2 Check: GAP-030 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-25, GAP-030: Use the official image of the configurator as a base image. Role: implementer.

### Read first

- `gaps.toml` entry GAP-030, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The condition is gone, or the implementation of the engine image settles it.
- Check: GAP-030 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
