---
name: anima-product-principles
description: "Use when taking or proposing any design decision on Anima, reviewing a proposal or ADR, or choosing between options, for any component: the product-wide criteria and the checklist of questions before proposing."
family: product
paths: []
---

# Anima product principles

The criteria behind every design decision on Anima, whatever the component. Each rule is checkable and states the principle; the detail lives in the skill named at its end.

## Use this when

- Taking or proposing any design decision on Anima.
- Reviewing a proposal, a pull request or an ADR.
- Choosing between options, including tools, names and scope.

## Rules

1. **The product is the paved integration.** Anima's contribution is adopted products configured to work together out of the box, specified, tested and released as one thing (README, ADR 0001). Not: rebuilding what an adopted product does.
2. **Adopt, never reinvent.** Look first for the official mechanism of something already adopted, then for an established tool; a script of ours is the last resort, a mise file task registered in `gaps.toml`. Not: the init container to generate secrets (ADR 0003). Detail: `anima-adopting-a-component`.
3. **Fork what we adopt, build from the fork, contribute upstream first** (`anima-maintaining-a-fork`). Not: "do not fork until there is a patch". Detail: `anima-adopting-a-component`.
4. **Contracts, not products.** A requirement states a capability and never names a product; a capability is a port with a standard contract and the product is an adapter, replaceable behind it wherever it runs; every port has one default adapter and one active, and every adapter passes the port's contract suite (R28, R58, R59). Detail: `anima-designing-a-port`.
5. **Agnostic by construction** of vendor, of machine and of build system. To boot the image nothing else is assumed; to run it as a container only an engine with no daemon and no root (R29). Not: a test that needs a Docker socket; `rules_oci` (rejected, `anima-repository-conventions`). Detail: `anima-designing-for-production`.
6. **Production is the default environment.** Local development replaces a production dependency with a stand-in behind the same port. Not: designing the local path first and hardening later.
7. **Code is static; an installation is a flow of physical data with a history.** What ships in an image is replaced by an upgrade; what lives in a volume must converge at every start; after an upgrade an installation equals a new one. A mechanism that runs only on an empty system is suspect (rule 14).
8. **Security by design.** Closed by default; least privilege through the platform's own mechanisms (ADR 0004); no secret in a repository or an image (R7); every known trap gets a test that forbids it (R34); a protection that does not protect is named as such (ADR 0003).
9. **Everything as code, everything verified.** Requirements are a formal model; every rule a machine can check becomes a test; flows and drills are tests; a claim about a tool is verified by running it before it is recommended.
10. **Decide now, in writing.** No "to be confirmed later". What is decided but not built is an `Unverified:` rule in a skill or an ADR status, never described as existing (`tests/pending.toml`).
11. **Single source of truth.** Each fact is declared in exactly one place; every other occurrence is derived from it or checked against it by a test (R39, `anima-configuration-design`). Example: the fixed roles, the identity provider's public URL. Not: the same role name typed into four files. The homes are the table in `AGENTS.md`.
12. **Declarative over imperative.** Whatever can be declared as data is declared; an imperative step is an exception, listed and to be removed (ADR 0003). Not: roles created by a first-start script.
13. **Generated over hand-written.** Whatever can be derived from another file is generated, committed so that a reader sees it, and fails the checks when stale (R38). Not: an index kept by hand. Detail: `anima-repository-conventions`.
14. **Converge, do not initialize.** Every place that holds state has one declared file and one configurator that applies it at every start, removals included (R37, ADR 0006). Not: `docker-entrypoint-initdb.d`. Detail: `anima-designing-for-production`.
15. **Never serving in an inconsistent state.** The system accepts work only after it has converged and that has been checked; a start that cannot converge stays not ready and closed (R40).
16. **One start path, also after a crash.** Starting after an abrupt stop is a normal start; there is no repair script or recovery mode (R42).
17. **Expand only.** A new version adds and never removes or narrows what a released version provided (R43). Detail: `anima-designing-for-production`.
18. **Declared and tested upgrade paths.** The supported versions are declared and each path is a test (R46). Not: an upgrade supported because nobody said otherwise.
19. **Reproducible builds.** The same pinned sources produce the same image, bit for bit, so that "build once, promote the artifact" (`anima-branching-and-releasing`) can be checked by rebuilding (R47).
20. **The composition names the adapters, not the database server.** The server knows ports; adapters are named only by the engine's composition (ADR 0001). Detail: `anima-database-design`.
21. **SOLID, read at the level of the system.** One default adapter per port, alternatives selectable with exactly one active (an adapter may fill several ports), and one tool per concern; Anima grows by adding ports, adapters and plugins, never by modifying the database server (ADR 0002); a port is a narrow, standard contract. Detail: `anima-designing-a-port`.
22. **Fail closed.** When something is wrong the system refuses rather than degrades: a check fails on a warning, a stale lock file is an error, a role without the scope is refused (R34). Not: a warning that is only printed.
23. **History is immutable.** Forks are merged, never rebased; a published tag is never moved; a requirement id, a gap id or a postmortem id is never reused; a closed gap stays in the register.
24. **Exactly one.** One entry point (`mise run`), one declaration of the engine's units, one default adapter per port, one home per kind of fact, one tool per concern, one way to run the system, one container engine family with no Docker. Start order is declared in the units, never obtained by restarts. Detail: `anima-image-design`.
25. **Unattended at run time, deliberate at design time.** Start, restart, unlock and renewal need no person (R26); decisions, version bumps and releases are made by a person through a pull request.
26. **Convention over invention.** Files and directories take the name and place their ecosystem expects (`third_party/`, `mise-tasks/`, `CODEOWNERS`). Not: a `tools/` directory.
27. **The test is the judge.** "Ready", "compatible" and "restorable" mean that a named test passed, not that a component said so (ADR 0005). Not: a health check taken as proof.
28. **Names tell the truth.** Functional and unbranded: no product prefix on roles, scopes or files; a name that says one thing and means another is a defect to fix at once.
29. **Pin everything.** Exact version plus digest or commit, never `latest` (R11); updates are deliberate (`anima-maintaining-a-fork`).
30. **Lean, but guardrails first.** Nothing speculative; yet what we need on Day 2 is adopted on Day 0 when cheap: the configurator, release tooling, the gap register.
31. **Maturity and governance count.** A young tool loses to the reference implementation; governance risk is recorded, not ignored; an excluded licence ends the discussion (`anima-licensing-and-brand`).
32. **Organized by capability, not by product.** Directories, configuration and names follow the capability, so that replacing a product renames nothing (R54).
33. **Two layers, two owners.** The engine is the product's and changes with a release; the configuration is the adopter's, public, validated before ready, product-neutral, free of secrets and expand only. Detail: `anima-configuration-design`.
34. **Close classes of bugs by design.** Prefer a design in which a kind of error cannot happen over a check that catches instances of it: access rules rather than grants; derived files generated; a fact declared once; versions pinned by digest.
35. **A spike answers a question that can change a decision; otherwise the implementation is the verification.** What a spike found goes into the repository as evidence; what worked is promoted, not rewritten. Decide at once from what is known; the unknown is the first test of the task (`anima-working-as-an-agent` rule 19). Detail: `anima-adopting-a-component`, role `spike`.
36. **Texts that do not age** (R57): the rule is in `anima-specifying-requirements`.
37. **Every setting has a production default; local is an overlay, never a copy** (R65, R66, ADR 0007). Detail: `anima-configuration-design`.
38. **Guardrails stop accidents, not a determined owner.** Deliberate misuse by a holder of the superuser or of the root of trust is out of scope; say so rather than claim otherwise (ADR 0006).
39. **Knowledge, defect, event: three homes.** How a technology behaves goes to its technology skill; a defect of a technology goes to `gaps.toml`; an event, something that went wrong, goes to a postmortem in `docs/postmortems/`, closed only by a protection that exists. Not: a lesson left in a conversation or only in a commit message.
40. **Write the lesson back in the same change.** What an agent learned while doing a task goes to the skill, the gap or the postmortem it belongs to before the task is done; the review checklist asks for it (`docs/work/review-checklist.md`).
41. **Write three orders of consequences.** For every decision: first, what it does; second, what it forces elsewhere (start order, who holds which secret, what must restart); third, what happens over time and across the installed base. Example, the fixed roles (ADR 0004): created at first start; a script runs only on an empty system; version N+1 changes a role and existing installations never receive it; so the roles are declared as data and applied at every start.
42. **Architecture in records, everything else in skills.** `docs/adr/` holds only decisions about the architecture of the product (R93, R94). Detail: `anima-writing-a-decision-record`.

