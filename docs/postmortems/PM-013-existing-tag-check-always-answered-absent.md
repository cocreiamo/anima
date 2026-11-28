---
id: PM-013
date: 2026-11-28
title: The promotion's check for an existing image tag always concluded the tag did not exist
class: a command written for one meaning that the tool reads as another, with every failure taken for one answer
status: guarded
guards:
  - kind: test
    ref: test_R115_published_tag_is_never_moved_and_unknown_is_not_absent
    added: 2026-11-28
recurrences: []
---

# PM-013: The promotion's check for an existing image tag always concluded the tag did not exist

## Overview

The job that publishes the engine image decided whether the version tag was already in the registry with `podman manifest inspect "docker://..."`, and read any failure as "does not exist". On podman 4.9.3 that form fails whatever the registry holds, so a re-run after a half-finished release would have pushed over an existing tag, which the release rules forbid. A spike found it before the first release was published; nothing was pushed.

## What happened

`manifest inspect` takes a bare reference. With the `docker://` prefix it looks the name up among local images and fails with `unsupported transport "docker" for looking up local images`. The check only distinguished success from failure, so this failure, a missing tag, an unreachable registry and a refused token all gave the same answer: absent. No test ran the check, and the path had never run.

## Root causes

- A failure of any kind was read as "does not exist"; "cannot tell" had no place in the decision.
- The command line was read, not run, against the pinned tool before it was written into the workflow.
- The test of the publish job read the text of the step but not what the check answers.

## Resolution

The step asks the registry with the bare reference and classifies the answer in a function with three outcomes: exists (exit status 0), absent (only the registry's own `manifest unknown` or `name unknown`) and unknown (anything else: no network, 401, 403). The step stops on unknown and never pushes. The function is run by a test against a stub that returns the recorded outputs of the pinned podman, and the stub answers the prefixed form as that podman does.

## Impact

None in a release: found by a spike before the first publishing run. Had it run, a tag could have been moved.

## Timeline

| When       | What                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| 2026-11-28 | A spike runs the check against a registry and finds the prefixed form fails.  |
| 2026-11-28 | The three outcomes recorded, the function and its test written, step changed. |

## How did we do

Went well: found before the first release. Did not go well: the promotion was specified and tested as text only.

## Guards

- test `test_R115_published_tag_is_never_moved_and_unknown_is_not_absent` (requirement R115, with its `_detects_violation` companion): runs the function on recorded outputs for the three outcomes and requires that the step stops on unknown and that the prefixed form is not used.
- Not protected: the real answers of the registry for a package that does not exist yet, which only the first publishing run shows.
