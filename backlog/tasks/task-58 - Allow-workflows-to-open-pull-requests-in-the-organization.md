---
id: TASK-58
title: Allow workflows to open pull requests in the organization
status: To Do
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:46Z'
labels:
  - founder
dependencies: []
ordinal: 58000
gaps:
  - GAP-046
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A repository cannot let GitHub Actions create and approve pull requests until the organization allows it; the release preparation needs it. Only the founder changes the organization setting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the organization allows it and the repository setting is applied by the file that describes the repository
- [ ] #2 Check: GAP-046 is closed in gaps.toml
<!-- AC:END -->

## Brief

Task: TASK-58, Allow workflows to open pull requests in the organization. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: the organization allows it and the repository setting is applied by the file that describes the repository
- Check: GAP-046 is closed in gaps.toml

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
