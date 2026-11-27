---
id: TASK-78
title: Run the identity provider in production mode
status: To Do
assignee: []
created_date: '2026-11-27T20:19:47Z'
labels:
  - engine
dependencies: []
ordinal: 78000
gaps: []
fork: none
role: implementer
owns:
  - engine/access/**
  - engine/configure/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The engine starts the identity provider in its development mode, with a bootstrap administrator. Production mode needs its own database settings, a certificate and no bootstrap administrator left behind.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the identity provider starts in production mode in the engine and the token tests still pass
- [ ] #2 Check: no bootstrap administrator remains after the configurator has run
<!-- AC:END -->

## Brief

Task: TASK-78, Run the identity provider in production mode. Role: implementer.

### Read first

- `engine/access/` and `anima-tech-keycloak`.

### Load these skills

- anima-tech-keycloak, anima-access-design, anima-image-design, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/access/**
- engine/configure/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the identity provider starts in production mode in the engine and the token tests still pass
- Check: no bootstrap administrator remains after the configurator has run

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
