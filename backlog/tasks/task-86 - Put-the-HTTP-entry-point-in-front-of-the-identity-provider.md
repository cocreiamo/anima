---
id: TASK-86
title: Put the HTTP entry point in front of the identity provider
status: To Do
assignee: []
created_date: '2026-11-28T10:05:22Z'
labels:
  - engine
  - entry
dependencies:
  - TASK-78
ordinal: 86000
gaps:
  - GAP-057
  - GAP-058
fork: none
role: implementer
owns:
  - engine/entry/**
  - config/entry/**
  - engine/image/**
  - engine/access/**
  - engine/configure/**
  - tests/system/**
  - skills/anima-entry-design.md
  - components.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build engine/entry/ and config/entry/: the host program, its configuration and the unit of the HTTP entry point (ADR 0008), in front of the identity provider, which stops being published. First a failing test for each acceptance line. Depends on TASK-78: the identity provider must run in production mode behind a TLS-terminating proxy (HTTP on the loopback, the Forwarded header trusted from the loopback).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R128_entry_forwards_only_declared_prefixes
- [ ] #2 test_R129_entry_never_forwards_management
- [ ] #3 test_R132_entry_overwrites_forwarded_header
- [ ] #4 test_R135_identity_provider_reachable_only_through_entry
- [ ] #5 Check: a request under /realms/master/ is refused by the entry, by a route to nothing or by code (the library has no deny route; unverified), and the choice is recorded in the entry's skill
- [ ] #6 Check: the skill anima-entry-design exists with the directory, and the base image of the entry's container file and the runtime packages are pinned in components.toml (digest) with GAP-057 named by the build
<!-- AC:END -->

## Brief

Task: TASK-86, Put the HTTP entry point in front of the identity provider. Role: implementer.

### Read first

- `docs/adr/0008-the-http-entry-point-of-the-engine.md`, R126 to R135 of `model/anima.sysml`
- `engine/access/`, `engine/image/anima.pod` and TASK-78 (production mode: its settings behind a TLS-terminating proxy are in `anima-tech-keycloak`)

### Load these skills

- anima-image-design, anima-tech-podman-quadlet-bootc, anima-access-design, anima-tech-keycloak, anima-designing-a-port, anima-adopting-a-component, anima-specifying-requirements

### Own these paths

- engine/entry/**
- config/entry/**
- engine/image/**
- engine/access/**
- engine/configure/**
- tests/system/**
- skills/anima-entry-design.md
- components.toml

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R128_entry_forwards_only_declared_prefixes
- test_R129_entry_never_forwards_management
- test_R132_entry_overwrites_forwarded_header
- test_R135_identity_provider_reachable_only_through_entry
- Check: a request under /realms/master/ is refused by the entry, by a route to nothing or by code (the library has no deny route; unverified), and the choice is recorded in the entry's skill
- Check: the skill anima-entry-design exists with the directory, and the base image of the entry's container file and the runtime packages are pinned in components.toml (digest) with GAP-057 named by the build

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
