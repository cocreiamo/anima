---
name: anima-tech-adrs-madr
description: "Use when writing, converting, checking or indexing decision records in Anima with MADR files and the adrs tool: required front matter, what adrs doctor does and does not check, the generated index, configuration that must not leak in from the user."
family: technology
paths:
  - docs/adr/**
  - adrs.toml
---

# Decision records: MADR and adrs

How the `adrs` tool treats MADR records when run. Where a decision is recorded
and by whom is in `anima-repository-conventions`.

## Use this when

- Writing a new record in `docs/adr/` or converting an old one.
- A check passes or fails and you do not know why.
- Changing the index `docs/adr/README.md` or its generator.
- `adrs` lists nothing, or lists differently on another machine.

## Rules

1. **Create a record with `adrs new "Title"` and quote a multi-word title.** Observed on 2026-11-27 with adrs 0.13.0; working files `adrs.toml`, `docs/adr/`, `mise-tasks/generate/generators.py`.
2. **Give every record `number` and `title` besides plain MADR front matter.** Example (`docs/adr/0010-roles-and-access.md`): `number: 10`, `title: …`, `status: proposed`, `date: 2026-11-27`, `decision-makers: [<role>]`. Not: plain MADR front matter; without `number` the record is not listed and no error is shown (GAP-044). Run `adrs export json` and count the records after converting.
3. **Write decision makers as a YAML list, even for one.** Not: `decision-makers: Name`, which is not read.
4. **Check with `adrs doctor --warnings-as-errors`, and add what it does not check.** It checks required sections, status values, dates, numbering and Markdown links between records. Not: expecting it to check plain-text references to other records or the "Considered Options" section (GAP-045); a test of ours must check what matters.
5. **Keep every key in `adrs.toml` and point the tool at it.** Keys: `adr_dir`, `mode = "nextgen"`, `default_status`, `no_edit = true`, `[templates]` with `format = "madr"` and `variant = "full"`, and `[doctor]` with `warnings_as_errors = true`; `ADRS_CONFIG = "{{config_root}}/adrs.toml"` in `mise.toml`. Not: expecting the same result on every machine; the tool also reads a user-level configuration, so a key set in `adrs.toml` wins over a global one only if named there.
6. **Produce the index with a status column from the JSON export.** Example: `adrs export json | jq -r '.adrs | sort_by(.number)[] | …'` (`adr_index` in `generators.py`). Not: the tool's own table of contents, which has no status (GAP-023).
7. **Detect a stale index by generating it again and comparing.** Example: `mise run generate:check`. Not: expecting a mode that fails on a stale index; there is none (GAP-023).
8. **Pin the tool exactly and keep records in plain MADR.** Not: expecting a stable tool; it is a 0.x project (GAP-024).
9. Unverified: other `adrs` modes than `nextgen` with the `madr` template in its `full` variant, and the other template formats the spike tried; the tool's behaviour on records with a status other than the ones `docs/adr/` uses today.

## Questions to answer before proposing

- Does the record list at least two options that were really considered?
- Are references to other records Markdown links?
- After the change, does `adrs export json` count every record?
- Does the decision belong in a new record or an amendment?

## Where the result goes

The record is a file in `docs/adr/` made with `adrs new`; the index is generated (`mise run generate`). The format and the toolchain are in `anima-repository-conventions`. Limits go to `gaps.toml` (GAP-023, GAP-024, GAP-044, GAP-045). Related skills: `anima-repository-conventions`, `anima-tech-mise`.
