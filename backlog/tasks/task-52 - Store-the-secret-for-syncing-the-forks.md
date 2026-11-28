---
id: TASK-52
title: Store the secret for syncing the forks
status: To Do
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:45Z'
labels:
  - founder
dependencies: []
ordinal: 52000
gaps: []
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The scheduled workflow that fast-forwards the mirror branches of the forks needs a token that can write to them, stored as the repository secret FORK_SYNC_TOKEN (`anima-maintaining-a-fork`, rule 3). Only the founder creates a secret.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the secret FORK_SYNC_TOKEN exists and a run of the sync-forks workflow fast-forwards a mirror branch
<!-- AC:END -->

## Brief

Task: TASK-52, Store the secret for syncing the forks. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: the secret FORK_SYNC_TOKEN exists and a run of the sync-forks workflow fast-forwards a mirror branch

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
