---
id: TASK-88
title: >-
  Serve the identity provider at the entry's public URL and trust the engine's
  authority
status: To Do
assignee: []
created_date: '2026-11-28T10:05:38Z'
labels:
  - engine
  - entry
  - access
dependencies:
  - TASK-86
  - TASK-87
ordinal: 88000
gaps: []
fork: none
role: implementer
owns:
  - config/**
  - engine/entry/**
  - engine/access/**
  - engine/database/**
  - tests/system/**
  - skills/anima-tech-postgresql-oauth.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Switch the example installation's public URL to https://localhost:8443 (the entry's), derived from the one parameter everywhere it is repeated; the tests and the token validator trust the engine's certificate authority. Unverified: whether the token validator honours a certificate-authority file; that is the first check of this task, run before anything is built, and the answer goes into anima-tech-postgresql-oauth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: first, whether the token validator accepts the issuer's certificate when given the engine authority's certificate file; the answer is recorded in anima-tech-postgresql-oauth, and if it does not, a gap and a decision are reported before going on
- [ ] #2 Check: the public URL of the example installation is https://localhost:8443 and no other file repeats it; the issuer of a token is that URL
- [ ] #3 Check: the existing token tests of tests/system/ pass over the entry with the engine authority trusted
<!-- AC:END -->

## Brief

Task: TASK-88, Serve the identity provider at the entry's public URL and trust the engine's authority. Role: implementer.

### Read first

- `docs/adr/0008-the-http-entry-point-of-the-engine.md` and `anima-tech-postgresql-oauth`
- `tests/system/test_tokens.py` and `config/profiles/local/`

### Load these skills

- anima-tech-postgresql-oauth, anima-access-design, anima-tech-keycloak, anima-configuration-design, anima-specifying-requirements

### Own these paths

- config/**
- engine/entry/**
- engine/access/**
- engine/database/**
- tests/system/**
- skills/anima-tech-postgresql-oauth.md

### Do not touch

- third_party/** (a change to the validator is written for upstream first, `anima-maintaining-a-fork`), generated files, lock files; do not weaken a check

### Acceptance

- Check: first, whether the token validator accepts the issuer's certificate when given the engine authority's certificate file; the answer is recorded in anima-tech-postgresql-oauth, and if it does not, a gap and a decision are reported before going on
- Check: the public URL of the example installation is https://localhost:8443 and no other file repeats it; the issuer of a token is that URL
- Check: the existing token tests of tests/system/ pass over the entry with the engine authority trusted

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
