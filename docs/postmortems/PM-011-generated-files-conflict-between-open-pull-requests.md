---
id: PM-011
date: 2026-11-28
title: Every pull request that added a requirement conflicted with every other one in a generated file
class: a derived file whose shape makes independent additions touch the same lines
status: guarded
guards:
  - kind: test
    ref: test_R150_independent_additions_do_not_conflict_in_generated_files
    added: 2026-11-28
recurrences: []
---

# PM-011: Every pull request that added a requirement conflicted with every other one in a generated file

## Overview

With several pull requests open at once, each one that added a requirement conflicted with each other one in `docs/catalog.md`, five times in one day. Each conflict cost a merge of `main`, a regeneration, a full check and a new round of CI, and pull requests fell out of the merge queue.

## What happened

The requirements table and the list of fitness functions of the catalog, and the list of pending tests, were sorted by id, and a new requirement takes the next free id: two branches inserted their line at the same place, after the last one. Git reports an insertion at the same place of both sides as a conflict. The total of unverified rules in the skills index was a second place where two branches that changed a count edited the same line. GitHub's merge and its merge queue run no custom merge driver, so the conflict could not be resolved by a `.gitattributes` rule.

## Root causes

- A list of a generated file ordered by the key that new items take in increasing order, so that independent additions always land at the same end.
- A sum in a generated file, which every change of a part edits.
- Nothing checked that two additions merge.

## Resolution

The lists are sorted by name, so an addition lands where its name falls; the total is not written. The merge of two independent additions is a test.

## Impact

Time and CI rounds of five pull requests. No defect reached `main`.

## Timeline

| When       | What                                                                    |
| ---------- | ----------------------------------------------------------------------- |
| 2026-11-28 | Five conflicts in `docs/catalog.md`; cause read in the three-way merge. |
| 2026-11-28 | Lists sorted by name, total removed, merge test added.                  |

## How did we do

Went well: the conflicts were always in one file and always the same shape. Did not go well: each was resolved by hand before anyone asked why it recurred.

## Guards

- test `test_R150_independent_additions_do_not_conflict_in_generated_files` (requirement R150, with its `_detects_violation` companion): renders the growing parts of the generated files for a base and two independent additions and merges them with `git merge-file`; the companion shows that the old renderings conflict.
- Not protected: two additions whose names sort between the same two neighbours still conflict (one in about a hundred pairs); and two branches that take the same id conflict in the model, which is a real collision.
