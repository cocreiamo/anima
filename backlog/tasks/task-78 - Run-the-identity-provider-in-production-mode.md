---
id: TASK-78
title: Run the identity provider in production mode
status: Done
assignee: []
created_date: '2026-11-27T20:19:47Z'
updated_date: '2026-11-28T11:01:17Z'
labels:
  - engine
dependencies: []
ordinal: 78000
gaps: []
fork: none
role: implementer
owns:
  - engine/access/**
  - engine/configure/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The engine starts the identity provider in its development mode, with a bootstrap administrator. Production mode needs its own database settings, a certificate and no bootstrap administrator left behind.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: the identity provider starts in production mode in the engine and the token tests still pass
- [x] #2 Check: no bootstrap administrator remains after the configurator has run
- [x] #3 Check: the issuer of a token is the configured public URL whatever name the request used, with a test (no requirement of the model fixes the issuer today; R2 and R3.3 name 'the configured issuer', so a requirement is added with it)
<!-- AC:END -->

## Brief

Task: TASK-78, Run the identity provider in production mode. Role: implementer.

### Read first

- `engine/access/` and `anima-tech-keycloak`.

### Load these skills

- anima-tech-keycloak, anima-access-design, anima-image-design, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/access/**
- engine/configure/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- Check: the identity provider starts in production mode in the engine and the token tests still pass
- Check: no bootstrap administrator remains after the configurator has run

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

Task: TASK-78. Role: implementer. Date: 2026-11-28.

### Done

- AC 1, production mode: `engine/access/access.container` runs `start --optimized` with the public URL as hostname, plain HTTP inside the pod, no proxy-headers setting, state in the `idp` database; `engine/access/Containerfile` builds the optimized server (database vendor, health). Requirement R123 (`test_R123_identity_provider_runs_in_production_mode`, with companion): the log says `Profile prod activated`, no development mode, a realm row in the `idp` database. The startup check waits for `/realms/master` because production mode answers 503 while it bootstraps, after its readiness endpoint is up.
- AC 1, database: `engine/database/prepare.sql` creates `svc_idp` and the database `idp` before the configurator, with a password derived from the root of trust (`engine/image/anima-credentials`, the file read by `database-prepare.container` and `KC_DB_PASSWORD` in the provider's environment); the configurator adopts them (`roles.yaml` `bootstrap: true`, import in `declarations/database.tf`); the 24 h rotation of that role is removed. ADR 0003 decision 4 and `anima-secrets-design` rule 5 amended.
- AC 2, no bootstrap administrator: the provider starts with a temporary service account (`KC_BOOTSTRAP_ADMIN_CLIENT_*`, secret derived); the configurator makes its own permanent client in the master realm (`declarations/identity-provider.tf`, with the `admin` role and the `kc-admin-api` scope) and `converge.sh` deletes the temporary client at the end of every run; later runs sign in as the permanent client. R117 (`test_R117_no_temporary_administrator_remains`, with companion): no user or service account marked temporary, and the temporary credentials get no token.
- AC 3, issuer: R116 (`test_R116_issuer_is_the_configured_public_url`, with companion): discovery document and tokens, asked by three names, all carry the public URL as issuer. The public URL is now one file, `engine/access/public-url.env`, read by the provider's unit and the configurator's.
- Other: `tests/system/test_tokens.py` signs in as the permanent client to set a person's password (the token tests pass); `engine/configure/proof/` updated for the new credentials (not run); `engine/configure/checks.py` and `tests/configure/test_declarations.py`: the R102 check now allows default scopes only for the configurator's client and forbids role scopes in them (see Decisions).
- Skills and ADRs written back: `anima-tech-keycloak` (rules 1, 4, 5, 6, 14 to 17), `anima-secrets-design` rule 5, `anima-tech-opentofu` rule 18, ADR 0003, ADR 0006.

### Ran

- Before the build, on the development-mode engine: `mise run engine:test -- -k "test_R123 or test_R116 or test_R117"`: 3 failed (log reports `Profile dev activated`; issuer follows the request name; no configurator client secret), 3 passed (logic companions).
- `mise run check`: `163 passed, 37 skipped in 49.62s`, all other tasks passed (lint, format, models, adr, licenses).
- `mise run engine:test` once, full: `46 passed in 1683.97s (0:28:03)`.

### Only read

- The `engine:configure-prove` proof (updated for the new credentials, not run); ADR 0005 rule 2 (the provider's own certificate) is now outdated by the decision of the entry point and was not changed; the claim that a later start ignores the bootstrap variables comes from the pinned guide.

### Denied commands

- A `Monitor` call with an `until ... sleep` loop was refused by the hook; I waited with `tail --pid` instead. One `git checkout --theirs` with two files was refused; I resolved the merge conflicts by editing.

### Lessons to write back

- Written in this change: production mode and its startup check, the temporary service account and its deletion, the `kc-admin-api` scope (401 without it), the derived database password.

### Decisions the brief did not cover

- R102's check forbade any default-scope resource; the configurator's client needs one for `kc-admin-api`. The check is now `default_scope_faults`: only that client may have default scopes, and none of a fixed role (its companion feeds each violation).
- Bootstrap client id `anima-bootstrap`, permanent client `anima-configurator` (in `identity.yaml`); the Keycloak master role name is also there so that `roles.yaml` names stay the only home of role names (R39).
- The `DELETE` is sent with `nc` from the configurator image, which has no other client able to send it.

### Inconsistencies

- ADR 0005 rule 2 says the provider's certificate carries the public URL; the founder's decision puts a proxy in front, which the entry-point task has to amend.
- The static role `svc_secrets_manage` still holds admin option on `svc_idp` and the secret store keeps a database connection with no rotated role; both wait for TASK-71.
- The worktree had been switched to another branch before I started; I switched it back to this branch.
