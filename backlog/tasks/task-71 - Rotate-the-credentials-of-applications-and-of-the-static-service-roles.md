---
id: TASK-71
title: Rotate the credentials of applications and of the static service roles
status: To Do
assignee: []
created_date: '2026-11-27T19:37:09Z'
labels:
  - engine
  - secrets
dependencies: []
ordinal: 71000
gaps: []
fork: none
role: implementer
owns:
  - engine/configure/**
  - tests/configure/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The credential of an application is derived from the root of trust and set write-only in the identity provider; the static service role of the identity provider is rotated once. Neither is rotated over time, and no test shows a rotation. Rotation of secrets is outside the first release (ADR 0003); this task is the work that follows it: say who reloads what when a credential changes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: a rotation of an application's credential is declared, applied by the configurator and shown by a test, with no secret in the state
- [ ] #2 Check: a rotation of the identity provider's database credential names who restarts what
<!-- AC:END -->

## Brief

Task: TASK-71, Rotate the credentials of applications and of the static service roles. Role: implementer.

### Read first

- ADR 0003, `anima-secrets-design` and `engine/configure/declarations/identities.tf`.

### Load these skills

- anima-secrets-design, anima-tech-opentofu, anima-tech-keycloak, anima-specifying-requirements

### Own these paths

- engine/configure/**
- tests/configure/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: a rotation of an application's credential is declared, applied by the configurator and shown by a test, with no secret in the state
- Check: a rotation of the identity provider's database credential names who restarts what

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
