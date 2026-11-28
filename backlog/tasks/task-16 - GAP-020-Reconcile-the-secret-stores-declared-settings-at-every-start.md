---
id: TASK-16
title: 'GAP-020: Reconcile the secret store''s declared settings at every start'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:39Z'
updated_date: '2026-11-27T18:55:55Z'
labels:
  - gap
  - engine
dependencies: []
ordinal: 16000
gaps:
  - GAP-020
fork: none
role: implementer
owns:
  - engine/configure/**
  - tests/configure/**
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-020 (OpenBao): the secret store's self-initialization runs once only, on an empty storage. What it creates (the certificate authority, the seed values, the first machine credential) is not reconciled at later starts. The secret store's policies, engines and roles are converged by the configurator at every start.

The remedy is ours (the configurator, ADR 0006), or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: OpenBao reconciles what its initialization created at every start, or an upgrade that must change it has a declared path (ADR 0006)
- [ ] #2 Check: GAP-020 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-16, Reconcile the secret store's declared settings at every start. Role: implementer.

### Read first

- `gaps.toml` entry GAP-020, and the skill of the component.

### Load these skills

- anima-tech-openbao, anima-secrets-design, anima-configuration-design, anima-tech-opentofu

### Own these paths

- engine/configure/**
- tests/configure/**
- gaps.toml

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: OpenBao reconciles what its initialization created at every start, or an upgrade that must change it has a declared path (ADR 0006)
- Check: GAP-020 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
