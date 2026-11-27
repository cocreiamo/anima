---
id: PM-003
date: 2026-11-27
title: An exporter wrote a file outside the worktree
class: tool behaviour not known beforehand
status: guarded
guards:
  - kind: test
    ref: test_R90_export_writes_nothing_outside_cache
    added: 2026-11-27
  - kind: detection
    ref: mise-tasks/model/export
    added: 2026-11-27
recurrences: []
---

# PM-003: An exporter wrote a file outside the worktree

## Overview

The model exporter names its output by cutting the input path at the first dot. The worktree's path contains a dotted directory, so the output landed in the main checkout. It was removed.

## What happened

The export was run on a path inside a worktree. The exporter cut the path at the first dot, which is in a directory name, and wrote the JSON beside what was left of the path: in the main checkout, outside the worktree.

## Root causes

The exporter's naming rule (GAP-003) was not known when the first export was run, and nothing checked where an export writes.

## Resolution

The stray file was removed. The export task runs the exporter from the directory that holds a bare file name, so the output lands there whatever the path of the repository; that was in place when this record was written.

## Impact

One file was created in the main checkout, outside the worktree, and removed. Nothing else was changed.

## Timeline

| When       | What                                                                 |
| ---------- | -------------------------------------------------------------------- |
| 2026-11-27 | The file was found in the main checkout and removed.                 |
| 2026-11-27 | The export task already ran from a bare file name; a test was added.    |

## How did we do

Went well: the file was noticed and removed. Did not go well: the defect was found by its effect.

## Guards

- test `test_R90_export_writes_nothing_outside_cache`: the session records the files in the directories above the repository before the model is exported and compares afterwards. It sees a stray file only when the export actually runs, that is on a cold cache (continuous integration, a changed model); on a warm cache it holds trivially.
- detection, `mise-tasks/model/export`: the workaround for GAP-003, a bare file name in a directory of its own.

The status is guarded, not closed by design: the exporter's defect remains (GAP-003) and the workaround is ours.
