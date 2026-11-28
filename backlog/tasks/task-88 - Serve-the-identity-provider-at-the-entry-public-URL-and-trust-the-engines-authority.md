---
id: TASK-88
title: >-
  Serve the identity provider at the entry's public URL and trust the engine's
  authority
status: Done
assignee: []
created_date: '2026-11-28T10:05:38Z'
updated_date: '2026-11-28T17:07:49Z'
labels:
  - engine
  - entry
  - access
dependencies:
  - TASK-86
  - TASK-87
ordinal: 88000
gaps: []
fork: none
role: implementer
owns:
  - config/**
  - engine/entry/**
  - engine/access/**
  - engine/database/**
  - tests/system/**
  - skills/anima-tech-postgresql-oauth.md
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Switch the example installation's public URL to https://localhost:8443 (the entry's), derived from the one parameter everywhere it is repeated; the tests and the token validator trust the engine's certificate authority. Unverified: whether the token validator honours a certificate-authority file; that is the first check of this task, run before anything is built, and the answer goes into anima-tech-postgresql-oauth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: first, whether the token validator accepts the issuer's certificate when given the engine authority's certificate file; the answer is recorded in anima-tech-postgresql-oauth, and if it does not, a gap and a decision are reported before going on
- [x] #2 Check: the public URL of the example installation is https://localhost:8443 and no other file repeats it; the issuer of a token is that URL
- [x] #3 Check: the existing token tests of tests/system/ pass over the entry with the engine authority trusted
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Partly done by TASK-86 (2026-11-28), because the entry could not be tested otherwise: the engine publishes the entry's port 8443 and no longer 8080 (tests/system/conftest.py, mise-tasks/engine/up); the identity provider listens on the loopback only and runs with --proxy-headers=forwarded; the token tests that a person's browser would make (discovery, device flow, issuer by several names) go through the entry over TLS, trusting the engine's authority read from /run/anima/entrytls/ca.crt inside the engine (tests/system/test_tokens.py, class Provider). The tests that need the master realm or the administration interface go over the loopback from inside the engine (class Inside), because the entry refuses both. NOT done and still this task's: the public URL is still http://localhost:8080 (engine/access/public-url.env, the issuer of every token is http://localhost:8080/realms/anima), and the database server's token validator still fetches the discovery document and the keys over plain HTTP on the loopback, so it trusts no certificate authority: acceptance #1 (does the validator honour a CA file over https) is NOT answered by TASK-86's run and nothing was kept from it; switch the public URL to https://localhost:8443 from the one parameter, make the validator fetch over the entry, and record the answer in anima-tech-postgresql-oauth.

Done (2026-11-28, second part): the public URL is https://localhost:8443, declared only in engine/access/public-url.env (R183); the validator cannot take a CA file (GAP-061, TASK-97), so it reads the identity provider over the pod's loopback (R182): pg_oidc_validator.discovery_url_override rendered next to the access rules, and the provider runs with --hostname-backchannel-dynamic=true. Remains for TASK-87: the certificate role of its own with the public host, renewal and pickup. For adopters (no adopter guide exists yet; the guide is a separate pending decision, to be taken in TASK-89's place): a person who logs in with the device flow needs the engine authority's certificate in the system trust store, or a publicly trusted certificate on the entry, because libpq reads only the system store (its CA-file variable works only in the unsafe debug mode); see anima-tech-postgresql-oauth rule 22.
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-88, Serve the identity provider at the entry's public URL and trust the engine's authority. Role: implementer.

### Read first

- `docs/adr/0008-the-http-entry-point-of-the-engine.md` and `anima-tech-postgresql-oauth`
- `tests/system/test_tokens.py` and `config/profiles/local/`

### Load these skills

- anima-tech-postgresql-oauth, anima-access-design, anima-tech-keycloak, anima-configuration-design, anima-specifying-requirements

### Own these paths

- config/**
- engine/entry/**
- engine/access/**
- engine/database/**
- tests/system/**
- skills/anima-tech-postgresql-oauth.md

### Do not touch

- third_party/** (a change to the validator is written for upstream first, `anima-maintaining-a-fork`), generated files, lock files; do not weaken a check

### Acceptance

- Check: first, whether the token validator accepts the issuer's certificate when given the engine authority's certificate file; the answer is recorded in anima-tech-postgresql-oauth, and if it does not, a gap and a decision are reported before going on
- Check: the public URL of the example installation is https://localhost:8443 and no other file repeats it; the issuer of a token is that URL
- Check: the existing token tests of tests/system/ pass over the entry with the engine authority trusted

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

Task: TASK-88. Role: implementer. Date: 2026-11-28.

### Done

- Acceptance 1 (the unknown, first): the validator cannot be given a CA file. Read in the pinned source, then settled by test: `src/http_client.cpp` sets no CA option and has no setting for one; a run with the public https issuer and nothing else failed every token login. The founder decided the internal channel; the long-run remedy is GAP-061 with TASK-97 (a `ca_file` setting for the validator's fork). Recorded in `skills/anima-tech-postgresql-oauth.md` rules 20 to 22.
- Acceptance 2: `engine/access/public-url.env` is `https://localhost:8443` and the only place that states it; `mise-tasks/engine/build` and `engine/configure/proof/pod.sh` read it instead of repeating a default; the host in `engine/configure/proof/scenarios.sh` is derived; `tests/system/conftest.py` reads it and `tests/system/test_tokens.py` derives `ISSUER` and the public host from it. R183 (`tests/repository/test_repository.py`, with companion) fails a repeat in `engine/`, `config/`, `mise-tasks/` or `tests/system/`.
- The internal channel (R182): `engine/configure/rendering/access-rules.tf` renders `validator_settings` (`pg_oidc_validator.discovery_url_override = 'http://127.0.0.1:8080/realms/anima'`) next to the access rules into `.cache/configure/validator.conf` (`mise-tasks/engine/configure-render`), copied into the database image (`engine/database/Containerfile`, tag input in `mise-tasks/engine/build`) and included by `engine/database/postgresql.conf`; `engine/access/access.container` runs the provider with `--hostname-backchannel-dynamic=true`. Test `test_R182_token_validator_reaches_provider_over_loopback` (also with the entry stopped), companion `test_R182_..._detects_violation`, logic `internal_channel_faults` in `tests/system/engine_logic.py`.
- Acceptance 3: the token tests pass over the entry over TLS with the engine's authority trusted (read from inside the engine). Removed because https made it unneeded: `PGOAUTHDEBUG=UNSAFE` in the client, the `Host:` headers of `Provider` and `Inside` (production mode keeps the issuer whatever the name, R116: the R116 test still sends three names), the `cookie.secure = False` workaround.
- R116 still holds with the flag: the issuer and tokens' `iss` stay the public URL; back-channel URLs follow the request and are used only inside the pod; written in `anima-tech-keycloak` rules 1 and 14 and `anima-access-design` rule 22.
- For adopters: no adopter documentation exists; the text is in `anima-tech-postgresql-oauth` rule 22 and in TASK-89's notes.
- Not done here, TASK-87: the entry's certificate naming the public host through a role of its own.

### Ran

- First test (rule 19), written before anything was built. Run 1 (declaration changed to https, the build still rendering the old default URL from `mise-tasks/engine/build`): `test_R2` failed with `OAuth discovery URI "http://localhost:8080/…" must use HTTPS`: a repeat of the URL, found and removed. Run 2 (the build reads the declaration, no override): `test_R2` failed, "OAuth bearer authentication failed" (the validator cannot trust the entry's certificate, as read). Run 3 (override, no flag): `test_R2` failed and `test_R182` showed the document's `jwks_uri` was `https://localhost:8443/realms/anima/protocol/openid-connect/certs`, the public address (companion evidence; it stays as the pure companion `test_R182_..._detects_violation`, not as a slow engine test). Run 4 (override and flag): `test_R2`, `test_R182`, `test_R116`, `test_R123` passed, a person's device-flow token included.
- `mise run check`: passed (after `mise run format`). `mise run engine:test`: 61 passed in 1817 s.
- The machine was loaded (load average 17): two runs failed to be ready within 180 s (R9's limit, untouched) and one failed at `podman system service did not create its socket`; the next run passed.

### Only read

- That `PGOAUTHCAFILE` is honoured only with `PGOAUTHDEBUG=UNSAFE` (`libpq-oauth/oauth-curl.c` and `doc/src/sgml/libpq.sgml`); a device-flow login by libpq itself against the entry was not run.
- `mise run engine:configure-prove` and the pod of the proof were not run with the changed default URL (the proof's pod now takes the declared URL, the identity provider there runs in development mode).

### Denied commands

- None. One shell command that wrote a task file with a here-document was refused by the sandbox as too complex; I used the edit tool.

### Unknowns resolved

- Does the validator honour a CA file: no (source, then test). The plan changed as the founder decided: internal channel, GAP-061.

### Lessons to write back

- Written in this change: `anima-tech-postgresql-oauth` rules 9, 20 to 22; `anima-tech-keycloak` rules 1 and 14; `anima-access-design` rule 22; GAP-061.

### Root cause and class of each defect met

- The build of the database image had its own default of the public URL (`mise-tasks/engine/build`), so the access rules kept `http://localhost:8080` after the declaration changed. Root cause: the same fact repeated in a task, outside the declaration. Class: a value stated in more than one place (the evidence of TASK-86 named `mise-tasks/engine/build:55` and `engine/configure/proof/pod.sh:18`; the scenarios script held a third copy, of the host). Instance fix: those places read the declaration. The class is closed by R183, which fails a repeat in `engine/`, `config/`, `mise-tasks/` and `tests/system/`. It was not found in `.github/` and `docs/`, which the check does not scan (they state the URL as an example, not as a setting).

### Decisions the brief did not cover

- R182 as a requirement of its own, R183 as a fitness function, GAP-061 and TASK-97; `identity_provider_internal_url` is a variable of the rendering with the provider's loopback address as its default.

### Inconsistencies

- The brief says "the existing token tests pass over the entry"; a test of the first batch (R2) needed the validator's channel to change first, so the order in the brief (check first) holds, and the check's answer was "no".
