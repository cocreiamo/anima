# Brief template

A brief is the whole instruction an agent gets for one task. It lives in the task file, under `## Brief`; the coordinator writes it, the role named in it reads it first. Copy the headings and fill every one; a heading that does not apply says "none".

```markdown
## Brief

Task: TASK-<n>, <title>. Role: <implementer | reviewer | spike | explorer>.

### Read first

- <the files, ADRs and registers this task depends on>

### Load these skills

- <skill names, derived from the paths the task will touch (the routing table in AGENTS.md)>

### Own these paths

- <the globs the agent may change; nothing else>

### Do not touch

- <paths another agent owns, generated files, lock files, third_party/>

### Acceptance

- <the verification names or explicit checks of the task, copied from its acceptance>

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

### Decision this serves (spike only)

- <the open decision, and what answer would change it>
```

Rules for the coordinator:

1. One task, one role, one set of owned paths. Two agents never own the same path at once.
2. The skills are derived from the paths, not from memory.
3. An instruction to an agent names the task id, never a hand-kept identifier of an agent.
