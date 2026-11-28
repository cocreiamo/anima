---
id: TASK-98
title: Name gaps by slug
status: To Do
assignee: []
created_date: '2026-11-28T18:04:03Z'
labels:
  - process
dependencies: []
ordinal: 98000
gaps: []
fork: none
role: implementer
owns:
  - gaps.toml
  - tests/repository/**
  - skills/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Gaps are numbered GAP-<nnn> by taking the next free number, which collides between branches. Identify a new gap by a slug, keep the existing numbers as aliases, and make gaps.toml, the workaround references (R25), the tasks that name a gap (R79, R80) and the checks accept both.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a gap without a number can be registered, referenced by a workaround and named by a task, and every check accepts both forms
<!-- AC:END -->

## Brief

Task: see the description. Role: implementer. Read `skills/anima-working-as-an-agent.md` (rule 20) and `skills/anima-specifying-requirements.md` first; the founder approved on 2026-11-28 that new identifiers are names, never the next number, and that existing numbers are kept.

## Report

(`docs/work/handback-template.md`, when done)
