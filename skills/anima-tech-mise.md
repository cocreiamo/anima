---
name: anima-tech-mise
description: "Use when adding or changing a mise task, tool, git hook, lockfile entry, environment variable or dev container setting in Anima: file tasks, the github backend, npm and pipx lock material, parallel tasks sharing files, a user-level configuration leaking in, uv and Python."
family: technology
paths:
  - mise.toml
  - mise.lock
  - mise-tasks/**
  - .mise/**
  - .devcontainer/**
---

# mise

How mise, the single entry point for tools and tasks, behaves when run. The
repository rules are in `anima-repository-conventions`.

## Use this when

- Adding a tool, a task or a git hook.
- A task passes alone and fails in `mise run check`.
- A tool installs on one machine and not on another.
- Isolating a run from the user's own mise configuration.

## Rules

1. **Write a script task as a file task under `mise-tasks/`, with its description in a comment line.** Example: `#MISE description="…"`; dependencies with `#MISE depends=["…"]` (`mise-tasks/engine/units-check`).
2. **Run tasks under `depends` as if they were parallel.** Not: expecting them in sequence; anything they share on disk must be safe for that, and two model exports once overwrote each other. Export into a directory of your own, then move it into place in one step (`mise-tasks/model/export`).
3. **Generate git hooks with `mise generate git-pre-commit --write --hook <hook> --task <task>`.** The message file is passed to the task of a `commit-msg` hook (`committed --commit-file` in `mise.toml`).
4. **Install a tool absent from the registry through the `github:` backend with an exact version.** Example: `"github:joshrotenberg/adrs" = "<exact version>"`; a release binary needing another command name takes `{ version = "<exact>", rename_exe = "<name>" }` (the backlog tool, `anima-tech-backlog-md`).
5. **Expect `npm:` and `pipx:` tools to write lock material under `.mise/locks/` as well as `mise.lock`.** `lockfile = true` under `[settings]` records URLs and checksums per platform in `mise.lock`; generated lock files are never edited by hand.
6. **Keep caches and data inside the project with `{{config_root}}` in `[env]`.** Example: `UV_PROJECT_ENVIRONMENT = "{{config_root}}/.cache/venv"`, `PYTHONPYCACHEPREFIX` under `.cache/`. Not: running Python outside `mise`; the interpreter then writes `__pycache__` beside the source, which happened once (PM-004).
7. **Make `uv` use the pinned Python with `UV_PYTHON_PREFERENCE = "only-system"` in `[env]`.** Not: expecting `uv` to use the project's Python; it picks its own unless told.
8. **Isolate a run by pointing mise's data, cache, state and trusted paths inside the project.** The variables are `MISE_DATA_DIR`, `MISE_CACHE_DIR`, `MISE_STATE_DIR`, `MISE_TRUSTED_CONFIG_PATHS` and `MISE_YES`. Not: expecting the project to be self-contained; a user-level mise configuration leaks into it, and extra tools at `latest` were installed from one (GAP-047).
9. Unverified: behaviour on a platform other than the one the lockfile was written on. `mise generate devcontainer` was seen to exist and its output was not used here; the development container is Debian-family (GAP-021).

## Questions to answer before proposing

- Is the tool in the mise registry, or does it need a backend?
- Is the version exact and recorded in `mise.lock`?
- Does the task share a file with another task that may run at the same time?
- Does anything write outside `.cache/`?
- Does the result depend on the user's own mise configuration?

## Where the result goes

Tools to `mise.toml` (and `mise.lock`, generated); tasks to `mise.toml` or `mise-tasks/`; the repository rules to `anima-repository-conventions`. Limits go to `gaps.toml` (GAP-021, GAP-047). Related skills: `anima-adopting-a-component`, `anima-tech-adrs-madr`, `anima-tech-sysml-pilot`, `anima-tech-backlog-md`.
