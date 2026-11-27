---
id: TASK-39
title: 'GAP-045: Check plain-text references and the options section in adrs doctor'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - upstream
dependencies: []
ordinal: 39000
gaps:
  - GAP-045
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-045 (adrs): adrs doctor checks neither plain-text references to other records nor the considered-options section.

Impact: A reference written as a bare number is never verified, and a record may omit the options it considered.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The doctor checks plain-text references and the presence of the considered-options section, or a test of ours does.
- [ ] #2 Check: GAP-045 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-39, GAP-045: Check plain-text references and the options section in adrs doctor. Role: implementer.

### Read first

- `gaps.toml` entry GAP-045, and the skill of the component.

### Load these skills

- anima-tech-adrs-madr, anima-writing-a-decision-record

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The doctor checks plain-text references and the presence of the considered-options section, or a test of ours does.
- Check: GAP-045 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
