---
id: TASK-38
title: 'GAP-044: List a decision record that lacks a number, or report it, in adrs'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
labels:
  - upstream
dependencies: []
ordinal: 38000
gaps:
  - GAP-044
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-044 (adrs): A decision record that lacks its number in the front matter is silently left out of the listings, and no error is shown.

Impact: A converted record can vanish from the index and from the export without any check failing.

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The tool reports a record without a number, or a test of ours counts the files against the listing.
- [ ] #2 Check: GAP-044 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-38, GAP-044: List a decision record that lacks a number, or report it, in adrs. Role: implementer.

### Read first

- `gaps.toml` entry GAP-044, and the skill of the component.

### Load these skills

- anima-tech-adrs-madr, anima-writing-a-decision-record

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The tool reports a record without a number, or a test of ours counts the files against the listing.
- Check: GAP-044 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
