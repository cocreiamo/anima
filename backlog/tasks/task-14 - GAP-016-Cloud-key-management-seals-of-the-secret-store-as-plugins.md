---
id: TASK-14
title: 'GAP-016: Cloud key-management seals of the secret store as plugins'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
labels:
  - gap
dependencies: []
ordinal: 14000
gaps:
  - GAP-016
fork: cocreiamo/anima-openbao
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-016 (OpenBao): Cloud key-management seals are external plugins fetched as images, not part of the server.

Impact: The next adapter of the root of trust (Google Cloud KMS) adds an image to pin by digest.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The cloud seals are part of the server, or the plugin images are pinned and verified in components.toml.
- [ ] #2 Check: GAP-016 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-14, GAP-016: Cloud key-management seals of the secret store as plugins. Role: implementer.

### Read first

- `gaps.toml` entry GAP-016, and the skill of the component.

### Load these skills

- anima-tech-openbao, anima-maintaining-a-fork, anima-secrets-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The cloud seals are part of the server, or the plugin images are pinned and verified in components.toml.
- Check: GAP-016 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
