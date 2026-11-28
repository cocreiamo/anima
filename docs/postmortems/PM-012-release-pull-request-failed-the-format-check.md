---
id: PM-012
date: 2026-11-28
title: The first release pull request could not merge because the formatter rejected the changelog the release tool wrote
class: a file written by a tool that the repository's own checks were never run against
status: guarded
guards:
  - kind: test
    ref: test_R155_files_written_by_the_release_tool_are_not_formatted_and_are_licensed
    added: 2026-11-28
recurrences: []
---

# PM-012: The first release pull request could not merge because the formatter rejected the changelog the release tool wrote

## Overview

The release pull request opened by the release tool was blocked: its required check `check / check` failed in lint, because `prettier --check .` rejected `CHANGELOG.md` as the tool writes it. No release was possible until this was fixed.

## What happened

The tool writes the changelog in its own layout (two blank lines before a heading, `*` bullets) and offers no option to change it. The repository formats every text with Prettier and had no exception for the file. Nothing ran the checks against a file the tool writes before the tool first wrote it.

## Root causes

- A file written by a tool outside our control was subject to the formatter that we apply to what we write.
- No requirement named the files the release tool writes.

## Resolution

`CHANGELOG.md` is excluded from the formatter in `.prettierignore`. The release tool's other file, the manifest, and the licensing annotation (`REUSE.toml`, `**`) already passed; the whole of `mise run check` was run with the tool's diff applied, and only the formatter failed (the time limit of R55 failed under load only). A test reads the release configuration and requires every file it writes to be excluded from the formatter and covered by a licensing annotation.

## Impact

The first release was delayed. Nothing reached `main` wrongly.

## Timeline

| When       | What                                                                          |
| ---------- | ----------------------------------------------------------------------------- |
| 2026-11-28 | Release pull request opened; `check / check` fails in lint on the changelog.  |
| 2026-11-28 | Tool's diff applied locally, every check run, changelog excluded, test added. |

## How did we do

Went well: the failure named the file at once. Did not go well: the release path was specified without ever running it.

## Guards

- test `test_R155_files_written_by_the_release_tool_are_not_formatted_and_are_licensed` (requirement R155, with its `_detects_violation` companion).
- Not protected: a new kind of file the tool writes that the configuration does not name (an extra file listed in a package) is not seen.
