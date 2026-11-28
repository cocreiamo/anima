---
id: TASK-65
title: >-
  Move the record template and the record tool's base configuration to the
  shared repository
status: To Do
assignee: []
created_date: '2026-11-27T18:38:17Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 65000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
  - adrs.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The decision-record template and the base configuration of the record tool move to the shared repository, and the product repository extends them. Why: every repository that records architecture decisions needs the same format.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the record template and the base configuration of the record tool live in the shared repository and the product repository uses them
- [ ] #2 Check: mise run adr:check passes in the product repository
<!-- AC:END -->

## Brief

Task: TASK-65, Move the record template and the record tool's base configuration to the shared repository. Role: implementer.

### Read first

- `adrs.toml`, `docs/adr/` and `skills/anima-tech-adrs-madr.md` of this repository

### Load these skills

- anima-tech-adrs-madr, anima-writing-a-decision-record, anima-repository-conventions

### Own these paths

- shared/**, adrs.toml

### Do not touch

- the decision records themselves, generated files, lock files, `third_party/`

### Acceptance

- Check: the record template and the base configuration of the record tool live in the shared repository and the product repository uses them
- Check: mise run adr:check passes in the product repository

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
