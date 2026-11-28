---
id: TASK-81
title: Have the configurator set the identity provider's outgoing mail
status: To Do
assignee: []
created_date: '2026-11-27T20:19:48Z'
labels:
  - engine
  - access
dependencies: []
ordinal: 81000
gaps: []
fork: none
role: implementer
owns:
  - engine/configure/**
  - tests/configure/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
R96 needs an identity to receive a message with a link at which it sets its credential. The configurator does not yet set the identity provider's outgoing mail to the mail service that the configuration names, so no such message is sent.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R96_declared_identity_receives_credential_link
- [ ] #2 Check: the configurator sets the identity provider's mail settings from the mail configuration
<!-- AC:END -->

## Brief

Task: TASK-81, Have the configurator set the identity provider's outgoing mail. Role: implementer.

### Read first

- R96, `anima-mail-design` and `engine/configure/declarations/identity-provider.tf`.

### Load these skills

- anima-mail-design, anima-access-design, anima-tech-keycloak, anima-tech-opentofu, anima-specifying-requirements

### Own these paths

- engine/configure/**
- tests/configure/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R96_declared_identity_receives_credential_link
- Check: the configurator sets the identity provider's mail settings from the mail configuration

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
