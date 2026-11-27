---
name: anima-designing-for-production
description: "Use when designing anything that touches a running Anima installation (first start, upgrade, configuration, backup, data, start order, readiness, the engine image) or writing the engine's units or anything under engine/ or config/."
family: product
paths: []
---

# Designing for production

How to design anything that touches a running Anima installation. The engine
image itself is `anima-image-design`; backup and the database server are
`anima-database-design`.

## Use this when

- Designing a first start, an upgrade, a configuration, a start order, a readiness check or any data in a volume. For the secrets and the roles in them, see `anima-secrets-design` and `anima-access-design`.
- Writing the engine's units (Quadlet), its container file, or anything under `engine/` or `config/`.
- Writing a flow or a drill (start, backup and restore, upgrade) as a test.

## Rules

1. **Production is the default; local is the special case.** Describe the production path first. A local stand-in sits behind the same port and is named a stand-in (a local key instead of the production adapter, an external key management service, ADR 0003). Not: a local script made to work first and hardened later.
2. **Separate what is in the image from what is in a volume.** An image is replaced by an upgrade. A volume (the database server's data, the secret store's storage) carries roles, privileges, identities, policies and installed extensions, and survives the upgrade (ADR 0005: one volume of state).
3. **Every place that holds state has one declared file and one configurator that applies it at every start, removals included.** The first start is only the first convergence (`anima-product-principles`). Example: the fixed roles of ADR 0004 are declared once and applied at each start. Not: roles created only by a `docker-entrypoint-initdb.d` script, which runs only on an empty data directory and never reaches an existing installation; a new first-start script. The configurator is one for all state (ADR 0006); it sees only what is declared, so with a lost or stale state it fails rather than adopts. Guardrails stop accidents, not a determined owner: deliberate misuse by a holder of the superuser or of the root of trust is out of scope, and the text says so.
4. **Upgrade equals new installation.** After an upgrade an installation must equal a new installation of the same version (R37); write that as a test. Removal of a privilege is part of an upgrade: converge by revoking, not only by granting. A crash is not a special case: starting after an abrupt stop, even in the middle of a first start or an upgrade, is the normal start with the same command (R42).
5. **Expand only (`anima-product-principles`).** A new version adds; it does not remove or narrow a role, privilege, scope, database, installed extension or installation parameter that a released version provided, so version N+1 runs on what N left and going back is possible (R43). A thing that holds data (a database, a volume, the secret store's mounts) is never removed by an upgrade: the configurator's own guard forbids it (R44). Any other contraction is declared in `contractions.toml` (what, why, deprecated in, removed in), is a breaking change, and is allowed only for what a released version already deprecated. Upgrade paths are declared (only from the previous released version, to start with) and each is a test (R46); the declaration is that rule itself, with no separate file until a second path exists. The register of contractions is built and empty, and its fields are checked by R45. Not: a role narrowed in a new version with no entry in the register.
6. **Start unattended, in a declared order.** No human step at first start (R26) or at restart: the secret store unseals itself from the root of trust given at installation. The start is one command of a container engine that needs no daemon and no root, or the boot of the image, ready within the limit of R9. Start order is declared in the units (`After=`, `Requires=`), never obtained by restarts. Not: a container that exits until what it needs exists; a "wait for" script.
7. **A first start is repeatable.** A failed first start is repeated from an empty state with the same command (R36). The secret store cannot repair a failed self-initialization (GAP-015), so nothing precious may be in it before the first start has succeeded, and its configuration is validated in continuous integration.
8. **Closed by default.** Two installation parameters only: the identity provider's full public URL (no default) and the listen address (default `127.0.0.1`) (R30). The public URL is the issuer and resolves inside the pod through a host alias that is a setting of the units (ADR 0005). A new parameter is a new decision. Each parameter is declared once; the hostname, the issuer, the certificate name, the host alias and the published ports are derived from it (`anima-product-principles`).
9. **Converge, then become ready; one readiness answer.** The configurator is a unit that runs to completion at every start and the units that serve are ordered after it; nothing is published and no connection is taken from outside until every place that holds state has reached its declared state; a start that cannot converge stays not ready and closed (R40). Every unit that runs a container declares startup, liveness and readiness as health settings (R41). The engine's one readiness answer is a target reached only when every unit is active and healthy and the configurator has succeeded; a system test that performs a real token login within the time limit of R9 shows that the answer is honest. Not: a unit that serves while it is still converging; a readiness answer nobody tests. Validate the units without starting them (R52).
10. **Build once, promote the artifact.** Images released are the ones built and verified in the promotion run, identified by digest; environments run released versions only, never a branch or commit (`anima-branching-and-releasing`). A release build restores no cache.
11. **The root of trust is kept apart from the backups** (`anima-secrets-design`). A key stored beside the data it encrypts does not protect it, and the document says so; whoever installs keeps the generated key elsewhere (ADR 0003).
12. **Drills and flows are code.** No runbook in prose stands in for a test. A system test starts the engine image with Testcontainers through podman's API service (`tests/system/`).
13. **Nothing depends on the host** (R29). When the image runs as a container, only a container engine that needs no daemon and no root; when it is booted, nothing. No host podman version, no host `/etc/hosts`, no host package, no Docker, no orchestrator.
14. **Two layers, two owners** (ADR 0001, `anima-product-principles`). The engine is the product's and lives in the engine image; the adopter's configuration lives outside it, in a mounted directory. Each fact has one owner. The configuration is validated before ready (R48), names no adapter (R49), holds no secret (R7), and a new version accepts every configuration the previous one accepted (R43). Not: a setting that an adopter must change inside the image.
15. **Secrets never sit in an image, a repository or the configuration** (R7). How they are generated and delivered, and what rotation needs, is `anima-secrets-design`; say who restarts what when one changes.
16. Unverified: **the start, order and readiness of the engine as designed.** Decided in ADR 0005 and not built end to end: in a spike the declared order and the gate worked, but the health checks inside the nested container did not (GAP-034), so do not claim the health settings work.
17. Unverified: **the check of expand only.** The comparison of what a new version would remove from an installation of the last released version with `contractions.toml`, a check on the configurator's planned actions (ADR 0006), is not built, nothing before the first release can be compared, and upgrades are outside the first release (ADR 0005).
18. Unverified: **the configurator.** ADR 0006 decides it and nothing of it is built; do not describe a converged installation as existing.

## Questions to answer before proposing

Answer in three orders (`anima-product-principles`): what it does, what it forces elsewhere (start order, who holds which secret, what restarts), what happens over time and across the installed base. Then:

- Empty system: does it start unattended from nothing? Restart: does it come back with no human step? Crash: is a stop at any moment recovered by the same command?
- Failure half-way: is the first start repeatable? Half-done: can a client observe it?
- Order and checks: which units must it follow, and what do its startup, liveness and readiness checks check?
- Declared: where is the fact declared, what derives from it, and which configurator converges it?
- Upgrade: how does each existing installation reach the new state, including a privilege taken away? Does it remove or narrow anything a released version provided? From which versions, and which test covers each path?
- Created later: does the rule hold for a database, role or identity created after installation?
- Restore: can it be rebuilt on another machine from the backups and the root of trust?
- Expiry and rotation: when a secret or certificate changes, who reloads it?
- Replacement: can the adapter be swapped without touching a requirement? Exposure: what is reachable by default?
- Evidence: which test proves it, or is it listed as pending?

## Where the result goes

The decision goes to an ADR (ADR 0005 covers the engine image); the rule to `model/anima.sysml` with its test in `tests/system/`; a missing test to `tests/pending.toml`, which is generated; a limit of a platform to `gaps.toml`. What is decided but not built is an `Unverified:` rule, never a statement of fact.
