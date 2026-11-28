---
id: PM-016
date: 2026-11-28
title: One new skill pushed AGENTS.md over its size limit because the routing table is padded to its widest cell
class: a derived file whose shape makes independent additions touch the same lines
status: guarded
guards:
  - kind: test
    ref: test_R150_independent_additions_do_not_conflict_in_generated_files
    added: 2026-11-28
recurrences: []
---

# PM-016: One new skill pushed AGENTS.md over its size limit because the routing table is padded to its widest cell

## Overview

The pull request that adds the skill `anima-entry-design` failed the size check (R81) with `AGENTS.md: 13191 bytes, limit 13000`, because the generated routing table of AGENTS.md pads every row to the width of its widest cell, so one new row cost 228 bytes. The table was also a merge-conflict source, as PM-011 had already found for other files.

## What happened

`main` carried AGENTS.md at 12963 of 13000 bytes. A new skill with a longer cell than any before it made the formatter-compatible rendering rewrite every row of the table: the file grew by the new row and by the padding of all the others, and the change touched every line of the table. The check blocked the pull request; nothing reached `main`.

## Root cause

The routing was rendered as a column-aligned Markdown table (Prettier pads a table, so the generator padded it the same way to stay formatted). In a padded table the size of the file is rows times the widest cell, not the content, and a new row with a wider cell rewrites every other row. Evidence: the 228 bytes of one added row reported by the check, and a test that merged two skill additions, one with a wide cell, with `git merge-file` and conflicted before the change.

## Class and earlier occurrences

The class is a generated, committed, always-loaded file whose rendering makes independent additions touch the same lines and inflate its size. Earlier occurrence: PM-011 (the catalog, the pending tests and the skills index). R150's test covered the new skills only with cells narrower than the widest one, so it could not see this form.

## Resolution

The routing is a list, one skill per line (`name`, family, paths), sorted by family and name. A list is not padded by the formatter, so a skill costs only its own line and touches only its own line. AGENTS.md went from 12963 to 9045 bytes and the always-loaded set from 19691 to 15773 bytes. R150's test adds a skill whose cells are wider than every other and merges it with another addition; its companion shows that the padded table conflicts.

## Impact

One pull request blocked for the time of the diagnosis. No defect reached `main`.

## Timeline

| When       | What                                                                               |
| ---------- | ---------------------------------------------------------------------------------- |
| 2026-11-28 | The check of the pull request adding `anima-entry-design` fails on R81.            |
| 2026-11-28 | Cause read in the generator; the routing rendered as a list; R150's test extended. |

## How did we do

Went well: the check named the file and the numbers, and PM-011 had named the class. Did not go well: PM-011's fix and its test were written for the files that had conflicted, not for every generated list, so the same shape survived in another file.

## Design options

- Render the routing as a list, one line per skill (done here): removes the padding and the shared lines; AGENTS.md keeps the routing in view.
- Generate the routing outside AGENTS.md (the path rules in `.claude/rules/` already point to each skill, and `skills/README.md` is the index) and leave one sentence in AGENTS.md: AGENTS.md stops growing with the number of skills and the routing cannot conflict in it. Cost in discoverability: an agent that has not touched a path yet no longer sees the whole map in the file it always loads, and has to open the index; a new agent would find skills only by the path rules or by the index. Recommendation: not now, the list is enough.
- Raise the limit: rejected, it hides the growth.

## Decision on the options

Only the rendering change is made here. Generating the routing outside AGENTS.md, or any larger change, is the founder's decision and is awaited.

## Guards

- test `test_R150_independent_additions_do_not_conflict_in_generated_files` (requirement R150, with its `_detects_violation` companion): merges a skill with cells wider than every other with another addition; the companion shows that the padded table conflicts. Also protects the size, since the new row is its own bytes only (R81 still holds the limits).
- Not protected: any other generated list that is padded by a formatter would have the same shape; none is known.
