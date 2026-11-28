---
id: TASK-23
title: >-
  GAP-028: A duration in hours reported as a perpetual difference by the Vault
  provider
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
labels:
  - upstream
dependencies: []
ordinal: 23000
gaps:
  - GAP-028
fork: cocreiamo/anima-terraform-provider-vault
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-028 (terraform-provider-vault): A duration written as 720h instead of in seconds is reported as a perpetual difference.

Impact: Every plan shows a change that is not one; durations must be written in seconds.

The remedy is a contribution upstream, prepared in the fork cocreiamo/anima-terraform-provider-vault (`anima-maintaining-a-fork`): written for upstream first, in upstream's licence and with its tools, then submitted the way upstream asks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The upstream project fixes it, or the contribution of our fork is merged.
- [ ] #2 Check: GAP-028 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-23, GAP-028: A duration in hours reported as a perpetual difference by the Vault provider. Role: implementer.

### Read first

- `gaps.toml` entry GAP-028, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The upstream project fixes it, or the contribution of our fork is merged.
- Check: GAP-028 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
