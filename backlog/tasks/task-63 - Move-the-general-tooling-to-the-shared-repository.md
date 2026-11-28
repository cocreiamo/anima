---
id: TASK-63
title: Move the general tooling to the shared repository
status: To Do
assignee: []
created_date: '2026-11-27T18:38:15Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 63000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
  - mise.toml
  - mise-tasks/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The model tasks, the generators and the general checks move from the product repository to the shared repository, and the product repository consumes them. Why: the tooling is not about the product, and every repository of the organization needs it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the model tasks, the generators and the general checks live in the shared repository and the product repository runs them from there
- [ ] #2 Check: mise run check passes in the product repository and in the shared repository
<!-- AC:END -->

## Brief

Task: TASK-63, Move the general tooling to the shared repository. Role: implementer.

### Read first

- `mise.toml`, `mise-tasks/` and `tests/repository/` of this repository
- TASK-61 and TASK-62 (what the tooling checks)

### Load these skills

- anima-tech-mise, anima-repository-conventions, anima-working-as-an-agent

### Own these paths

- shared/**, mise.toml, mise-tasks/** (agree with the owner of `mise-tasks/engine/**` first)

### Do not touch

- `engine/**`, `config/**`, `tests/system/**`, `mise-tasks/engine/**`, generated files, lock files, `third_party/`

### Acceptance

- Check: the model tasks, the generators and the general checks live in the shared repository and the product repository runs them from there
- Check: mise run check passes in the product repository and in the shared repository

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
