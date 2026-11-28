---
id: PM-019
date: 2026-11-28
title: Pull requests that each added a requirement to the model conflicted, because the model was one long file
class: a file whose shape makes independent additions touch the same lines
status: guarded
guards:
  - kind: test
    ref: test_R150_independent_additions_do_not_conflict_in_generated_files
    added: 2026-11-28
  - kind: test
    ref: test_R190_each_requirement_in_a_file_of_its_own
    added: 2026-11-28
recurrences: []
---

# PM-019: Pull requests that each added a requirement to the model conflicted, because the model was one long file

## Overview

Several pull requests were open at once and each added a requirement at the same place of `model/anima.sysml`; git cannot merge two additions at one place, so the second pull request left the merge queue, seven times in one day, and once a requirement was left without its closing lines by a hand resolution. The root cause is that the model was one file whose groups grow at their end, so that independent additions always land together.

## What happened

A new requirement takes the next free id and its text is added at the end of its group, its `satisfy` line at the end of the satisfaction section and its verification at the end of the verification package. Every pull request that added a requirement edited those same three places. Each conflict cost a merge of `main`, a resolution by hand, a full check and a new round of CI. In one resolution the closing lines of a requirement were lost. Backlog tasks and skills, which are one file each, never conflicted.

## Root cause

The model is one file in which the growing lists end at the same lines, so independent additions touch the same lines. Evidence: the brief of this change counts seven occurrences of the same merge conflict in the model in one day, and a test (R150, extended) that adds a requirement on each of two branches of git and conflicts on the single-file layout and merges on the layout of one file per requirement.

## Class and earlier occurrences

The class is a file whose shape makes independent additions touch the same lines. Earlier occurrences: PM-011 (the catalog, the pending tests and the skills index, which are generated) and PM-016 (the routing table of AGENTS.md, which is generated). Both were fixed in the rendering of a generated file; the hand-written model, which every requirement changes, had the same shape and R150 did not look at it.

## Resolution

Each requirement, with its verifications and its `satisfy` line, is a file of its own under `model/requirements/<group>/`, named `R<id>-<name>.sysml`, in a package of its own. The root file `model/anima.sysml` holds the structure they refer to (the ports, the parts, the triggers) and no requirement. The pilot reads a directory as one model and resolves packages across files (observed on 2026-11-28 with the pinned release); a package declared in two files is not merged, which is why each file has its own. A new requirement is one new file and changes no file that exists, so two additions cannot conflict. The move was made by a script and shown equivalent: the export of the model before and after has the same elements once the layout-dependent fields are left out.

A second step removes the allocation of identifiers, which collided the same way (R165 to R167, PM-014 claimed three times): the name of a requirement is its identifier, and a new requirement carries no number (`newRequirementsCarryNoNumber`); postmortems are named by date and slug from now on. Two branches that choose one name make one file, which git reports.

## Impact

Time and CI rounds of the pull requests that conflicted. No defect reached `main`.

## Timeline

| When       | What                                                                                   |
| ---------- | -------------------------------------------------------------------------------------- |
| 2026-11-28 | Seven conflicts in the model between open pull requests; one requirement lost its end. |
| 2026-11-28 | The founder approves one file per requirement; the pilot tried on a split model first. |
| 2026-11-28 | The model split by script; R150 extended to the model; R190 to R192 added.             |

## How did we do

Went well: PM-011 had named the class, and the three-way merge of two additions was already a test. Did not go well: the fix of PM-011 and PM-016 was written for the generated files that had conflicted; the one hand-written file that every requirement edits was not looked at until it had conflicted seven times.

## Design options

- One file per requirement (done here): two additions are two files; costs many small files and a root that stays free of requirements.
- Keep one file and order the requirements by name, as the generated lists are: an addition lands where its name falls, but two names that sort between the same neighbours still conflict, and the `satisfy` and verification sections would have to be ordered the same way. Rejected: it narrows the conflicts and does not remove them.
- A merge driver for the model: GitHub's merge and its merge queue run none (PM-011). Rejected.

## Decision on the options

The founder approved one file per requirement on 2026-11-28.

## Guards

- test `test_R150_independent_additions_do_not_conflict_in_generated_files` (requirement R150, with its `_detects_violation` companion): commits the model, adds one requirement on each of two branches the way the layout says and merges them with git; the companion shows that two additions at the end of one file conflict.
- test `test_R190_each_requirement_in_a_file_of_its_own` (requirement R190, with its `_detects_violation` companion): every requirement is in a file of its own named by its id, no requirement is outside such a file, and no id is in two files, so a requirement cannot be put back into a shared file.
- Not protected: two branches that take the same id add two files with the same id, which R190 reports once they meet; the coordinator assigns the ids. A new shared file that every requirement must edit is not looked for by name; R150's test would see it once a requirement needs it.
