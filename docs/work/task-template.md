# Task template

A task is one file in `backlog/tasks/`, created with `backlog task create` (`anima-tech-backlog-md`) and addressed by its id (`TASK-<n>`). Besides the tool's own keys it carries these:

```markdown
---
id: TASK-<n>
title: <what, in a few words>
status: To Do
labels:
  - <upstream | gap | pending-tests | founder | engine | ...>
gaps:
  - GAP-<nnn>
fork: <cocreiamo/anima-<name>, or none>
role: <implementer | reviewer | spike | explorer>
wave: <id in waves.toml, or none>
owns:
  - <path glob the task may change>
---

## Description

What and why.

## Acceptance Criteria

- [ ] #1 test_R<id>_<what>
- [ ] #2 Check: <an explicit check, for a task that is not about a requirement>

## Brief

(`docs/work/brief-template.md`)

## Report

(`docs/work/handback-template.md`, when done)
```

- Acceptance lines are verification names from `model/anima.sysml` (the task is done when those tests exist and pass) or begin with `Check:`.
- `gaps` lists the gap ids the task is about; an open gap has at least one task that names it.
- `fork` is set on a task whose remedy is a contribution upstream (label `upstream`).