## Questions to answer before proposing

- Where is this fact declared, and what derives from it or is checked against it? Can it be declared instead of scripted, or generated?
- Which configurator converges it at every start, removals included? Can a client observe it half-done?
- Does it remove or narrow anything a released version provided? From which versions can an installation reach this one?
- Empty system, restart, failure half-way, upgrade, crash: does each reach the declared state with no human step?
- Created later: does the rule hold for a database, role or identity created after installation?
- Restore: can it be rebuilt on another machine from the backups and the root of trust (R20)? Expiry and rotation: who reloads a changed secret?
- Is this decision still open? If not, why is this a spike rather than the implementation?
- Replacement: can the adapter be swapped without touching a requirement, and does every adapter pass its contract suite?
- Does a text I write state a version or a number that a register or the model already holds?
- Default: is there a production default, and is local an overlay? Exposure: what is reachable by default (R30)?
- Order and checks: which units must it follow, and what do its startup, liveness and readiness checks check?
- Is there a design in which this error cannot occur at all? Owner: is the fact the engine's or the configuration's, and not both?
- Evidence: which test proves it, and if none, is it listed as pending?

## Where the result goes

A decision about the architecture goes to a record in `docs/adr/`, and any other decision to the skill that owns it (`anima-writing-a-decision-record`); one recommendation, then the founder's decision, then build. A rule a machine can check goes to `model/requirements/` with its test. A limit found in an adopted product goes to `gaps.toml`; how a technology behaves to its technology skill; an event to `docs/postmortems/`; work to do to the backlog. An unwritten test is listed in `tests/pending.toml`, which is generated.
