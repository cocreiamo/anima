---
id: TASK-90
title: Add the administration console route, off by default
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
ordinal: 90000
gaps: []
fork: none
role: implementer
owns:
  - engine/entry/**
  - config/entry/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The identity provider's administration console is reachable through the entry only when the installation turns a route on by one setting; off by default. The configurator keeps using the administration API from inside the pod and never through the entry.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R130_administration_console_route_off_by_default
- [ ] #2 test_R131_administration_console_route_on_by_configuration
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Nothing of this task is done by TASK-86 (2026-11-28). Findings it must start from: the entry refuses every path under /realms/master/ by the route constraint of its realms route (engine/entry/appsettings.json: /realms/{realm:regex(^(?!master$).+$)}/{**rest}), and has no route for /admin/; the administration console lives in the master realm, so turning it on needs routes for both and a way to keep the rest of the master realm refused; the host program also answers 404 to any path with a segment health, metrics, management or q whatever the routes say (Program.cs). The route's flag is configuration of the entry (anima-entry-design).
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-90, Add the administration console route, off by default. Role: implementer.

### Read first

- `docs/adr/0008-the-http-entry-point-of-the-engine.md`, R130, R131
- `anima-tech-keycloak`

### Load these skills

- anima-tech-keycloak, anima-configuration-design, anima-specifying-requirements

### Own these paths

- engine/entry/**
- config/entry/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; the configurator's use of the administration API from inside the pod does not change

### Acceptance

- test_R130_administration_console_route_off_by_default
- test_R131_administration_console_route_on_by_configuration

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
