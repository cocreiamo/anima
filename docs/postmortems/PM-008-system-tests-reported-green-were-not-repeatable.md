---
id: PM-008
date: 2026-11-28
title: The system tests, reported green once, failed on the next run
class: a result seen once was taken as repeatable
status: guarded
guards:
  - kind: test
    ref: test_R21_upstream_regression_suite_passes
    added: 2026-11-28
  - kind: test
    ref: test_R42_abrupt_stop_recovers_with_same_start
    added: 2026-11-28
recurrences: []
---

# PM-008: The system tests, reported green once, failed on the next run

## Overview

An agent reported `mise run engine:test` all green after one run. The next run on the same machine failed two tests, because one read its verdict from a place that a cached build does not fill and the other took the exit code of a command for the fact it needed. Both were faults of the tests, not of the engine.

## What happened

The second run had every image layer cached and the machine was under heavy load. `test_R21_upstream_regression_suite_passes` failed: the task looked for "All N tests passed" in the output of the image build, and a build whose layers are all cached does not run the `make check` step, so the line was not there although the suite had passed for exactly these inputs. `test_R42_abrupt_stop_recovers_with_same_start` failed: the helper asserted that `podman kill` returned 0, and under load it returned 125 (`timed out waiting for file .../exits/<id>`) although the signal had been sent.

## Root causes

- A single green run was reported as the state of the suite. The first run had no cache, which is the one case in which the build output holds the verdict; the repeat, which is the usual case, was never seen.
- The verdict was read from a log of the build, a side effect, not from the result the step keeps in the image.
- The step piped `make check` to `tee | tail`, so the exit status of the build was that of `tail`: a failing `make` would not have failed the build. The task's grep was the only check, and it read the wrong place.
- The helper took the exit code of a command that waits on the container runtime for the fact it needed (the container is stopped), instead of observing that fact.

## Resolution

The step runs `make check` into a file in the image keeping its exit status; the task reads that file out of the built image (by image id) into `.cache/engine/logs/regress.log` and keeps the build output in `regress-build.log`. The test reads the verdict through one function of text. The second repeat run showed the same fault in the removal of an engine container at the end of a test (500, "given PID did not die within timeout", at load about 15). The helpers `kill`, `stop`, `start_again` and `remove` send the command and then wait, within a bound, for the phase read from `podman inspect`; a container in any other phase is never accepted, and the failure message names the phase and the last answer.

## Impact

One false failure of the suite on a repeat run; the engine was not at fault. No data lost, nothing reached `main`.

## Timeline

| When       | What                                                                  |
| ---------- | --------------------------------------------------------------------- |
| 2026-11-28 | A repeat of `engine:test` failed two tests that had passed before.    |
| 2026-11-28 | Both traced to the tests; fixed, with the repeat run as the evidence. |

## How did we do

Went well: the log of the failed run named both causes. Did not go well: the suite had been called green on one run, and the repeat is where its faults showed.

## Correction, 2026-11-28

The text above reads the answer 125 of `podman kill` as "the command took effect, so observe the phase" and counts Status `stopped` as stopped. That was incomplete. After the 125 podman reports Status `stopped` with ExitCode -1 because it gave up waiting 5 s for the exit file, while the previous run is not finished; a start issued then answers 0 and is undone when the old run's exit is applied (GAP-056). `test_R42_abrupt_stop_recovers_with_same_start` failed again on GitHub for this reason. Only Status `exited` is a finished stop; `container_phase` now reports `stopped` for it alone (with a companion case for Status `stopped`), and `Engine.kill` and `Engine.stop` return only then.

## Guards

- test `test_R21_upstream_regression_suite_passes` (requirement R21, with its `_detects_violation` companion): reads the verdict through `regress_tests_passed` from the result kept in the image; the companion shows that a failed result, an empty one and the output of a cached build give no verdict. It does not prove that `make` failing fails the build; that rests on the kept exit status in the container file, which was read and not exercised with a failing suite.
- test `test_R42_abrupt_stop_recovers_with_same_start` (requirement R42, with its companion): the helpers decide on `container_phase` of the inspected state; the companion feeds it running, paused, created, unreadable and missing states. Load itself is not reproduced; it is the probable cause, not proven.
- rule 19 of `anima-tech-podman-quadlet-bootc` (PM-008): a command to the container runtime that waits can time out although it took effect; observe the phase.
- The repeat is the evidence: a result is called repeatable only after two runs in a row, the second on a warm cache.

The status is guarded: the faults were in the tests, and checks now cover the decisions; the end-to-end repeat was run twice in a row.
