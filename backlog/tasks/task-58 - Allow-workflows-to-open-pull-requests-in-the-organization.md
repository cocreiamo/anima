---
id: TASK-58
title: Allow workflows to open pull requests in the organization
status: To Do
assignee:
  - '@founder'
created_date: '2026-11-27T18:18:46Z'
updated_date: '2026-11-28T17:35:27Z'
labels:
  - founder
dependencies: []
ordinal: 58000
gaps:
  - GAP-046
fork: none
role: explorer
owns:
  - none (a setting or an action of the founder)
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A repository cannot let GitHub Actions create and approve pull requests until the organization allows it; the release preparation needs it. Only the founder changes the organization setting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Check: the organization allows it and the repository setting is applied by the file that describes the repository
- [ ] #2 Check: GAP-046 is closed in gaps.toml
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-28: prepare-release.yml gives the release tool an installation token of the App cocreiamo-bot (contents and pull requests write) through the token input of the action, so the pull request it opens starts the required checks (R195). Remains: the founder stores BOT_APP_ID and BOT_APP_PRIVATE_KEY (not present when read on 2026-11-28); the first release pull request opened by the bot must be seen running its checks, then the close-and-reopen gesture is dropped from anima-branching-and-releasing rule 13. The organization setting of GAP-046 is not needed by an App token.
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-58, Allow workflows to open pull requests in the organization. Role: explorer.

### Read first

- The skill named in the description.

### Load these skills

- anima-tech-github-governance, anima-repository-conventions

### Own these paths

- none (a setting or an action of the founder)

### Do not touch

- everything: an agent never changes a setting; this task is the founder's own

### Acceptance

- Check: the organization allows it and the repository setting is applied by the file that describes the repository
- Check: GAP-046 is closed in gaps.toml

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
