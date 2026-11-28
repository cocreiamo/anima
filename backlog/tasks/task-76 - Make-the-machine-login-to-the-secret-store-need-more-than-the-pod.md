---
id: TASK-76
title: Make the machine login to the secret store need more than the pod
status: To Do
assignee: []
created_date: '2026-11-27T20:19:47Z'
labels:
  - engine
  - secrets
dependencies: []
ordinal: 76000
gaps: []
fork: none
role: implementer
owns:
  - engine/secrets/**
  - engine/configure/**
  - docs/adr/0003-secret-management.md
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A unit logs in to the secret store by a role of its machine authentication that holds no second factor, so any local process in the pod can obtain what the role allows. Decided by the rule for the register: it is our own design choice, not a defect of the secret store, so it is a task and a stated limit of ADR 0003 (guardrails stop accidents, not a determined owner). Decide whether a second factor, or a narrower role, is worth its cost.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the decision is written in ADR 0003 and the roles of the machine authentication are as narrow as it says
- [ ] #2 Check: a test shows a process without the factor refused, if one is chosen
<!-- AC:END -->

## Brief

Task: TASK-76, Make the machine login to the secret store need more than the pod. Role: implementer.

### Read first

- ADR 0003 and the stanzas of the machine authentication in `engine/secrets/` and `engine/configure/secret-store-bootstrap.hcl`.

### Load these skills

- anima-secrets-design, anima-tech-openbao, anima-writing-a-decision-record

### Own these paths

- engine/secrets/**
- engine/configure/**
- docs/adr/0003-secret-management.md
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the decision is written in ADR 0003 and the roles of the machine authentication are as narrow as it says
- Check: a test shows a process without the factor refused, if one is chosen

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
