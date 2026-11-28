---
id: TASK-77
title: Test the login of a person with a token
status: Done
assignee: []
created_date: '2026-11-27T20:19:47Z'
updated_date: '2026-11-28T05:21:27Z'
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
- [x] #1 Check: a person's token opens a session as the role it holds over TLS, and the audit line names the person
- [x] #2 test_R2_valid_token_opens_session
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

Task: TASK-77. Role: implementer. Date: 2026-11-28.

### Done

- `tests/system/test_tokens.py`: `test_R2_valid_token_opens_session` also logs in the person `carol` (role `readwrite`) with a token of the device flow of the engine's client, played by a scripted browser against the published port; the session opens as `readwrite` over TLS, the audit line names `carol` in the same session, and the same token is refused for `admin`. The password is generated at run time through the identity provider's administration interface; none is written in a file.
- `tests/system/engine_logic.py` and `tests/system/test_logic.py`: the form and audit decisions as pure functions, with `test_R2_valid_token_opens_session_detects_violation`.
- `tests/repository/test_fitness.py`: `test_R2_valid_token_opens_session` leaves the exceptions table, since it has a companion.

### Ran

- `mise run engine:test`: 32 passed in 601.12s.
- `mise run check`: 151 passed, 29 skipped.

### Only read

- The identity provider's documentation on the device flow was not read; the flow was observed.

### Denied commands

- none

### Lessons to write back

- Written in this change: `skills/anima-tech-keycloak.md` rules 1 and 12, `skills/anima-access-design.md` rules 20 and 21. TASK-78 carries the check that the issuer is the configured URL.

### Decisions the brief did not cover

- The shipped example person `carol` is used, with a password set at run time; no separate identities fixture.

### Inconsistencies

- The issuer of a token followed the request's Host although a public URL is configured (keycloak rule 1 said otherwise).
