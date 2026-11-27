---
name: anima-tech-backlog-md
description: "Use when creating, editing or reading a task of the backlog in Anima with Backlog.md: installing the tool, its non-interactive commands, the task file format, which custom front matter keys and sections its commands keep, and what it must never do here (commit)."
family: technology
paths:
  - backlog/**
  - backlog.config.yml
  - docs/work/**
---

# Backlog.md

How the Backlog.md command line, the adopted home of work to do, behaves when
run. The rules for work, the unit of work and its templates are in
`anima-working-as-an-agent`.

## Use this when

- Creating, editing, archiving or listing a task.
- Changing `backlog.config.yml` or the layout under `backlog/`.
- Adding a field or a section that every task carries.
- Seeding tasks from a register (the gaps, the pending tests).

## Rules

1. **Install it from the release binary through mise's `github:` backend, with an exact version and the executable renamed to `backlog`.** Example: `"github:MrLesk/Backlog.md" = { version = "<exact>", rename_exe = "backlog" }` in `mise.toml`; `mise.lock` records the checksum of each platform's binary. Observed on 2026-11-27 with Backlog.md 1.57.4: the release assets are one raw binary per platform (`backlog-bun-linux-x64` and others), and `backlog --version` printed the pinned version. The organization's fork is `cocreiamo/Backlog.md`; nothing is built from it yet.
2. **Initialize non-interactively with explicit flags.** Example: `backlog init Anima --defaults --integration-mode none --no-git --check-branches false --include-remote false --backlog-dir backlog --config-location root --task-prefix task --auto-open-browser false` wrote `backlog.config.yml` (statuses To Do, In Progress, Done; `auto_commit: false`; `filesystem_only: true`) and the folders under `backlog/`. Not: `--agent-instructions none` together with `--integration-mode none`; the command refuses ("Skipping AI integration cannot be combined with --agent-instructions"). Not: leaving git integration on; the tool could then commit, which this repository forbids to agents.
3. **Create a task with `backlog task create`.** Example: `backlog task create "Title" -d "why" -l label1,label2 --ac "test_R… exists" --ref gaps.toml --plain` wrote `backlog/tasks/task-<n> - <Title>.md` and printed its path. One `--ac` per acceptance line; a multi-line value needs real newlines.
4. **Read a task file as YAML front matter plus Markdown sections.** Keys written by the tool: `id` (`TASK-<n>`), `title`, `status`, `assignee`, `created_date`, `updated_date` (after an edit), `labels`, `dependencies`, `references`, `ordinal`. Sections the tool owns sit between HTML comment markers: Description (`SECTION:DESCRIPTION`), Acceptance Criteria (`AC`, lines `- [ ] #<n> <text>`), Implementation Notes, Final Summary.
5. **Add repository fields as extra front matter keys and extra sections after the tool's own.** Observed on 2026-11-27 with Backlog.md 1.57.4: two hand-added keys (`gap: …`, `role: …`) and two hand-added sections (`## Brief`, `## Report`) survived `backlog task edit` with a status change, an added label, notes, an added criterion and a final summary. Not: editing the text between the tool's own markers by hand; use the command.
6. **Run `backlog doctor` after seeding.** It reports duplicate ids, self-referential dependencies and cycles; it printed none for a probe task.
7. **Do not commit through the tool.** `auto_commit: false` and `filesystem_only: true` are the configuration; the repository's rule is that an agent never commits.
8. **A seeded task owns the paths where its acceptance is met, and its labels say whose remedy it is.** A task whose acceptance needs our code owns that code, not only `gaps.toml`; a task that writes tests owns `tests/**` and loads `anima-specifying-requirements`; the label `upstream` is for a remedy that is a contribution to another project, with its fork named or its project named, and a gap whose remedy is ours is labelled `gap` with its area; a defect of our own build is a task, never a gap. Not: one template for every register entry; it gave a task whose acceptance was the configurator's work the ownership of `gaps.toml` alone. A written test is not acceptance: seed from the pending list only.
9. Unverified: concurrent `backlog task create` from two processes (id assignment), the web and board commands (never run), moving a task between worktrees, and the ids after `backlog task delete`.

## Questions to answer before proposing

- Is the new field an extra key or section the tool keeps, and was that tried by running?
- Does a test read it, and does the model name that test?
- Does the command write only under `backlog/`?
- Is the task addressed by its id, the way the coordinator addresses work?

## Where the result goes

The rules for work are in `anima-working-as-an-agent`; the task template, the brief and report templates and the review checklist are in `docs/work/`; tasks are files in `backlog/tasks/`. Related skills: `anima-repository-conventions`, `anima-tech-mise`.
