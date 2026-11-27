---
id: TASK-45
title: Write the tests of identities and configuration
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
labels:
  - pending-tests
dependencies: []
ordinal: 45000
gaps: []
fork: none
role: implementer
owns:
  - config/**
  - engine/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about the declaration of identities, the configuration read at every start (defaults, profiles, unknown settings, no secret in a file), the configuration naming no adapter, one adapter active per port, and an identity receiving a message with a link to set its credential. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R6_identities_declared
- [ ] #2 test_R14_identities_reapplied
- [ ] #3 test_R22_roles_declared_with_identities
- [ ] #4 test_R39_each_fact_declared_once
- [ ] #5 test_R48_configuration_validated_before_ready
- [ ] #6 test_R49_configuration_names_no_adapter
- [ ] #7 test_R59_one_adapter_active_per_port
- [ ] #8 test_R63_declared_identity_can_set_its_credential
- [ ] #9 test_R65_every_setting_has_production_default
- [ ] #10 test_R66_profile_differs_only_in_selection_and_data
- [ ] #11 test_R95_absent_setting_takes_production_default
- [ ] #12 test_R96_declared_identity_receives_credential_link
<!-- AC:END -->

## Brief

Task: TASK-45, Write the tests of identities and configuration. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-configuration-design, anima-access-design, anima-tech-opentofu

### Own these paths

- config/**
- engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R6_identities_declared
- test_R14_identities_reapplied
- test_R22_roles_declared_with_identities
- test_R39_each_fact_declared_once
- test_R48_configuration_validated_before_ready
- test_R49_configuration_names_no_adapter
- test_R59_one_adapter_active_per_port
- test_R63_declared_identity_can_set_its_credential
- test_R65_every_setting_has_production_default
- test_R66_profile_differs_only_in_selection_and_data
- test_R95_absent_setting_takes_production_default
- test_R96_declared_identity_receives_credential_link

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
