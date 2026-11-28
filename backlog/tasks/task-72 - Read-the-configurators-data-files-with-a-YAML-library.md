---
id: TASK-72
title: Read the configurator's data files with a YAML library
status: To Do
assignee: []
created_date: '2026-11-27T19:37:09Z'
labels:
  - engine
  - tooling
dependencies: []
ordinal: 72000
gaps: []
fork: none
role: implementer
owns:
  - engine/configure/**
  - tests/configure/**
  - pyproject.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`engine/configure/checks.py` reads the declarations of roles and identities with a hand-written reader of a subset of YAML, because the test environment has no YAML library. Adopt a library instead (`anima-product-principles`: adopt, never reinvent), add it to the project's dependencies, and delete the hand-written reader.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the data files of the configurator are read with a YAML library and the hand-written reader is gone
- [ ] #2 Check: the tests of the configurator still pass, with their companions
<!-- AC:END -->

## Brief

Task: TASK-72, Read the configurator's data files with a YAML library. Role: implementer.

### Read first

- `engine/configure/checks.py` and `pyproject.toml` (read it again before an edit).

### Load these skills

- anima-adopting-a-component, anima-tech-mise, anima-configuration-design

### Own these paths

- engine/configure/**
- tests/configure/**
- pyproject.toml

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the data files of the configurator are read with a YAML library and the hand-written reader is gone
- Check: the tests of the configurator still pass, with their companions

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
