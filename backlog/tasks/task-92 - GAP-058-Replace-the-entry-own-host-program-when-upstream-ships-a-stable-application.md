---
id: TASK-92
title: >-
  GAP-058: Replace the entry's own host program when upstream ships a stable
  application
status: To Do
assignee: []
created_date: '2026-11-28T10:05:45Z'
labels:
  - upstream
dependencies: []
ordinal: 92000
gaps:
  - GAP-058
fork: cocreiamo/anima-yarp
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-058 (YARP): the packaged application is preview only, so the entry runs a host program of ours. Watch for a stable, configurable application upstream and, when it exists, run it instead.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: upstream ships a stable application configured by files with what the entry needs, and the entry runs it instead of our host program
- [ ] #2 Check: GAP-058 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-92, GAP-058: Replace the entry's own host program when upstream ships a stable application. Role: implementer.

### Read first

- `gaps.toml` entry GAP-058, and the skill of the component

### Load these skills

- anima-adopting-a-component

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: upstream ships a stable application configured by files with what the entry needs, and the entry runs it instead of our host program
- Check: GAP-058 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
