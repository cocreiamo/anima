---
id: TASK-75
title: Renew the database server's certificate
status: To Do
assignee: []
created_date: '2026-11-27T20:19:47Z'
labels:
  - engine
  - secrets
dependencies: []
ordinal: 75000
gaps: []
fork: none
role: implementer
owns:
  - engine/**
  - mise-tasks/engine/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The database server's certificate is requested once, at start, from the secret store's authority and TLS is turned on by a reload. Nothing renews it before it expires. Decide the lifetime, the renewal and the reload, and say who restarts what.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the certificate is renewed before it expires and the server reloads it with no restart
- [ ] #2 Check: a renewal that fails leaves the engine not ready and says so
<!-- AC:END -->

## Brief

Task: TASK-75, Renew the database server's certificate. Role: implementer.

### Read first

- `engine/database/tls-enable` and `anima-secrets-design`.

### Load these skills

- anima-secrets-design, anima-tech-postgresql-oauth, anima-image-design, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/**
- mise-tasks/engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the certificate is renewed before it expires and the server reloads it with no restart
- Check: a renewal that fails leaves the engine not ready and says so

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
