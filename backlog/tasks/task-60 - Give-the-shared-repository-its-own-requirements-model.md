---
id: TASK-60
title: Give the shared repository its own requirements model
status: Done
assignee: []
created_date: '2026-11-27T18:37:46Z'
updated_date: '2026-11-28T10:15:31Z'
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
- [x] #1 Check: the shared repository has a requirements model that its model tasks validate and export
- [x] #2 Check: every check of the shared repository's check task is a requirement with a test and a _detects_violation companion
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

Task: TASK-60. Role: implementer. Date: 2026-11-28.

### Done

- Shared repository, pull request cocreiamo/.github#1, merged as 6a8d9e44def0e7d7f6146fa549256d19456aa9f5: `model/shared.sysml` (R1 to R13, one per check of its check task, each a fitness function with a verification named like its test), `tests/test_model.py` and `tests/test_files.py` (every `test_R<n>_…` with a `_detects_violation` companion), `mise-tasks/model/{check,export,fetch}` (copied from this repository until TASK-63), `mise run check` now runs `model:check` and `test` (acceptance 1).
- Acceptance 2: R6 fails when a command of the shared check task is not the check of a requirement; R7 to R13 cover REUSE, workflow analysis and audit, formatting, spelling and linting.
- This repository: `shared/` pointer moved to the merged commit.

### Ran

- Shared repository: `mise run check` green (26 passed), also in CI of the pull request before merging.
- This repository: `mise run generate`, `mise run check`; results in the pull request.

### Only read

- Whether the pilot cache of the shared CI is restored: not observed.

### Denied commands

- None. The harness twice refused a compound command as too complex; it was split.

### Lessons to write back

- None written.

### Decisions the brief did not cover

- The model follows this repository's conventions as they are; TASK-61 specifies the standard.
- The tooling is copied, not shared, until TASK-63.
- No threshold and one trigger value in the shared model, because no check there needs more.

### Inconsistencies

- This repository's `.github/workflows/ci.yml` pins shared workflows at 0b4136b, older than the pointer of `shared/`.
