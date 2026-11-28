---
id: TASK-53
title: Create an organization GitHub App to restrict main-green
status: To Do
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:45Z'
updated_date: '2026-11-28T17:35:27Z'
labels:
  - founder
dependencies: []
ordinal: 53000
gaps:
  - GAP-008
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The GitHub Actions app cannot be a bypass actor, so main-green cannot be restricted to the Promote workflow. An organization GitHub App that the workflow acts as can be one. The founder creates the app and applies the ruleset.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: only the Promote workflow can push to main-green and the ruleset says so
- [ ] #2 Check: GAP-008 is closed in gaps.toml
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-28: promote.yml makes an installation token of the App cocreiamo-promote (contents write, installed on this repository) in the promote job only, and promote:green and promote:release use it; the job's own token is contents read (R195, R171). Remains: the founder stores PROMOTE_APP_ID and PROMOTE_APP_PRIVATE_KEY (not present when read on 2026-11-28); after the first real Promote run that pushes main-green with the token, the platform adds 'restrict updates' to the main-green ruleset with the promote App as the only bypass actor (never before: it would break Promote), and GAP-008 is closed.
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-53, Create an organization GitHub App to restrict main-green. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: only the Promote workflow can push to main-green and the ruleset says so
- Check: GAP-008 is closed in gaps.toml

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
