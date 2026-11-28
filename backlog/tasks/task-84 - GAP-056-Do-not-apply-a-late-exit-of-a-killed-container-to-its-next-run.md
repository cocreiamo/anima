---
id: TASK-84
title: 'GAP-056: Do not apply a late exit of a killed container to its next run'
status: To Do
assignee: []
created_date: '2026-11-28T12:00:00Z'
labels:
  - upstream
dependencies: []
ordinal: 84000
gaps:
  - GAP-056
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-056 (podman): after a kill whose wait for the exit file times out, podman reports the container stopped before the previous run has finished, and a start issued then is undone by the late exit.

Impact: a start right after a kill can be lost (R42).

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: make podman wait wait for health is fixed upstream or settled by the engine
- [ ] #2 Check: GAP-056 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-84, GAP-056: Do not apply a late exit of a killed container to its next run. Role: implementer.

### Read first

- `gaps.toml` entry GAP-056.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-tech-testcontainers-podman

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the project is changed in its own repository, not here

### Acceptance

- Check: make podman wait wait for health is fixed upstream or settled by the engine
- Check: GAP-056 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
