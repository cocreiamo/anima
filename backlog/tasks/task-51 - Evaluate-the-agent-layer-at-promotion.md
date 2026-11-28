---
id: TASK-51
title: Evaluate the agent layer at promotion
status: To Do
assignee: []
created_date: '2026-11-27T18:18:45Z'
labels:
  - pending-tests
dependencies: []
ordinal: 51000
gaps: []
fork: none
role: implementer
owns:
  - docs/evaluation/**
  - mise-tasks/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Specified in docs/evaluation/scenarios.md and not run: run the scenarios with and without the agent layer and report the difference. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R88_agent_layer_evaluated_at_promotion
<!-- AC:END -->

## Brief

Task: TASK-51, Evaluate the agent layer at promotion. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-working-as-an-agent

### Own these paths

- docs/evaluation/**
- mise-tasks/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R88_agent_layer_evaluated_at_promotion

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
