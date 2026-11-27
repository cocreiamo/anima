---
id: TASK-77
title: Test the login of a person with a token
status: To Do
assignee: []
created_date: '2026-11-27T20:19:47Z'
labels:
  - engine
  - testing
dependencies: []
ordinal: 77000
gaps: []
fork: none
role: implementer
owns:
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Only an application's token login is tested; a person's token needs a browser flow. Write a test that logs a person in through the device flow or a scripted browser, and shows the session as the person's role, the person staying identifiable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a person's token opens a session as the role it holds over TLS, and the audit line names the person
- [ ] #2 test_R2_valid_token_opens_session
<!-- AC:END -->

## Brief

Task: TASK-77, Test the login of a person with a token. Role: implementer.

### Read first

- `tests/system/test_tokens.py` and `anima-access-design`.

### Load these skills

- anima-tech-testcontainers-podman, anima-access-design, anima-specifying-requirements

### Own these paths

- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: a person's token opens a session as the role it holds over TLS, and the audit line names the person
- test_R2_valid_token_opens_session

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
