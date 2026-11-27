---
id: TASK-62
title: >-
  Put the common structure every repository shows at first sight in the shared
  repository
status: To Do
assignee: []
created_date: '2026-11-27T18:38:14Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 62000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The same top-level layout by role (model, decision records, registers, skills, tasks), the same table of homes in AGENTS.md and the same entry tasks in every repository of the organization: decided once in the shared repository and checked in each repository. Why: a reader, human or agent, should find the same things in the same places in every repository (screaming architecture).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the layout, the table of homes and the entry tasks are specified once in the shared repository
- [ ] #2 Check: a check in each repository fails when its layout, table of homes or entry tasks differ from the specification
<!-- AC:END -->

## Brief

Task: TASK-62, Put the common structure every repository shows at first sight in the shared repository. Role: implementer.

### Read first

- `AGENTS.md` (the table of homes), `skills/anima-repository-conventions.md` and `mise.toml` of this repository
- TASK-61 (the traceability standard) and TASK-63 (the tooling that checks it)

### Load these skills

- anima-repository-conventions, anima-working-as-an-agent, anima-product-principles

### Own these paths

- shared/**

### Do not touch

- the paths of this repository outside `shared/` until the structure is decided with the founder, generated files, lock files, `third_party/`

### Acceptance

- Check: the layout, the table of homes and the entry tasks are specified once in the shared repository
- Check: a check in each repository fails when its layout, table of homes or entry tasks differ from the specification

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
