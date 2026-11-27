---
id: TASK-64
title: >-
  Move the skills that can be shared, the roles and the scope anima skills to
  the shared repository
status: To Do
assignee: []
created_date: '2026-11-27T18:38:16Z'
updated_date: '2026-11-27T19:02:00Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 64000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
  - skills/**
  - agents/**
  - AGENTS.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The skills that can be shared are rewritten in general form and move to the shared repository, in one folder for the organization divided by scope: homes are named by role (not by path), examples are dated, attributed evidence, and no live identifier (a name, a number, an address) remains. The skills of scope anima and the roles move too; the product repository is rewired to consume them from the pinned submodule. Why: skills and roles are the organization's way of working, and every repository needs the same ones.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the skills of the organization live in one folder of the shared repository, divided by scope, and the roles live there too
- [ ] #2 Check: the product repository reads its skills and roles from the pinned submodule and its routing, generated files and checks still pass
<!-- AC:END -->

## Brief

Task: TASK-64, Move the skills that can be shared, the roles and the scope anima skills to the shared repository. Role: implementer.

### Read first

- `skills/README.md`, `AGENTS.md`, `agents/`, `mise-tasks/generate/agent_layer.py` and `tests/repository/test_agent_layer.py` of this repository
- TASK-62 (the common structure) and TASK-63 (the tooling that generates the routing)

### Load these skills

- anima-working-as-an-agent, anima-repository-conventions

### Own these paths

- shared/**, skills/**, agents/**, AGENTS.md

### Do not touch

- `engine/**`, `config/**`, `tests/system/**`, generated files, lock files, `third_party/`

### Acceptance

- Check: the skills of the organization live in one folder of the shared repository, divided by scope, and the roles live there too
- Check: the product repository reads its skills and roles from the pinned submodule and its routing, generated files and checks still pass

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
