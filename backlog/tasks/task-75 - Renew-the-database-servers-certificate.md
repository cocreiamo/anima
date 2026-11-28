---
id: TASK-75
title: Renew the database server's certificate
status: Done
assignee: []
created_date: '2026-11-27T20:19:47Z'
updated_date: '2026-11-28T06:53:47Z'
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
- [x] #1 Check: the certificate is renewed before it expires and the server reloads it with no restart
- [x] #2 Check: a renewal that fails leaves the engine not ready and says so
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
R118 and R119 added; tls-enable stays up and renews by reload; engine/image/anima-ready reports why the engine is not ready. Tests: test_R118_certificate_renewed_before_expiry, test_R119_failed_renewal_leaves_engine_not_ready.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
R118 and R119 added. tls-enable stays up and renews the certificate by reload at the share of its lifetime set by the thresholds of R118; a failed renewal fails database-tls, so the engine is not ready, and engine/image/anima-ready says why. Unverified: a booted machine; the real default lifetime was never run; the R42 system test failed once in a full run (not ready within its limit) and passed alone and in the next full run.
<!-- SECTION:FINAL_SUMMARY:END -->

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

Task: TASK-75. Role: implementer. Date: 2026-11-28.

### Done

- Acceptance 1: `engine/database/tls-enable` stays up and renews by reload (R118); `engine/database/database-tls.container` carries the thresholds; test `test_R118_certificate_renewed_before_expiry`.
- Acceptance 2: a failed renewal fails `database-tls`, the target leaves active, `engine/image/anima-ready` states the reason (R119); test `test_R119_failed_renewal_leaves_engine_not_ready`.
- Skills: `anima-secrets-design`, `anima-tech-podman-quadlet-bootc`, `anima-image-design`, `anima-tech-postgresql-oauth`.

### Ran

- Both tests failed on the old image for the right reason, then passed on the new one; full `mise run engine:test` 35 passed; `mise run check` green.

### Only read

- Nothing relied on reading alone, except as under Unverified.

### Denied commands

- Removal of three dangling podman volumes left by a test engine: denied; left alone.

### Lessons to write back

- Written: secrets-design rule 14, podman skill rule 20, image-design rule 12.

### Decisions the brief did not cover

- Long-running unit instead of a timer; lifetime and renewal share as thresholds of R118; the health check is the new readiness script.

### Inconsistencies

- Unverified: the booted machine; the real default lifetime was never run; test_R42 failed once in a full run (flake, passed alone and in the next full run).
