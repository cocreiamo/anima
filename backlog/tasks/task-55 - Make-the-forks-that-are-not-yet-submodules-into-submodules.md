---
id: TASK-55
title: Make the forks that are not yet submodules into submodules
status: To Do
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:46Z'
labels:
  - founder
dependencies: []
ordinal: 55000
gaps: []
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
anima-opentofu, anima-terraform-provider-postgresql, anima-terraform-provider-vault, anima-terraform-provider-keycloak and anima-mailpit exist as forks and are pinned in components.toml by the commit of an upstream release. Adding a submodule changes .gitmodules and third_party/, and is committed by the founder (`anima-maintaining-a-fork`).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: each of the five is a submodule under third_party/ and its components.toml entry has the submodule field with the same commit
- [ ] #2 Check: the paths of the skills for them are no longer listed in skills/not-yet-present.toml
<!-- AC:END -->

## Brief

Task: TASK-55, Make the forks that are not yet submodules into submodules. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: each of the five is a submodule under third_party/ and its components.toml entry has the submodule field with the same commit
- Check: the paths of the skills for them are no longer listed in skills/not-yet-present.toml

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
