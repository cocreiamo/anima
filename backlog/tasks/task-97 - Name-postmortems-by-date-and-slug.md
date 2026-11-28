---
id: TASK-97
title: Name postmortems by date and slug
status: To Do
assignee: []
created_date: '2026-11-28T18:04:02Z'
labels:
  - process
dependencies: []
ordinal: 97000
gaps: []
fork: none
role: implementer
owns:
  - docs/postmortems/**
  - skills/anima-working-as-an-agent.md
  - tests/repository/test_work.py
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Postmortems are numbered by taking the next free number, which collides between branches (PM-014 was claimed three times). Name them PM-<date>-<slug> from now on, keep the existing numbers, and make the template, the guards, the catalogue and the skills say so. The shape check already accepts both forms.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the postmortem template and skill name the form PM-<date>-<slug> and every check accepts both forms
<!-- AC:END -->

## Brief

Task: see the description. Role: implementer. Read `skills/anima-working-as-an-agent.md` (rule 20) and `skills/anima-specifying-requirements.md` first; the founder approved on 2026-11-28 that new identifiers are names, never the next number, and that existing numbers are kept.

## Report

(`docs/work/handback-template.md`, when done)
