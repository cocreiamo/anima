---
id: PM-010
date: 2026-11-28
title: The cache of the inner images was never refreshed and every run on main after the first failed
class: a step verified only by its text and first run
status: guarded
guards:
  - kind: test
    ref: test_R125_cache_of_inner_images_refreshed_when_they_changed
    added: 2026-11-28
  - kind: test
    ref: test_R170_workflow_steps_call_tested_commands
    added: 2026-11-28
recurrences: []
---

# PM-010: The cache of the inner images was never refreshed and every run on main after the first failed

## Overview

The system tests keep the engine's inner images in a cache. On the first push to `main` the cache was saved; on every later push the step that packs the images failed, so `main` was red and the cache never moved on.

## What happened

The workflow restores the cache, loads the archive and builds. When the images had changed, the restored cache was the nearest older one, and the new archive was written by `podman save` to the path where the restored archive still lay. Podman refused (`docker-archive doesn't support modifying existing images`). The failing steps stopped the cache save, so pull requests kept rebuilding what changed since the first save (24 minutes instead of about 10). Runs 46127838141 and 46131055671 show it.

## Root causes

- The archive restored from the cache was left at the path the new archive is written to.
- The check of the workflow read its text and nobody had run the save step a second time; it could only fail on the second push.

## Resolution

The step that loads the restored archive removes it. The save runs only when the exact key of the current inner images is not in the cache (`cache-hit` is true only for an exact match, a cache is immutable, so a new key is needed to store new images), and the cache is saved only when the archive was written.

## Impact

`main` reported red on every push after the first and pull requests ran slower. No release was affected.

## Timeline

| When       | What                                                         |
| ---------- | ------------------------------------------------------------ |
| 2026-11-28 | Two pushes to `main` failed in the save step; cause read.    |
| 2026-11-28 | Restored archive removed; a test of the workflow text added. |

## How did we do

Went well: the log named the refusal. Did not go well: the workflow's first run was taken as proof of its second.

## Guards

- test `test_R125_cache_of_inner_images_refreshed_when_they_changed` (requirement R125, with its `_detects_violation` companion): requires that the restored archive is removed before the new one is written and that restore and save use the key of the inner images and save only on a miss.
- Not protected: that the cache is refreshed is shown only by the first push to `main` after the merge that changes the inner images.
