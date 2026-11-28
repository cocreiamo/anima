---
id: TASK-83
title: Make format and test exclude each other
status: Done
assignee: []
created_date: '2026-11-27T20:19:48Z'
updated_date: '2026-11-28T04:16:22Z'
labels:
  - tooling
dependencies: []
ordinal: 83000
gaps: []
fork: none
role: implementer
owns:
  - mise.toml
  - mise-tasks/**
  - tests/repository/**
  - docs/postmortems/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PM-006: the formatter rewrote test files while a test session was running. Build a guard with its negative case: one lock that `mise run format` and `mise run test` take, or a check that refuses to run them together.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: a run of format and a run of test exclude each other, shown by a test with its negative case
- [x] #2 Check: PM-006 lists the guard and its status follows
<!-- AC:END -->

## Brief

Task: TASK-83, Make format and test exclude each other. Role: implementer.

### Read first

- `docs/postmortems/PM-006-formatter-rewrote-test-files-during-a-test-session.md`.

### Load these skills

- anima-tech-mise, anima-specifying-requirements, anima-working-as-an-agent

### Own these paths

- mise.toml
- mise-tasks/**
- tests/repository/**
- docs/postmortems/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: a run of format and a run of test exclude each other, shown by a test with its negative case
- Check: PM-006 lists the guard and its status follows

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
