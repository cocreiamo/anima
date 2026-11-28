---
id: TASK-87
title: Issue, renew and pick up the entry's certificate
status: Done
assignee: []
created_date: '2026-11-28T10:05:37Z'
updated_date: '2026-11-28T18:52:38Z'
labels:
  - engine
  - entry
  - secrets
dependencies:
  - TASK-86
ordinal: 87000
gaps: []
fork: none
role: implementer
owns:
  - engine/entry/**
  - engine/secrets/**
  - engine/image/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The HTTP entry point presents a certificate issued by the engine's certificate authority in the secret store, renewed by the same mechanism as the database server's (engine/database/tls-enable, database-tls.container, R118, R119), and takes a renewed one without a restart. The database server's script replaces the key and the certificate as two files one after the other; a reader could load a mismatched pair, so the first test is that the key and the certificate are replaced as one (atomically), before any other work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Check: first test, written before the implementation: the key and the certificate the entry reads are replaced atomically, so no reader sees a key with another's certificate
- [x] #2 test_R126_entry_terminates_tls_with_engine_certificate
- [x] #3 test_R127_entry_takes_renewed_certificate_without_restart
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Done by TASK-86 (2026-11-28): the entry has a certificate, issued once per start by engine/entry/entry-certificate (unit entry-certificate.service) through the secret store's existing role of the database server (names localhost and 127.0.0.1, lifetime 720h), into /run/anima/entrytls (server.crt, server.key, ca.crt, owned by the entry's user, 1011). The entry reads it through Kestrel settings in engine/entry/entry.container (Certificate Path and KeyPath). R126 is tested (tests/system/test_entry.py). Remains for this task: a role of its own whose names include the installation's public host, renewal by the mechanism and thresholds of the database server's certificate (R118, R119: a failure is reported by the readiness check), pickup of a renewed certificate without a restart and the pair of files replaced as one (R127, still pending), and the entry's certificate unit then stays up instead of running once.

Done (2026-11-28, TASK-87): the certificate has a role of its own (entry: localhost, 127.0.0.1 and the public host, declared by the configurator from the public URL), is renewed by its own unit with the thresholds of entryCertificateRenewedBeforeExpiry (equal to R118's), and the entry takes it without a restart; key and certificate are ONE PKCS#12 file replaced by a rename. First test: two files can leave the entry on the old certificate (see the report). Not here: the supplied certificate (TASK-89); R134 stays pending.
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-87, Issue, renew and pick up the entry's certificate. Role: implementer.

### Read first

- `engine/database/tls-enable`, `engine/database/database-tls.container` and `docs/adr/0008-the-http-entry-point-of-the-engine.md`
- R118, R119, R126, R127 of `model/anima.sysml`

### Load these skills

- anima-secrets-design, anima-image-design, anima-tech-openbao, anima-tech-podman-quadlet-bootc, anima-specifying-requirements

### Own these paths

- engine/entry/**
- engine/secrets/**
- engine/image/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; the database server's renewal is changed only if the shared mechanism needs it, and then with its tests passing

### Acceptance

- Check: first test, written before the implementation: the key and the certificate the entry reads are replaced atomically, so no reader sees a key with another's certificate
- test_R126_entry_terminates_tls_with_engine_certificate
- test_R127_entry_takes_renewed_certificate_without_restart

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

Task: TASK-87. Role: implementer. Date: 2026-11-28.

### Done

- Acceptance 1 (first test): written and run before the implementation, on the first build (two files, `server.crt` and `server.key`, read by Kestrel). Result: the entry watches the certificate file and not the key file. Replacing the key first and the certificate second was taken; replacing the certificate first and the key second was refused (`crit ... Unable to reload configuration ... The provided key does not match the public key`), the old pair kept being presented, and the later replacement of the key was never taken: the renewal was missed without an outage. No mismatched pair was ever presented (Kestrel refuses it), so the failure is a missed renewal, depending on the order of two writes. Plan chosen from it: ONE file (PKCS#12, `server.pfx`) replaced by a rename (`engine/entry/entry-certificate`). The observation is a pure companion (`pickup_faults`, `test_R127_..._detects_violation`) and a rule of `anima-entry-design` (rule 7), not a slow test.
- Acceptance 2, R126: the certificate names `localhost`, `127.0.0.1` and the host of the public URL, signed through a role of its own, `entry` (`engine/configure/declarations/secret-store.tf`: policy, certificate role, machine login with no secret from the loopback); `test_R126` derives the names from the declaration and checks the file `server.pfx`.
- Acceptance 3, R127: `test_R127_entry_takes_renewed_certificate_without_restart` (`tests/system/test_entry_certificate.py`): an engine with a 180 s lifetime, every connection during the renewal recorded; none failed, the certificate changed, the entry was not restarted, its log has no error.
- entryCertificateRenewedBeforeExpiry (new, with R118's thresholds): `entry-certificate.service` stays up (type notify, `engine/entry/entry-certificate.service`), renews at the share of the lifetime, a failure ends it with "entry certificate renewal failed", it is bound to `anima-ready.target` (`engine/image/anima-ready.target`), and the entry `Wants` it, so the entry keeps serving the certificate in place. Tests: `test_entry_certificate_renewed_before_expiry` (also compares the unit's numbers with the model, and with R118), `test_entry_certificate_renewed_before_expiry_failure_leaves_engine_not_ready` (the secret store's login of the entry is deleted; the engine answers not ready and says so, and the entry still presents the old certificate), with companions.
- The test left unverified by TASK-86: `test_R135_forged_forwarded_header_not_trusted`. A request from an address that is not the loopback cannot be sent (the provider listens on the loopback only, R135's test shows every other address refuses), so it checks the rest of the chain: the provider's arguments trust `127.0.0.1/32` alone, forged `Forwarded` and `X-Forwarded-*` headers sent through the entry changed no address in the provider's answer, and the control (the same forged header sent from the loopback straight to the provider) did change it, so the entry's overwrite is what keeps it out.
- `tokenValidatorReachesProviderOverLoopback` entry-independence moved to an engine of its own (`test_token_validator_reaches_provider_over_loopback_without_the_entry`), because it stops a part and the engine is shared now (R181).

### Ran

- The first test, twice, directly with pytest through mise on the engine image of the first build (key first: new pair taken; certificate first: refused, see above).
- By hand on a debug engine of the new build: `entry-certificate` re-run (`systemctl restart`): the served serial changed, the entry container's start time did not, no `crit` in its log; `server.pfx` with the empty password loaded in Kestrel.
- `mise run engine:test -k` (entry certificate, R126, forged header, R2, tokenValidatorReachesProviderOverLoopback): 11 passed, 1 failed (`test_entry_certificate_renewed_before_expiry`: `model_thresholds` returns a pair since the shared-engine change; fixed). Earlier runs on a machine at load 20 to 25 failed to be ready within R9's 180 s (untouched), six errors in one run.
- `mise run check`: passed. `mise run engine:test`: 77 passed in 3108 s (the machine was loaded; the access image was rebuilt after the merge of main).

### Only read

- That Kestrel watches the certificate file by a directory watcher and takes a rename over it: read in aspnetcore's pull request 49979 by ADR 0008, and observed by the engine test above (the rename was taken).
- The proof of the configurator in its pod (`mise run engine:configure-prove`, scenarios `secret_store_entry_role`, `secret_store_entry_login`) was not run; the configurator's run in the engine applied the new resources (47 added, no error) in the debug engine.

### Denied commands

- None. Polling loops with `sleep` are blocked by a hook; blocking waits were used. A here-document into a shell command was refused as too complex; the edit tool was used.

### Unknowns resolved

- Can two files replaced one after the other be seen mismatched by the entry: not presented, but a renewal can be missed (certificate first); the plan changed from "two files, atomically" to one file, as the brief allows ("whatever the entry's reload behaviour supports").

### Lessons to write back

- Written: `anima-entry-design` rule 7, `anima-secrets-design` rule 14, `anima-tech-keycloak` rule 14.

### Root cause and class of each defect met

- Defect met in the design as written by ADR 0008 and the database server's script: key and certificate replaced as two files. Root cause: a reader that watches one of two files can miss, or half-load, a pair; evidence above. Class: a value spread over several files that a reader must see together. It occurred before in nothing of the repository (the database server reloads from a configuration written last, so it is not the same case). Instance fixed (one file). Class: a rule for any future certificate or secret pair a service reads (supplied certificate, TASK-89): one file or one rename of a directory; recommendation for the founder, a line in `anima-secrets-design`, not written beyond rule 14's mention.

### Decisions the brief did not cover

- entryCertificateRenewedBeforeExpiry as a new requirement, the entry certificate unit bound to the readiness target and ordered after the configurator, and `Wants` instead of `Requires` from the entry; the PKCS#12 file with an empty password in memory (owner-only file, as the key was).

### Inconsistencies

- ADR 0008 (status proposed) still lists the key and certificate as two files and the pickup as unverified; not mine to edit.
