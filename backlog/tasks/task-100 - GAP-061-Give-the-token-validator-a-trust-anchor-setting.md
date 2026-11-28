---
id: TASK-100
title: 'GAP-061: Give the token validator a trust-anchor setting'
status: To Do
assignee: []
created_date: '2026-11-28T16:32:55Z'
labels:
  - gap
  - upstream
dependencies: []
ordinal: 100000
gaps:
  - GAP-061
fork: cocreiamo/anima-pg-oidc-validator
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-061 (pg_oidc_validator): the validator has no setting for a certificate authority file; it uses its libcurl's compiled-in system store. Contribute a ca_file setting to the validator's fork, then the database server's validator may fetch the discovery document and keys over the entry again, with the engine authority trusted, and the internal channel (tokenValidatorReachesProviderOverLoopback) becomes an option and not a necessity.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the validator accepts a setting that names a certificate authority file and refuses a provider whose certificate is not issued by it, with a test on the fork
- [ ] #2 Check: GAP-061 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-100, GAP-061: Give the token validator a trust-anchor setting. Role: implementer.

### Read first

- `gaps.toml` entry GAP-061, `anima-tech-postgresql-oauth` and tokenValidatorReachesProviderOverLoopback of `model/anima.sysml`

### Load these skills

- anima-tech-postgresql-oauth, anima-maintaining-a-fork, anima-access-design

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: the validator accepts a setting that names a certificate authority file and refuses a provider whose certificate is not issued by it, with a test on the fork
- Check: GAP-061 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
