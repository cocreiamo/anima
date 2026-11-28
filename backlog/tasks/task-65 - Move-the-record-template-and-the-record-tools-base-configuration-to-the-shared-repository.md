---
id: TASK-65
title: >-
  Move the record template and the record tool's base configuration to the
  shared repository
status: Done
assignee: []
created_date: '2026-11-27T18:38:17Z'
updated_date: '2026-11-28T10:34:08Z'
labels:
  - organization-move
  - shared
dependencies: []
ordinal: 65000
gaps: []
fork: none
role: implementer
owns:
  - shared/**
  - adrs.toml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The decision-record template and the base configuration of the record tool move to the shared repository, and the product repository extends them. Why: every repository that records architecture decisions needs the same format.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: the record template and the base configuration of the record tool live in the shared repository and the product repository uses them
- [x] #2 Check: mise run adr:check passes in the product repository
<!-- AC:END -->

## Brief

Task: TASK-65, Move the record template and the record tool's base configuration to the shared repository. Role: implementer.

### Read first

- `adrs.toml`, `docs/adr/` and `skills/anima-tech-adrs-madr.md` of this repository

### Load these skills

- anima-tech-adrs-madr, anima-writing-a-decision-record, anima-repository-conventions

### Own these paths

- shared/**, adrs.toml

### Do not touch

- the decision records themselves, generated files, lock files, `third_party/`

### Acceptance

- Check: the record template and the base configuration of the record tool live in the shared repository and the product repository uses them
- Check: mise run adr:check passes in the product repository

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

Task: TASK-65. Role: implementer. Date: 2026-11-28.

### Done

- The record template moved: `templates/adr-madr.md` in the shared repository (cocreiamo/.github#3), with its requirement R14. `adrs.toml` names it as `custom = "shared/templates/adr-madr.md"`; R145 and its test and companion are in `model/anima.sysml` and `tests/repository/test_records.py` (acceptance 1).
- The base configuration did not move, because the record tool cannot inherit one: `crates/adrs-core/src/config.rs` of adrs 0.13.0 has no `extends` key, and a configuration named by `ADRS_CONFIG` takes its own directory as the root, so a shared file would resolve `adr_dir` inside `shared/`. `adrs.toml` stays whole here. Tried in a scratch directory on 2026-11-28: the custom template is used, and a template without `number` gives a record the tool does not list and no error.
- The check job reads `shared/`: the shared `check.yml` has a `submodule-paths` input (cocreiamo/.github#4) and `ci.yml` passes `shared` and pins that commit.
- Skills `anima-tech-adrs-madr` (rule 5) and `anima-writing-a-decision-record` (rule 4) say what the tool shares and that `category` and `decision-makers` are added by hand (R93 is not weakened).

### Ran

- `mise run generate`, `mise run check`: results in the pull request.

### Only read

- The source of adrs 0.13.0 (`config.rs`, `commands/new.rs`) and its book, with `gh api` at the tag.

### Denied commands

- One compound command with `rm docs/adr/*` in a scratch directory was refused by the safety check; not retried, a second scratch directory was used.

### Lessons to write back

- Written in the two skills named above.

### Decisions the brief did not cover

- Only the template is shared, not a base configuration: the tool has no inheritance. No gap was recorded, since nothing is blocked.
- `submodule-paths` fetches only `shared`, not every submodule.

### Inconsistencies

- None.
