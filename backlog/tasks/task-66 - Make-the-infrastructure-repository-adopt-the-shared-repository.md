---
id: TASK-66
title: Make the infrastructure repository adopt the shared repository
status: To Do
assignee: []
created_date: '2026-11-27T18:38:17Z'
labels:
  - organization-move
  - infrastructure
dependencies: []
ordinal: 66000
gaps: []
fork: none
role: implementer
owns:
  - the infrastructure repository (not this one)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The infrastructure repository adopts everything the other tasks of the label organization-move put in the shared repository: the community health files, the reusable workflows, the Renovate preset, the requirements model standard, the common structure, the tooling, the skills and roles, and the record template. Why: the organization's repositories work the same way.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the infrastructure repository consumes the shared repository's workflows, preset, tooling, skills and roles from a pinned commit
- [ ] #2 Check: mise run check passes in the infrastructure repository on its own requirements model
<!-- AC:END -->

## Brief

Task: TASK-66, Make the infrastructure repository adopt the shared repository. Role: implementer.

### Read first

- TASK-60 to TASK-65, which put the shared parts in the shared repository
- The infrastructure repository's own `AGENTS.md` and `mise.toml`

### Load these skills

- anima-repository-conventions, anima-tech-github-governance, anima-working-as-an-agent

### Own these paths

- the infrastructure repository (not this one)

### Do not touch

- this repository, generated files, lock files

### Acceptance

- Check: the infrastructure repository consumes the shared repository's workflows, preset, tooling, skills and roles from a pinned commit
- Check: mise run check passes in the infrastructure repository on its own requirements model

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
