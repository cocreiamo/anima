---
id: TASK-88
title: >-
  Serve the identity provider at the entry's public URL and trust the engine's
  authority
status: To Do
assignee: []
created_date: '2026-11-28T10:05:38Z'
updated_date: '2026-11-28T12:54:08Z'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Partly done by TASK-86 (2026-11-28), because the entry could not be tested otherwise: the engine publishes the entry's port 8443 and no longer 8080 (tests/system/conftest.py, mise-tasks/engine/up); the identity provider listens on the loopback only and runs with --proxy-headers=forwarded; the token tests that a person's browser would make (discovery, device flow, issuer by several names) go through the entry over TLS, trusting the engine's authority read from /run/anima/entrytls/ca.crt inside the engine (tests/system/test_tokens.py, class Provider). The tests that need the master realm or the administration interface go over the loopback from inside the engine (class Inside), because the entry refuses both. NOT done and still this task's: the public URL is still http://localhost:8080 (engine/access/public-url.env, the issuer of every token is http://localhost:8080/realms/anima), and the database server's token validator still fetches the discovery document and the keys over plain HTTP on the loopback, so it trusts no certificate authority: acceptance #1 (does the validator honour a CA file over https) is NOT answered by TASK-86's run and nothing was kept from it; switch the public URL to https://localhost:8443 from the one parameter, make the validator fetch over the entry, and record the answer in anima-tech-postgresql-oauth.
<!-- SECTION:NOTES:END -->

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
