---
id: TASK-36
title: 'GAP-042: A configurator provider for the secret store itself'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:42Z'
labels:
  - gap
dependencies: []
ordinal: 36000
gaps:
  - GAP-042
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-042 (OpenTofu providers): No configurator provider is published for the secret store itself; the provider for another product, used against its compatible API, is the one in use.

Impact: The configurator depends on a provider whose product is not the one it configures, so a difference between the two interfaces is found only by running it.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: A provider for the secret store is published and pinned, or a contribution of our fork (cocreiamo/anima-terraform-provider-vault) makes the compatible API a tested contract.
- [ ] #2 Check: GAP-042 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-36, GAP-042: A configurator provider for the secret store itself. Role: implementer.

### Read first

- `gaps.toml` entry GAP-042, and the skill of the component.

### Load these skills

- anima-tech-opentofu, anima-maintaining-a-fork, anima-configuration-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: A provider for the secret store is published and pinned, or a contribution of our fork (cocreiamo/anima-terraform-provider-vault) makes the compatible API a tested contract.
- Check: GAP-042 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
