---
id: TASK-44
title: Write the tests of token logins and access
status: To Do
assignee: []
created_date: '2026-11-27T18:18:44Z'
updated_date: '2026-11-27T18:55:57Z'
labels:
  - pending-tests
dependencies: []
ordinal: 44000
gaps: []
fork: none
role: implementer
owns:
  - engine/access/**
  - engine/database/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The verifications about logins by token, the refusal of other ways in, the mapping of an identity to a role and the confinement of the identity provider's database. Each test is written with its `_detects_violation` companion where it is a check of the repository.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R2_valid_token_opens_session
- [ ] #2 test_R3_1_tampered_token_rejected
- [ ] #3 test_R3_2_expired_token_rejected
- [ ] #4 test_R3_3_foreign_issuer_token_rejected
- [ ] #5 test_R4_no_password_access
- [ ] #6 test_R5_identity_maps_to_role
- [ ] #7 test_R8_database_server_depends_on_standard_issuer_only
- [ ] #8 test_R27_idp_role_confined_to_its_database
- [ ] #9 test_R31_service_roles_internal_token_roles_by_token
- [ ] #10 test_R32_idp_database_reachable_only_by_its_role
- [ ] #11 test_R33_token_for_other_client_refused
- [ ] #12 test_R34_token_rules_require_scope
- [ ] #13 test_R35_fixed_role_names_reserved
<!-- AC:END -->

## Brief

Task: TASK-44, Write the tests of token logins and access. Role: implementer.

### Read first

- `tests/pending.toml` (generated), the requirements named below in `model/anima.sysml`, and the skill of the capability.

### Load these skills

- anima-access-design, anima-tech-keycloak, anima-tech-postgresql-oauth, anima-tech-testcontainers-podman, anima-specifying-requirements

### Own these paths

- engine/access/**
- engine/database/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R2_valid_token_opens_session
- test_R3_1_tampered_token_rejected
- test_R3_2_expired_token_rejected
- test_R3_3_foreign_issuer_token_rejected
- test_R4_no_password_access
- test_R5_identity_maps_to_role
- test_R8_database_server_depends_on_standard_issuer_only
- test_R27_idp_role_confined_to_its_database
- test_R31_service_roles_internal_token_roles_by_token
- test_R32_idp_database_reachable_only_by_its_role
- test_R33_token_for_other_client_refused
- test_R34_token_rules_require_scope
- test_R35_fixed_role_names_reserved

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
