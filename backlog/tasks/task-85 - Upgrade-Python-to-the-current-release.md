---
id: TASK-85
title: Upgrade Python to the current release
status: To Do
assignee: []
created_date: '2026-11-28T09:48:12Z'
labels:
  - tooling
dependencies: []
ordinal: 85000
gaps: []
fork: none
role: implementer
owns:
  - mise.toml
  - pyproject.toml
  - tests/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PR 18 (Renovate) moves Python from 3.13 to 3.15 and fails the check: the formatter wants the unparenthesised form of an except clause with two exceptions (tests/repository/test_agent_layer.py:641, 3.14 syntax). A deliberate upgrade: take the formatter's output and decide the syntax, then move the pins together (mise.toml, mise.lock, pyproject.toml, uv.lock).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: mise run check is green on the new Python version
<!-- AC:END -->

## Brief

Task: TASK-85, Upgrade Python to the current release. Role: implementer.

### Read first

- Renovate pull request 18 (the pins it moves) and the failing line `tests/repository/test_agent_layer.py:641`.

### Load these skills

- anima-tech-mise, anima-specifying-requirements, anima-working-as-an-agent

### Own these paths

- mise.toml
- pyproject.toml
- tests/**

### Do not touch

- third_party/**, generated files, lock files by hand (`mise.lock` and `uv.lock` are written by their tools); do not weaken a check

### Acceptance

- Check: mise run check is green on the new Python version

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
