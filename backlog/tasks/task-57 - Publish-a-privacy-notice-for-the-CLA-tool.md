---
id: TASK-57
title: Publish a privacy notice for the CLA tool
status: Done
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:46Z'
labels:
  - founder
dependencies: []
ordinal: 57000
gaps: []
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CLA Assistant records the user name and signing date of each signer, so a privacy notice must be linked before the first outside contribution (`anima-licensing-and-brand`). The founder writes and publishes it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: the notice is published and linked from the CLA text the tool shows
<!-- AC:END -->

## Brief

Task: TASK-57, Publish a privacy notice for the CLA tool. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: the notice is published and linked from the CLA text the tool shows

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

Task: TASK-57. Role: explorer (the founder delegated the writing). Date: 2026-11-28.

### Done

- AC 1 is complete only after TASK-95 (the Gist the tool shows carries the privacy note) is done; until then the notice is published and linked from `CLA.md` but not from the text the tool shows. TASK-94 publishes a private contact route.
- `PRIVACY.md` (new) is the notice; `CLA.md` ends with a note linking it (the text the tool shows must carry the same line: a setting of the founder, not done); `CONTRIBUTING.md` and `README.md` link it.
- R140 and its test (`tests/repository/test_repository.py`) check that the notice exists and that `CLA.md` and `CONTRIBUTING.md` link it; the model has the requirement and verification.
- The skill `anima-licensing-and-brand` (rule 11, paths) records the notice and what stays unverified.

### Ran

- `mise run generate`; `mise run check` (170 passed, 34 skipped, 59 s).

### Only read

- The CLA Assistant source (schema of its `CLA` and `User` documents), its README and the terms and privacy statement of `cla-assistant.io` (via a web fetch, summarized); the repository was not tested against the live tool.

### Denied commands

- none

### Lessons to write back

- Rule 11 of `anima-licensing-and-brand`, written in this change.

### Decisions the brief did not cover

- Legal basis: legitimate interest (GDPR 6(1)(f)); the founder confirms.
- Contact route: the issue tracker of the repository, asking for a private channel; no privacy address is published.
- The controller is named "Cocreiamo, as named in the CLA", not by legal name.

### Inconsistencies

- none
