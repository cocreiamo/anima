---
id: TASK-40
title: 'GAP-047: Isolate a project from the user-level configuration of mise'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - upstream
dependencies: []
ordinal: 40000
gaps:
  - GAP-047
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-047 (mise): A user-level configuration of the task runner leaks its tools into a project: extra tools at latest were installed from one.

Impact: A run in a project is not isolated from the user's own configuration; a tool that is not pinned by the project can appear.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The project can state that it ignores the user-level configuration, or the isolation is a task of the repository.
- [ ] #2 Check: GAP-047 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-40, GAP-047: Isolate a project from the user-level configuration of mise. Role: implementer.

### Read first

- `gaps.toml` entry GAP-047, and the skill of the component.

### Load these skills

- anima-tech-mise

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The project can state that it ignores the user-level configuration, or the isolation is a task of the repository.
- Check: GAP-047 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
