---
id: TASK-18
title: 'GAP-023: A status column and a stale-index check in adrs'
status: To Do
assignee: []
created_date: '2026-11-27T18:18:40Z'
labels:
  - upstream
dependencies: []
ordinal: 18000
gaps:
  - GAP-023
fork: none
role: implementer
owns:
  - gaps.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GAP-023 (adrs): The tool generates a table of contents with no status, and has no mode that fails when a generated index is stale.

Impact: The ADR index needs glue of ours: `adrs export json` filtered with `jq`, and the generate:check of this repository to detect a stale index (`anima-repository-conventions`).

The remedy is a contribution upstream; no fork of ours exists for this project, so it is prepared against upstream directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: The tool's table of contents carries the status of each record and a check mode fails on a stale index; to be proposed upstream.
- [ ] #2 Check: GAP-023 is updated in gaps.toml (status, upstream link)
<!-- AC:END -->

## Brief

Task: TASK-18, GAP-023: A status column and a stale-index check in adrs. Role: implementer.

### Read first

- `gaps.toml` entry GAP-023, and the skill of the component.

### Load these skills

- anima-tech-adrs-madr, anima-writing-a-decision-record

### Own these paths

- gaps.toml

### Do not touch

- third_party/**; the code of the fork is changed in the fork's own repository, not here

### Acceptance

- Check: The tool's table of contents carries the status of each record and a check mode fails on a stale index; to be proposed upstream.
- Check: GAP-023 is updated in gaps.toml (status, upstream link)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
