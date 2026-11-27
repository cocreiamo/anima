---
id: TASK-19
title: 'GAP-024: Continuity of adrs: one maintainer, a version 0.x project'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
labels:
  - gap
dependencies: []
ordinal: 19000
gaps:
  - GAP-024
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-024 (adrs): The tool is a version 0.x project with one maintainer, so its format checks, its configuration keys and its JSON export may change without notice, and its continuity is not assured.

Impact: The decision records depend on a tool whose governance is thin; `anima-repository-conventions` pins it to an exact version.

The remedy is ours, or a change of what we adopt; the gap stays open until the condition below holds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The tool reaches a stable release with more than one maintainer, or we change the tool; the records stay MADR 4.0.0, a plain format that other tools read.
- [ ] #2 Check: GAP-024 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-19, GAP-024: Continuity of adrs: one maintainer, a version 0.x project. Role: implementer.

### Read first

- `gaps.toml` entry GAP-024, and the skill of the component.

### Load these skills

- anima-tech-adrs-madr, anima-writing-a-decision-record

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The tool reaches a stable release with more than one maintainer, or we change the tool; the records stay MADR 4.0.0, a plain format that other tools read.
- Check: GAP-024 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
