---
id: PM-002
date: 2026-11-27
title: A formatter changed a file inside a fork
class: tool run over more files than intended
status: guarded
guards:
  - kind: test
    ref: test_R89_submodule_working_trees_clean
    added: 2026-11-27
  - kind: detection
    ref: .taplo.toml
    added: 2026-11-27
recurrences: []
---

# PM-002: A formatter changed a file inside a fork

## Overview

A TOML formatter run with its default file discovery descended into a submodule under what is now `third_party/` and rewrote one of its files. The change was set aside in a stash inside the submodule.

## What happened

During the setup of this repository the formatter was run over the whole tree. Its default discovery does not stop at a submodule, so it reached a file of a fork and rewrote it.

## Root causes

The formatter's configuration did not limit it to the repository's own files, and nothing checked that the forks stayed untouched.

## Resolution

The change was set aside in a stash inside the submodule, so the fork's working tree was clean again. The formatter's include list names only the repository's own files (`.taplo.toml`), which was in place when this record was written.

## Impact

One file of one fork was changed in a working tree; nothing was committed or pushed.

## Timeline

| When       | What                                                                 |
| ---------- | -------------------------------------------------------------------- |
| 2026-11-27 | The formatter rewrote a file in a fork; the change was set aside.    |
| 2026-11-27 | The include list is limited; a check of the forks' trees was added.  |

## How did we do

Went well: the change was noticed before any commit. Did not go well: no check would have noticed it.

## Guards

- test `test_R89_submodule_working_trees_clean`: after the checks, the working tree of every checked-out fork is clean. It runs in `mise run check`, not inside `mise run format`, so it notices the damage at the next check; it does not stop the formatter from writing.
- detection, `.taplo.toml`: the include list names only the repository's own files, so the formatter does not discover a fork. The other formatters and linters skip `third_party/` already.
- Not a guard of this record: the agent settings refuse edits by the agent's own tools under `third_party/`; they do not govern what a formatter process writes.

The status is guarded: a check stops a recurrence from passing. It is not closed by design, because widening the include list would reopen it.
