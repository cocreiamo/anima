---
id: TASK-87
title: Issue, renew and pick up the entry's certificate
status: To Do
assignee: []
created_date: '2026-11-28T10:05:37Z'
labels:
  - engine
  - entry
  - secrets
dependencies:
  - TASK-86
ordinal: 87000
gaps: []
fork: none
role: implementer
owns:
  - engine/entry/**
  - engine/secrets/**
  - engine/image/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HTTP entry point presents a certificate issued by the engine's certificate authority in the secret store, renewed by the same mechanism as the database server's (engine/database/tls-enable, database-tls.container, R118, R119), and takes a renewed one without a restart. The database server's script replaces the key and the certificate as two files one after the other; a reader could load a mismatched pair, so the first test is that the key and the certificate are replaced as one (atomically), before any other work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: first test, written before the implementation: the key and the certificate the entry reads are replaced atomically, so no reader sees a key with another's certificate
- [ ] #2 test_R126_entry_terminates_tls_with_engine_certificate
- [ ] #3 test_R127_entry_takes_renewed_certificate_without_restart
<!-- AC:END -->

## Brief

Task: TASK-87, Issue, renew and pick up the entry's certificate. Role: implementer.

### Read first

- `engine/database/tls-enable`, `engine/database/database-tls.container` and `docs/adr/0008-the-http-entry-point-of-the-engine.md`
- R118, R119, R126, R127 of `model/anima.sysml`

### Load these skills

- anima-secrets-design, anima-image-design, anima-tech-openbao, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/entry/**
- engine/secrets/**
- engine/image/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; the database server's renewal is changed only if the shared mechanism needs it, and then with its tests passing

### Acceptance

- Check: first test, written before the implementation: the key and the certificate the entry reads are replaced atomically, so no reader sees a key with another's certificate
- test_R126_entry_terminates_tls_with_engine_certificate
- test_R127_entry_takes_renewed_certificate_without_restart

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
