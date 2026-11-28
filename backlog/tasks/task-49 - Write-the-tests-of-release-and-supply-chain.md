---
id: TASK-49
title: Write the tests of release and supply chain
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
labels:
  - pending-tests
dependencies: []
ordinal: 49000
gaps: []
fork: none
role: implementer
owns:
  - .github/workflows/**
  - tests/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about attested published images, images for both architectures, a release only from a verified commit and reproducible builds. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R16_published_images_attested
- [ ] #2 test_R23_images_for_both_architectures
- [ ] #3 test_R24_release_only_from_verified_commit
- [ ] #4 test_R47_builds_reproducible
<!-- AC:END -->

## Brief

Task: TASK-49, Write the tests of release and supply chain. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-branching-and-releasing, anima-tech-github-governance, anima-specifying-requirements

### Own these paths

- .github/workflows/**
- tests/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R16_published_images_attested
- test_R23_images_for_both_architectures
- test_R24_release_only_from_verified_commit
- test_R47_builds_reproducible

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
