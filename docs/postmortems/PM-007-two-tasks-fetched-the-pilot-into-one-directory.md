---
id: PM-007
date: 2026-11-27
title: Two tasks fetched the pilot implementation into one directory at once
class: tasks that run in parallel share a file without a guard
status: guarded
guards:
  - kind: test
    ref: test_R108_pilot_fetched_in_one_guarded_place
    added: 2026-11-27
recurrences: []
---

# PM-007: Two tasks fetched the pilot implementation into one directory at once

## Overview

On an empty cache, `mise run check` failed in continuous integration because `model:check` and the model tests each downloaded and unpacked the SysML pilot into the same directory at the same time. The local cache hid it, because the pilot was always already there.

## What happened

The first run of the checks on GitHub failed: `model:check` stopped with `checkdir error: cannot create .../Kernel Libraries: File exists`. The task runner starts `model:check` and `test` together. The tests export the model, and the exporter ran `model:check` itself when the jar was missing, so two scripts unpacked the same archive into the same directory with `unzip -o` at once. On the development machine the cache was warm and neither script fetched. Reproduced afterwards by moving the cache aside and running `mise run check`: the test session failed at setup in every test that reads the model, with the export task exiting 1, and the partly unpacked tree stayed behind.

## Root causes

- Two places held the download-and-unpack logic (`model:check` directly, `model:export` through a call of the first), and neither was safe for a second caller. The rule that tasks under `depends` run as if in parallel existed (`anima-tech-mise`, rule 2) and was applied to the export, not to the fetch.
- Nothing ran the checks from an empty cache before the first run on a clean machine; a warm cache hides every first-run fault.
- A failed or interrupted unpack left a tree without its jar, which the next run took for a cache to fill, not for damage.

## Resolution

One script, `mise-tasks/model/fetch`, is the only place that downloads and unpacks the pilot. It takes a lock (`flock`), downloads to a directory of its own, checks the SHA-256 before it unpacks, unpacks into that directory and renames the tree into place in one step, and is idempotent. `model:check` and `model:export` call it. The library aliases of GAP-002, which `model:export` made on every run, are made once in that script before the rename.

## Impact

The first run of the checks on pull request 1 failed. No data was lost; nothing reached `main`.

## Timeline

| When       | What                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| 2026-11-27 | The first run of the checks on GitHub failed on an empty cache.               |
| 2026-11-27 | Reproduced locally by moving the cache aside; the fetch was made one script.  |
| 2026-11-27 | Requirement R108 and its test added; the rule written into `anima-tech-mise`. |

## How did we do

Went well: the log named the directory and the fault was reproduced on the first try. Did not go well: a local warm cache hid it, and the same class (a shared directory under parallel tasks) had been written down for the export only.

## Guards

- test `test_R108_pilot_fetched_in_one_guarded_place` (requirement R108, with its `_detects_violation` companion): reads the scripts to show that the download exists in one place and holds the lock, the temporary directory, the checksum before the unpack and the atomic rename; and starts eight fetches at once on an empty cache with the download replaced by a stand-in, without the network, and shows that all succeed and leave one complete tree. It does not prove that the real archive unpacks, nor that a future second caller outside `mise-tasks/` is safe, and a race that does not show in eight callers is not excluded; the lock and the rename are the protection, the test is the evidence.

The status is guarded: the fault was not a failure of judgement but of a missing guard, and a check now stops it.
