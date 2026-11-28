---
id: TASK-91
title: >-
  GAP-057: Build the entry's library from a fork of ours, or record that the
  package stays
status: To Do
assignee: []
created_date: '2026-11-28T10:05:45Z'
labels:
  - gap
dependencies: []
ordinal: 91000
gaps:
  - GAP-057
fork: cocreiamo/anima-yarp
role: implementer
owns:
  - gaps.toml
  - components.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-057 (YARP): the entry's library is taken from its NuGet package, pinned by version and content hash, and the runtime from a distribution's packages; the mirror fork cocreiamo/anima-yarp does not exist yet. The remedy is ours; the gap stays open until the condition of gaps.toml holds. Creating the fork is a repository setting that needs the founder's approval.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the mirror fork of YARP exists and the entry's build compiles the library from the fork's pinned commit, or the founder records that the package stays
- [ ] #2 Check: GAP-057 is updated in gaps.toml (status)
<!-- AC:END -->

## Brief

Task: TASK-91, GAP-057: Build the entry's library from a fork of ours, or record that the package stays. Role: implementer.

### Read first

- `gaps.toml` entry GAP-057, `docs/adr/0008-the-http-entry-point-of-the-engine.md`, `anima-maintaining-a-fork`

### Load these skills

- anima-adopting-a-component, anima-maintaining-a-fork

### Own these paths

- gaps.toml
- components.toml

### Do not touch

- third_party/**; creating the fork is a repository change that needs the founder's approval

### Acceptance

- Check: the mirror fork of YARP exists and the entry's build compiles the library from the fork's pinned commit, or the founder records that the package stays
- Check: GAP-057 is updated in gaps.toml (status)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
