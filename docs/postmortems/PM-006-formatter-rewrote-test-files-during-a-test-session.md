---
id: PM-006
date: 2026-11-27
title: The formatter rewrote test files while a test session was running
class: tool run while another run reads the same files
status: guarded
guards:
  - kind: test
    ref: test_R112_format_and_test_exclude_each_other
    added: 2026-11-28
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

One lock that the `format` and `test` tasks take: `format` holds it exclusively, `test` holds it shared, so a format run waits for running test sessions and a test session waits for a running format run (`mise-tasks/format`, `mise-tasks/test`; R112). The proposed rule that only one agent runs `format` at a time was not taken: the lock makes it unnecessary.

## Impact

Not observed by the author. A test session that reads a file changed in the middle of it can fail or pass for the wrong reason, and the failure then looks like a fault of the code.

## Timeline

| When       | What                                                      |
| ---------- | --------------------------------------------------------- |
| 2026-11-27 | The formatter rewrote test files during a test session.   |
| 2026-11-27 | The engine implementer reported it; this record was made. |
| 2026-11-28 | The two tasks took one lock; the guard test was added.    |

## How did we do

Went well: the event was reported. Did not go well: nothing orders the two tasks, and nothing detects the overlap.

## Guards

- test `test_R112_format_and_test_exclude_each_other` (requirement R112, with its `_detects_violation` companion): runs the `format` and `test` tasks together, one format run against three test runs, with stand-ins for the formatters and the test runner that log their start and end, and shows that no format run overlaps a test run in time; the companion shows that the overlap check sees an overlap in a hand-made log and that the same two tasks with the lock lines taken out do overlap. It does not prove that the real formatters and pytest are the commands inside the lock, and it does not cover a formatter or a test run started by hand outside `mise run`, which takes no lock.

The status is guarded: the fault was a missing order between two tasks, and a check now stops it.
