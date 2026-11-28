---
id: TASK-45
title: Write the tests of identities and configuration
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
updated_date: '2026-11-27T18:56:07Z'
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
The verifications about the declaration of identities of two kinds (people and applications), the refusal of a configuration without an administrator, an identity or a client that is not declared never holding the scope of a role, the configuration read at every start (defaults, profiles, no adapter named), one adapter active per port, no credential written in a file and an identity receiving a message with a link to set its credential. The tests of the refusal of an invalid configuration and of an absent setting taking its default are written already.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R6_identities_declared
- [ ] #2 test_R14_identities_reapplied
- [ ] #3 test_R22_roles_declared_with_identities
- [ ] #4 test_R39_each_fact_declared_once
- [ ] #5 test_R49_configuration_names_no_adapter
- [ ] #6 test_R59_one_adapter_active_per_port
- [ ] #7 test_R65_every_setting_has_production_default
- [ ] #8 test_R66_profile_differs_only_in_selection_and_data
- [ ] #9 test_R96_declared_identity_receives_credential_link
- [ ] #10 test_R63_declared_identity_credential_never_in_file
- [ ] #11 test_R100_configuration_without_administrator_refused
- [ ] #12 test_R101_undeclared_identity_never_holds_role_scope
- [ ] #13 test_R102_undeclared_client_gets_no_role_scope
<!-- AC:END -->

## Brief

Task: TASK-45, Write the tests of identities and configuration. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-configuration-design, anima-access-design, anima-tech-opentofu, anima-specifying-requirements

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
- test_R49_configuration_names_no_adapter
- test_R59_one_adapter_active_per_port
- test_R65_every_setting_has_production_default
- test_R66_profile_differs_only_in_selection_and_data
- test_R96_declared_identity_receives_credential_link
- test_R63_declared_identity_credential_never_in_file
- test_R100_configuration_without_administrator_refused
- test_R101_undeclared_identity_never_holds_role_scope
- test_R102_undeclared_client_gets_no_role_scope

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
