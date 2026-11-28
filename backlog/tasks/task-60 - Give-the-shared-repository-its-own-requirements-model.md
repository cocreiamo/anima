---
id: TASK-60
title: Give the shared repository its own requirements model
status: To Do
assignee: []
created_date: '2026-11-27T18:37:46Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 60000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The shared repository validates and exports a requirements model with the same tasks as the product repository, and every check there becomes a requirement with a test and its negative case. Why: today the shared repository's checks (REUSE, workflows, formatting, spelling) are plain tasks, and the rule of the product repository is that nothing is checked outside the model.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the shared repository has a requirements model that its model tasks validate and export
- [ ] #2 Check: every check of the shared repository's check task is a requirement with a test and a _detects_violation companion
<!-- AC:END -->

## Brief

Task: TASK-60, Give the shared repository its own requirements model. Role: implementer.

### Read first

- `mise.toml`, `model/anima.sysml` and `mise-tasks/model/` of this repository, which are the pattern to follow
- `shared/mise.toml` and `shared/AGENTS.md`
- TASK-61 (the standard this model follows) and TASK-63 (the tooling it runs)

### Load these skills

- anima-specifying-requirements, anima-tech-sysml-pilot, anima-tech-mise, anima-repository-conventions

### Own these paths

- shared/**

### Do not touch

- the paths of this repository outside `shared/`, generated files, lock files, `third_party/`

### Acceptance

- Check: the shared repository has a requirements model that its model tasks validate and export
- Check: every check of the shared repository's check task is a requirement with a test and a _detects_violation companion

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
