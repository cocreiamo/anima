---
id: TASK-99
title: >-
  Name the founder's decisions and learnings by date and slug, and check how
  adrs and backlog number
status: To Do
assignee: []
created_date: '2026-11-28T18:04:03Z'
labels:
  - process
dependencies: []
ordinal: 99000
gaps: []
fork: none
role: implementer
owns:
  - docs/adr/**
  - backlog/**
  - skills/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The founder's decisions and learnings are named by date and slug (the shared standard does this). The two tools that number by themselves, adrs new and backlog task create, take the next number of the working tree; adrs offers renumber to repair a duplicate afterwards, and Backlog.md has check_active_branches and remote_operations (both false here, with effects on id allocation not verified). Decide, with the founder, whether decision records and tasks keep numbers and how a collision between two branches is caught.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a recommendation on numbering of decision records and tasks is brought to the founder, with what each tool offers read from the pinned version
<!-- AC:END -->

## Brief

Task: see the description. Role: implementer. Read `skills/anima-working-as-an-agent.md` (rule 20) and `skills/anima-specifying-requirements.md` first; the founder approved on 2026-11-28 that new identifiers are names, never the next number, and that existing numbers are kept.

## Report

(`docs/work/handback-template.md`, when done)
