---
id: TASK-48
title: Write the tests of upgrade, backup and the booted image
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
updated_date: '2026-11-27T20:19:58Z'
labels:
  - pending-tests
dependencies: []
ordinal: 48000
gaps: []
fork: none
role: implementer
owns:
  - engine/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about an upgrade converging to a new installation, removing only what is declared, never destroying data, the tested upgrade paths, all state in one store and the restore into an empty system. The booted image has its own task (TASK-79).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R20_backup_restores_into_empty_system
- [ ] #2 test_R37_upgrade_converges_to_new_installation
- [ ] #3 test_R43_upgrade_removes_only_declared
- [ ] #4 test_R44_upgrade_never_destroys_data
- [ ] #5 test_R46_upgrade_paths_tested
- [ ] #6 test_R60_all_state_in_one_store
<!-- AC:END -->

## Brief

Task: TASK-48, Write the tests of upgrade, backup and the booted image. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-designing-for-production, anima-image-design, anima-database-design, anima-specifying-requirements

### Own these paths

- engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R20_backup_restores_into_empty_system
- test_R37_upgrade_converges_to_new_installation
- test_R43_upgrade_removes_only_declared
- test_R44_upgrade_never_destroys_data
- test_R46_upgrade_paths_tested
- test_R60_all_state_in_one_store

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
