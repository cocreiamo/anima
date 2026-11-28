---
id: TASK-67
title: Decide how end users query data through a general interface
status: To Do
assignee: []
created_date: '2026-11-27T18:40:33Z'
labels:
  - access
dependencies: []
ordinal: 67000
gaps: []
fork: none
role: spike
owns:
  - none (a decision, if the question is taken up)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Noted from the decision on identities: if end users of an application ever query data through a general interface with their own row-level permissions, the interface holds the database session and tells the database who the user is; end users still do not become database roles. Decide when such an interface is wanted; nothing is built before. Why: the answer must not turn end users into database roles (docs/adr/0004-roles-and-access.md).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a decision about the interface is recorded, or the question is dropped, and no end user is a database role
<!-- AC:END -->

## Brief

Task: TASK-67, Decide how end users query data through a general interface. Role: spike.

### Read first

- `docs/adr/0004-roles-and-access.md` (the three meanings of user, and More Information)
- `skills/anima-access-design.md`

### Load these skills

- anima-access-design, anima-writing-a-decision-record

### Own these paths

- none (a decision, if the question is taken up)

### Do not touch

- `engine/**`, `config/**`, `tests/system/**`, generated files, lock files, `third_party/`

### Acceptance

- Check: a decision about the interface is recorded, or the question is dropped, and no end user is a database role

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

### Decision this serves (spike only)

- Whether end users will ever query data through a general interface with their own row-level permissions, and if so how the session is held; an answer that makes end users database roles is refused.
- Why a test inside the task cannot answer it: the question is whether a general interface is wanted at all, and no implementation exists to test.

## Report

(`docs/work/handback-template.md`, when done)
