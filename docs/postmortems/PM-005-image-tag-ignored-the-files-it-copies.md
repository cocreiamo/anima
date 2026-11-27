---
id: PM-005
date: 2026-11-27
title: An image tag ignored the files its container file copies
class: derived key that leaves out an input
status: guarded
guards:
  - kind: test
    ref: test_R99_image_tag_depends_on_every_input
    added: 2026-11-27
recurrences: []
---

# PM-005: An image tag ignored the files its container file copies

## Overview

The database unit of the engine failed at start with a parse error, because the inner image it ran contained an older access-rules file than the repository. The task that builds the inner images computed the tag of an image from the source commits and the container file only, so a corrected configuration file, copied by the container file, caused no rebuild.

## What happened

The access-rules file was corrected in the repository. The build task found an image with the expected tag and reused it. The image still held the earlier file, and the unit failed at start with a parse error on that stale file. The failure is deterministic: it happens every time a file copied into an image changes and nothing else does.

## Root causes

The tag of an image was a function of the source commits and of the container file, and not of the files the container file copies in. The tag therefore stayed the same while the content that the image should hold had changed, and the build treated the tag as proof that the image was current. Nothing compared the content of the image with its inputs.

## Resolution

Temporary: the stale image was rebuilt. Long-term: the tag of an image is computed by `mise-tasks/engine/tag` from every input of its build, that is the source commits, the container file and every file the container file copies.

## Impact

One failed start of the engine's database unit, found by reading the parse error. No data was affected. The same cause would make any corrected file copied into an inner image silently ineffective until the image is rebuilt by hand.

## Timeline

| When       | What                                                                               |
| ---------- | ---------------------------------------------------------------------------------- |
| 2026-11-27 | The unit failed at start with a parse error on the access-rules file.              |
| 2026-11-27 | The image was found to hold an older file than the repository; the cause was read. |
| 2026-11-27 | A requirement and a verification were added for the guard below.                   |

## How did we do

Went well: the parse error named the stale file, so the cause was found by comparing the file in the image with the repository. Did not go well: the tag looked like a proof of currency and nothing checked that it was one.

## Guards

- test `test_R99_image_tag_depends_on_every_input` (requirement R99, with its `_detects_violation` companion, in `tests/system/test_inputs.py`): the tag of the database image changes when the container file or any file it copies changes, and a tag made of the commits and the container file only is shown to miss them. It runs without starting a container.

The status is guarded: a check stops a recurrence from passing. It is not closed by design, because the tag is still computed by a task and not by a construction that cannot leave an input out. The check covers the database image only; another inner image has its own container file and is not yet covered.
