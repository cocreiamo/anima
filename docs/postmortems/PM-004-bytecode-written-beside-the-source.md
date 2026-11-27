---
id: PM-004
date: 2026-11-27
title: Bytecode written beside the source
class: tool run outside the repository's entry point
status: guarded
guards:
  - kind: test
    ref: test_R91_no_bytecode_outside_cache
    added: 2026-11-27
  - kind: rule
    ref: skills/anima-tech-mise.md
    added: 2026-11-27
recurrences: []
---

# PM-004: Bytecode written beside the source

## Overview

A `__pycache__` directory with one compiled file of Python 3.12 existed under `tests/repository/`, although bytecode belongs under `.cache/`.

## What happened

The directory held one file, `tests/repository/__pycache__/sysml_model.cpython-312.pyc`, written at 16:52 on 2026-11-27. The repository pins Python 3.13 through `mise` and sets the bytecode cache prefix in the environment that `mise` provides. A file of version 3.12 therefore came from an interpreter run outside `mise` (inferred from the version in the file name; the run itself was not observed), before this review. It was listed and removed.

## Root causes

Python run outside `mise` does not get `PYTHONPYCACHEPREFIX`, so it writes bytecode next to the source. The repository's ignore file has a single entry, `.cache/`, so git did not hide it and nothing noticed it.

## Resolution

The directory was removed. The ignore file stays a single entry; the guard is a check.

## Impact

One stray file, untracked. It could have been committed.

## Timeline

| When       | What                                              |
| ---------- | ------------------------------------------------- |
| 2026-11-27 | The directory was found, listed and removed.      |
| 2026-11-27 | A check that fails on bytecode outside `.cache/`. |

## How did we do

Went well: the likely cause was read from the interpreter version in the file name. Did not go well: no check existed.

## Guards

- test `test_R91_no_bytecode_outside_cache`: fails on any `__pycache__` or compiled file among the files git does not ignore.
- rule, `skills/anima-tech-mise.md`: Python runs only through `mise`.

The status is guarded. It is not closed by design: running an interpreter by hand remains possible; the test notices the result.
