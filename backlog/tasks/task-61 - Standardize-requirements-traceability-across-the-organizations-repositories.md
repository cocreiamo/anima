---
id: TASK-61
title: Standardize requirements traceability across the organization's repositories
status: To Do
assignee: []
created_date: '2026-11-27T18:38:13Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 61000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
One way to state requirements, verifications, thresholds and fitness-function markers in the product repository, the shared repository and the infrastructure repository; one set of shared tasks and checks, each repository running them on its own model. Why: traceability that differs between repositories cannot be checked once, and each repository would reinvent its own.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: one specification of requirements, verifications, thresholds and fitness-function markers is written in the shared repository
- [ ] #2 Check: the product, shared and infrastructure repositories each run the same shared tasks and checks on their own model
<!-- AC:END -->

## Brief

Task: TASK-61, Standardize requirements traceability across the organization's repositories. Role: implementer.

### Read first

- `model/anima.sysml`, `tests/repository/test_traceability.py`, `tests/repository/test_fitness.py` and `mise-tasks/model/` of this repository
- TASK-60 (the shared repository's own model) and TASK-63 (the tooling)

### Load these skills

- anima-specifying-requirements, anima-tech-sysml-pilot, anima-repository-conventions

### Own these paths

- shared/**

### Do not touch

- the paths of this repository outside `shared/` until the specification is decided with the founder, generated files, lock files, `third_party/`

### Acceptance

- Check: one specification of requirements, verifications, thresholds and fitness-function markers is written in the shared repository
- Check: the product, shared and infrastructure repositories each run the same shared tasks and checks on their own model

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
