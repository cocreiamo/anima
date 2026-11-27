---
id: TASK-46
title: Write the tests of secrets
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
labels:
  - pending-tests
dependencies: []
ordinal: 46000
gaps: []
fork: none
role: implementer
owns:
  - engine/secrets/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about secrets generated at first start and about a storage connection that uses no secret. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R7_secrets_generated
- [ ] #2 test_R62_storage_connection_uses_no_secret
<!-- AC:END -->

## Brief

Task: TASK-46, Write the tests of secrets. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-secrets-design, anima-tech-openbao

### Own these paths

- engine/secrets/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R7_secrets_generated
- test_R62_storage_connection_uses_no_secret

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
