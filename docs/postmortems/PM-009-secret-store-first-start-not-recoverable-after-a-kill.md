---
id: PM-009
date: 2026-11-28
title: An abrupt stop during the secret store's first start left an engine that never became ready
class: a requirement taken as met at every moment after a test of one moment
status: guarded
guards:
  - kind: test
    ref: test_R42_abrupt_stop_in_secret_store_first_start_recovers
    added: 2026-11-28
recurrences: []
---

# PM-009: An abrupt stop during the secret store's first start left an engine that never became ready

## Overview

R42 promises that an engine stopped abruptly at any moment reaches readiness with the same start command. The test killed the engine at one moment only, while the database cluster was being created. A kill while the secret store was initialising itself for the first time left storage that the store never repairs, and the engine then never became ready.

## What happened

`test_R42_abrupt_stop_recovers_with_same_start` failed twice in full runs and passed when run alone, which pointed at the test's bound. An investigation read the pinned secret store's source and found that its first start has three windows in which a kill leaves storage it cannot use: the key ring written and the seal configuration not yet (it cannot unseal), the store initialised and its self-initialisation not yet marked as started (it skips the self-initialisation for good and serves without the machine authentication the other parts log in with), and the self-initialisation marked as started and not finished (it refuses to unseal). Polling could not land a kill inside these windows (about a second long), so the test was rebuilt to hold the store's write of a chosen key with a trigger on its storage table and kill there. On the unfixed engine all three kills left an engine that was not ready after 240 s; the database server's certificate unit or the secret store itself had hit its start limit.

## Root causes

- The test exercised one kill moment and the requirement says every moment. The moment chosen was before the secret store started at all.
- The secret store's self-initialisation has no rollback (GAP-015). The workaround recorded for it was a first start "repeatable from an empty state", which assumed someone empties the state; nothing in the engine did.
- The skill said that nothing precious is in the secret store before its first start has succeeded, and the engine did not use that fact to start the store again from empty storage.

## Resolution

Before every start of the secret store (`ExecStartPre` of `secrets.service`), `engine/secrets/first-start.sql` drops and recreates the store's storage database unless the store's first start is recorded as completed. Once the store is healthy, `ExecStartPost` records the completion in the database server (`anima.secret_store_first_start`), so a backup carries the record together with the storage it describes. The secret store's listener starts only after its self-initialisation has returned, so a healthy store whose storage was empty at this start has completed it. Every unit that uses the store orders after `secrets.service`, which is active only after the record is written, so emptying an unrecorded store loses nothing anybody used.

## Impact

An engine killed during that second of its first start would never have become ready, and the adopter would have had to remove its state by hand. No installation exists yet; nothing reached a release.

## Timeline

| When       | What                                                                                    |
| ---------- | --------------------------------------------------------------------------------------- |
| 2026-11-28 | R42's test failed twice in full runs, passed alone; first read as a test defect.        |
| 2026-11-28 | Three windows found in the source; reproduced with a held write; all three not ready.   |
| 2026-11-28 | Storage of an unrecorded first start is emptied before each start; the test is a guard. |

## How did we do

Went well: the source of the adopted store named the mechanism exactly, and holding a write made a one-second window deterministic. Did not go well: two failures were first attributed to load and to the test, and the requirement was called covered by a test of one moment.

## Guards

- test `test_R42_abrupt_stop_in_secret_store_first_start_recovers` (requirement R42, with its `_detects_violation` companion in `tests/system/test_logic.py`): kills the engine at each of the three stages and requires readiness and the completion record after the same start; the companion shows that the stage of the kill is read from the storage keys and that keys of no stage are not taken for one. It failed on the engine before the fix, at all three stages.
- Not protected: a kill during another part's first start that leaves state of a kind no test has looked at. The kill moments that polling reached (cluster creation, the identity provider's and the configurator's first runs) recovered, but polling does not land on a chosen moment.
