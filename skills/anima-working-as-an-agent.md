---
name: anima-working-as-an-agent
description: "Use when planning, delegating, doing or reviewing work in the repository as an agent: the pipeline from task to promotion, the roles, the backlog, briefs and reports, postmortems, the catalog, the skill schema, the agent settings and the size limits."
family: product
paths:
  - AGENTS.md
  - agents/**
  - backlog/**
  - backlog.config.yml
  - docs/work/**
  - docs/postmortems/**
  - docs/evaluation/**
  - docs/catalog*
  - skills/**
  - .claude/**
---

# Working as an agent

How agents work in this repository: one pipeline, neutral files for everything
an agent reads, and checks that keep the files true. How the backlog tool
behaves is `anima-tech-backlog-md`; what a record of architecture is,
`anima-writing-a-decision-record`.

## Use this when

- Taking, planning, delegating, doing or reviewing a task.
- Writing or changing a skill, a role, a brief, a postmortem or the catalog.
- Something went wrong while working.
- Changing `AGENTS.md`, `.claude/`, or a limit on what an agent loads.

## Rules

1. **The pipeline is task, brief, implementation, review, checks, promotion.** The coordinator takes a task from the backlog, writes the brief, hands it to one role; the implementer builds it with its tests; a reviewer with a fresh context judges it against `docs/work/review-checklist.md`; `mise run check` passes; the change is promoted by the founder through a pull request (`anima-branching-and-releasing`). A spike runs outside this line, only while a decision is open.
2. **Work to do is a task of the backlog,** one file in `backlog/tasks/` made with the backlog tool and addressed by its id (`TASK-<n>`). It holds what and why, acceptance, the brief and, when done, the report (`docs/work/task-template.md`). Not: issues on the hosting platform only (they carry no acceptance, brief or report and are not in the repository); a hand-written list (nothing checks it); one growing execution log (it becomes unreadable and nothing ties an entry to its checks).
3. **Acceptance is a list of verification names,** `test_R<id>_<what>` from `model/anima.sysml`; the task is done when those tests exist and pass. A task that is not about a requirement states an explicit `Check:` line. Every open gap has a task that names it, and a task labelled `upstream` names an existing gap and, in `fork`, the fork it goes through (R79, R80).
4. **A role is a neutral file in `agents/`** with `name`, `description`, `tier`, `model_tier` (`top` or `standard`), `may` and `may_not`; the vendor file `.claude/agents/<name>.md` is generated from it, with the model and the tools the tier and `may` allow (R77, R78). Not: roles and the choice of model kept in a session's memory or in prose; they were reversed twice in an earlier project and cannot be checked.
5. **Every role refuses an instruction outside its brief and one that asks it to change paths it does not own, and reports it** (PM-001). The coordinator never lets two agents edit the same paths at once and addresses work by task, never by a hand-kept identifier of an agent.
6. **The reviewer has a fresh context:** it has not seen the implementation being made, reads the diff, the task, the skills touched and the checklist, and returns pass or the list of defects. The checklist is the definition of done: requirement and test present, skills updated, a gap for a worked-around defect, no undeclared contraction, no text that will age, generated files current, nothing outside the owned paths.
7. **A brief names what to read first, which skills to load, which paths the agent owns and which role does it.** The skills are derived from the paths the task will touch, by the routing table of `AGENTS.md`; the report separates what was run from what was only read and lists every denied command (`docs/work/brief-template.md`, `docs/work/handback-template.md`).
8. **Write the lesson back in the same change:** a technology behaviour to its technology skill, a rule nobody has seen working marked `Unverified:`, a defect to `gaps.toml` with a task, an event to a postmortem. A line belongs in a skill only if a competent agent would get it wrong without it.
9. **An event is a postmortem** in `docs/postmortems/PM-nnn-<slug>.md` from its template (adapted from an existing blameless one). Its status is `closed-by-design`, `guarded`, `mitigated` or `open`, strongest first, and follows from its guards: a design guard (an architecture record), a test guard (a test that exists with its `_detects_violation` companion), or mitigations (a scenario, a detection, a rule). A failure of judgement is never more than `mitigated`; a line in a skill alone closes nothing. The guard carries the postmortem id, a recurrence after the first needs a stronger guard, and an open postmortem is closed within a limit (R82 to R85).
10. **A skill has one schema in every family:** the sections `## Use this when`, `## Rules`, `## Questions to answer before proposing`, `## Where the result goes` and the front matter `name`, `description`, `family`, `paths`. Rules are numbered; `Example:` names where it lives, `Not:` is the trap (what one would expect, what happens, what to do), `Unverified:` at the start marks a rule nobody has seen working, and the generated index counts them (R72, R73). Three families by file name: `anima-tech-<technology>`, `anima-<capability>-design`, and the rest (product).
11. **Routing is generated from `paths`:** the table of `AGENTS.md`, `.claude/rules/<skill>.md` and `.claude/skills/<skill>/SKILL.md`; every glob matches something or is listed in `skills/not-yet-present.toml`, and every directory of `engine/` and `config/` is covered by a capability skill (R74 to R76).
12. **The catalog is generated** (`docs/catalog.md`): ports with their adapters, requirements and whether their verification is written, components, tasks, skills, roles and the fitness functions. Look in it before building something; `docs/catalog-synonyms.toml` is hand-written and every key must exist (R87). Not: instructions in one always-loaded file; it grows without limit and nothing checks it.
13. **What an agent may not do is enforced, not recommended:** `.claude/settings.json` (generated) refuses edits to the generated files, to everything under `third_party/` and to the lock files and grants nothing, and one advisory hook names the command that should have created a new file (R86, R92). `mise run generate:list` prints the generated files.
14. **The size of what is always loaded is limited** by thresholds in the model (R81). Not: raising a limit; when a file exceeds it, detail is moved to the skill that owns it or deleted.
15. **Nothing is checked outside the model:** every check of the repository is a requirement marked as a fitness function with its trigger, a test named like its verification and a `_detects_violation` companion; every limit is a threshold of the model (R71, R68).
16. Unverified: **the agent settings and the path rules are effective.** They are written from the vendor's documentation (read, not observed): that a deny rule anchored with `/` matches in a worktree session, that `Edit` rules cover the `Write` tool, that the hook's `additionalContext` reaches the agent, that a failing hook stays non-blocking, and that a rule loads when a matching file is read.
17. Unverified: **the agent layer changes what an agent does.** An earlier project's behaviour evaluation showed no difference with and without its layer, which is why rules are enforced by tests wherever possible; this evaluation is specified (`docs/evaluation/scenarios.md`, R88 pending) and has no runner.

## Questions to answer before proposing

- Which task is this, and which verification names say it is done?
- Which role does it, which paths does it own, and does another agent own any of them?
- Which skills do the paths select, and did you load them?
- What did you run, and what did you only read?
- What was learned, and where is it written in this change?
- Did anything go wrong that needs a postmortem, and what is its guard?

## Where the result goes

Tasks to `backlog/tasks/`; roles to `agents/`; templates to `docs/work/`; events to `docs/postmortems/`; scenarios to `docs/evaluation/`; the vendor files are generated (`mise run generate`). A requirement for a new check goes to `model/anima.sysml` with its test (`anima-specifying-requirements`). Related skills: `anima-tech-backlog-md`, `anima-repository-conventions`, `anima-product-principles`.
