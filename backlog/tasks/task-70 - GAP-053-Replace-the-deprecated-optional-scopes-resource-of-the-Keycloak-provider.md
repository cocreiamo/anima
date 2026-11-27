---
id: TASK-70
title: >-
  GAP-053: Replace the deprecated optional-scopes resource of the Keycloak
  provider
status: To Do
assignee: []
created_date: '2026-11-27T19:35:24Z'
labels:
  - gap
  - engine
dependencies: []
ordinal: 70000
gaps:
  - GAP-053
fork: none
role: implementer
owns:
  - engine/configure/**
  - tests/configure/**
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-053 (terraform-provider-keycloak): the resource that sets the optional scopes of a client is deprecated upstream.

Impact: the declarations use a resource that upstream will remove.

The remedy is ours: move the declarations to the resource that replaces it; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the declarations use the resource that replaces the deprecated one, and the pinned provider accepts them
- [ ] #2 Check: GAP-053 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-70, GAP-053: Replace the deprecated optional-scopes resource of the Keycloak provider. Role: implementer.

### Read first

- `gaps.toml` entry GAP-053, and `engine/configure/declarations/`.

### Load these skills

- anima-tech-opentofu, anima-tech-keycloak, anima-configuration-design

### Own these paths

- engine/configure/**
- tests/configure/**
- gaps.toml

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the declarations use the resource that replaces the deprecated one, and the pinned provider accepts them
- Check: GAP-053 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
