---
id: TASK-89
title: >-
  Supply the entry's certificate by one parameter and export the engine
  authority's certificate
status: To Do
assignee: []
created_date: '2026-11-28T10:05:38Z'
labels:
  - engine
  - entry
  - secrets
dependencies:
  - TASK-87
ordinal: 89000
gaps: []
fork: none
role: implementer
owns:
  - engine/entry/**
  - config/entry/**
  - engine/secrets/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
An adopter chooses between the engine's certificate and a certificate of their own, for a name the world reaches, by one installation parameter of config/entry/; the supplied certificate and key arrive as files of a supplied secret (R103). A client can obtain the engine authority's certificate with no credential. Whether one listener must serve an internal and a public name at once (SNI) is open in ADR 0008: do not decide it here.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R133_supplied_certificate_selected_by_one_parameter
- [ ] #2 test_R134_engine_authority_certificate_obtainable
- [ ] #3 Check: the way a client obtains the authority's certificate is a recommendation reported to the founder before it is built (a file the adopter can read, not a fetch over the channel it is meant to secure)
<!-- AC:END -->

## Brief

Task: TASK-89, Supply the entry's certificate by one parameter and export the engine authority's certificate. Role: implementer.

### Read first

- `docs/adr/0008-the-http-entry-point-of-the-engine.md`, R103, R133, R134
- `anima-secrets-design` and `anima-configuration-design`

### Load these skills

- anima-secrets-design, anima-configuration-design, anima-image-design, anima-specifying-requirements

### Own these paths

- engine/entry/**
- config/entry/**
- engine/secrets/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files

### Acceptance

- test_R133_supplied_certificate_selected_by_one_parameter
- test_R134_engine_authority_certificate_obtainable
- Check: the way a client obtains the authority's certificate is a recommendation reported to the founder before it is built (a file the adopter can read, not a fetch over the channel it is meant to secure)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
