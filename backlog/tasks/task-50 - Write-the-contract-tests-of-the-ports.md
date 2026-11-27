---
id: TASK-50
title: Write the contract tests of the ports
status: To Do
assignee: []
created_date: '2026-11-27T18:18:45Z'
labels:
  - pending-tests
dependencies: []
ordinal: 50000
gaps: []
fork: none
role: implementer
owns:
  - tests/**
  - engine/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about vector search in every database, compatibility with the upstream regression suite, every adapter passing the contract suite of its port and mail delivered through the configured service. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R19_vector_search_in_every_database
- [ ] #2 test_R21_upstream_regression_suite_passes
- [ ] #3 test_R58_every_adapter_passes_its_contract_suite
- [ ] #4 test_R64_mail_delivered_through_configured_service
<!-- AC:END -->

## Brief

Task: TASK-50, Write the contract tests of the ports. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-designing-a-port, anima-specifying-requirements

### Own these paths

- tests/**
- engine/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R19_vector_search_in_every_database
- test_R21_upstream_regression_suite_passes
- test_R58_every_adapter_passes_its_contract_suite
- test_R64_mail_delivered_through_configured_service

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
