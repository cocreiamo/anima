---
id: PM-014
date: 2026-11-28
title: The first publishing run failed in the publish job, whose shell had never been run against the real tools
class: shell written from memory of what a tool prints, tested only as text
status: guarded
guards:
  - kind: test
    ref: test_R115_promotion_loads_only_the_image_that_passed
    added: 2026-11-28
  - kind: test
    ref: test_R170_promotion_steps_are_calls_to_tested_commands
    added: 2026-11-28
recurrences: []
---

# PM-014: The first publishing run failed in the publish job, whose shell had never been run against the real tools

## Overview

The first publishing run of the promotion (version 0.0.1) passed `verify` and failed in `publish`, after about 40 minutes, with `Error: invalid reference format`. Nothing was pushed and no release exists. The cause was the shell of the job, written from what the tools were believed to print and checked only as text.

## What happened

The step that loads the archive took the last line `podman load` prints as the image reference. That line is `Loaded image: localhost/...`, which is not a reference. Rehearsing the whole job against the real podman 4.9.3 and a throwaway registry on localhost found a second defect behind it: the digest of an existing tag was read with `podman image inspect --format '{{.Digest}}'` after a pull, and on a runner that has loaded the image it answers the digest of the loaded copy (`sha256:637295...`), not the one in the registry (`sha256:faf570...`), so a release would have pointed at a digest the registry does not hold. The id of an image (the digest of its config) survives `podman save` and `podman load`; the digest of its manifest does not.

## Root cause

The root cause is that the shell of the job lived in the workflow, where it could be tested only as text, so a path that had never run counted as checked. Evidence: a rehearsal of every line against podman 4.9.3 and a local registry reproduced the failure (`podman load` prints `Loaded image: <name>`) and found the second defect (`.Digest` of a loaded image is not the registry's: 637295... against faf570...). Contributing:

- The tests of the job (R115) read its text and had no run of the shell against the tools; a job that has never run was treated as checked.
- The previous fix (PM-013) rehearsed one command, not the job around it.
- The cost of a real run (about 40 minutes) made each defect surface one at a time.
- The shell lived in the workflow, where it could be tested only as text or by extracting it.

## Class and earlier occurrences

The class is shell written from memory of what a tool prints and tested only as text. It occurred before in PM-013 (the same job: a check written with a prefix that podman 4.9.3 does not accept, always concluding that the tag was absent). No gap belongs to it.

## Resolution

Every step of the promotion that does something is one call to a command of `mise-tasks/promote/` (`archive`, `load`, `tag-state`, `registry-digest`, `publish`, `plan`, `green`, `release`). Each is run by a test against real podman and a throwaway registry (`mise run promote:test`, run by the system tests workflow on every change to the commands or the workflow), with a tiny image and never the engine image; the last call to GitHub of `green` and `release` is replaced by a recorder in the tests. The digest of an existing tag is read from the registry. A workflow that holds a decision or a line of its own fails R170.

## Impact

The first release was delayed by one run. Nothing was pushed or released.

## Timeline

| When       | What                                                                           |
| ---------- | ------------------------------------------------------------------------------ |
| 2026-11-28 | Publishing run: `verify` passes, `publish` fails loading the archive.          |
| 2026-11-28 | Job rehearsed step by step on a local registry; two defects found, both fixed. |
| 2026-11-28 | Steps turned into tested commands (founder's decision), integration tests.     |

## How did we do

Went well: the failure stopped before any push. Did not go well: a path never run was listed as unverified but tested as if it were proven.

## Design options

1. Every step of every workflow is a call to a command tested against the real tools (applied to the promotion in this change; the other workflows and the general rule are another change). Recommended: it removes the class, not the instance.
2. Keep the shell in the workflow and run its functions on recorded outputs (done first, in the previous change, and dropped): it proves the parsing, not the interplay of the tools.

## Decision on the options

Option 1 was decided by the founder on 2026-11-28 and is built here for the promotion workflow.

## Guards

- test `test_R115_promotion_loads_only_the_image_that_passed` (requirement R115, with its `_detects_violation` companion): runs `archive` and `load` for real and refuses an archive of another image.
- test `test_R170_promotion_steps_are_calls_to_tested_commands` (requirement R170, with its companion): no step of the workflow holds shell, and every command it calls is run by a test.
- Not protected: the push to the real registry and its login, `gh` against GitHub (moving `main-green`, `gh release create`), and `mise run` on the runner, which only the first publishing run shows.
