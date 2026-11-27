---
id: PM-006
date: 2026-11-27
title: The formatter rewrote test files while a test session was running
class: tool run while another run reads the same files
status: open
guards: []
recurrences: []
---

# PM-006: The formatter rewrote test files while a test session was running

## Overview

`mise run format` rewrote test files while a test session that reads them was running. The engine implementer reported it; it is recorded here from that report, and the exact files and the effect on the session were not observed by the author of this record.

## What happened

Two runs worked on the same tree at the same time: the code formatter, which rewrites files in place, and a test session, which reads them. The formatter changed test files during the session.

## Root causes

Nothing orders the formatter and the tests. Both are plain tasks of the task runner, started by different implementers working at once, and the formatter writes where the tests read. This is a consequence of several agents sharing one worktree, which the rules already forbid for the same paths (`anima-working-as-an-agent`, rule 5); the rule was kept for who edits a path, not for who runs a task that edits files.

## Resolution

Not yet decided. The proposals are one lock that the `format` and `test` tasks take, or a rule that only one agent runs `format` while others work.

## Impact

Not observed by the author. A test session that reads a file changed in the middle of it can fail or pass for the wrong reason, and the failure then looks like a fault of the code.

## Timeline

| When       | What                                                      |
| ---------- | --------------------------------------------------------- |
| 2026-11-27 | The formatter rewrote test files during a test session.   |
| 2026-11-27 | The engine implementer reported it; this record was made. |

## How did we do

Went well: the event was reported. Did not go well: nothing orders the two tasks, and nothing detects the overlap.

## Guards

None yet; the status is open and the record is closed within the limit of R85 only by a guard that exists. The guard to build is a check or a lock, with its negative case, that makes a run of `format` and a run of `test` exclude each other.
