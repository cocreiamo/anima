---
id: TASK-54
title: Turn on immutable releases
status: Done
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:45Z'
updated_date: '2026-11-28T17:35:26Z'
labels:
  - founder
dependencies: []
ordinal: 54000
gaps: []
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A published tag is never moved or reused (`anima-branching-and-releasing`, rule 8). GitHub can enforce it with the setting for immutable releases, which only the founder can change.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: the setting is on for the repository and a published release cannot be changed
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-28: done by the platform team (session of the infrastructure repository), by the founder's sign-in. Verified read-only the same day: GET repos/cocreiamo/anima/immutable-releases answered enabled true, enforced_by_owner false.
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-54, Turn on immutable releases. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: the setting is on for the repository and a published release cannot be changed

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
