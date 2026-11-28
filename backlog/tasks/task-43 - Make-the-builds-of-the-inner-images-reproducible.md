---
id: TASK-43
title: Make the builds of the inner images reproducible
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
updated_date: '2026-11-27T18:55:54Z'
labels:
  - engine
  - build
dependencies: []
ordinal: 43000
fork: none
role: implementer
gaps: []
owns:
  - engine/**
  - mise-tasks/engine/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The database server's image installs distribution packages at build time with no snapshot pin, and the identity provider's build downloads from the Java and JavaScript package registries. The same pinned sources do not produce the same image bit for bit, so building again cannot check what was promoted. This is a defect of our own builds, not of something adopted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R47_builds_reproducible
- [ ] #2 Check: distribution packages are taken from a dated snapshot and build-time downloads are pinned or vendored
<!-- AC:END -->

## Brief

Task: TASK-43, Make the builds of the inner images reproducible. Role: implementer.

### Read first

- The container files under `engine/`, `components.toml` and `anima-branching-and-releasing` rule 6.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design, anima-branching-and-releasing, anima-specifying-requirements

### Own these paths

- engine/**
- mise-tasks/engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R47_builds_reproducible
- Check: distribution packages are taken from a dated snapshot and build-time downloads are pinned or vendored

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
