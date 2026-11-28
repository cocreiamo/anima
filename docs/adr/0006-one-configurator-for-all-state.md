---
number: 6
title: One configurator for all state
status: proposed
date: 2026-11-27
category: architecture
decision-makers: [founder]
---

# One configurator for all state

## Context and Problem Statement

`anima-product-principles` says that every place
that holds state has one declared file and one configurator that applies it at
every start, removals included. The identity provider had a configurator
(`keycloak-config-cli`); the database server's roles, privileges and
extensions and the secret store's policies had none chosen, and the secret
store's own self-initialization runs once only
(GAP-020). Several tools for several stores would mean several
declarations, and no single place to see what an installation is meant to be.

Which configurator applies the product's declarations and the adopter's
configuration to every store, at every start, and keeps the installation at its
declared state?

## Decision Drivers

- One declaration across all stores, applied at every start, removals included
  (`anima-product-principles`).
- It repairs drift on the objects it tracks, at every start, not only when a
  declaration changes.
- No network at run time, no secret in its state, and an identity that is
  wrong is refused before anything changes.
- An existing tool, not one of ours
  (`anima-repository-conventions`).

## Considered Options

- OpenTofu with three providers (database server, secret store, token issuer)
- An idempotent SQL file for the database server plus commands for the secret
  store
- Ansible `community.postgresql`
- `keycloak-config-cli` kept beside the chosen tool
- Atlas
- pgbedrock and pgperms
- pgroles

## Decision Outcome

Chosen option: "OpenTofu with three providers", because it is the only option
that gives one declaration across the database server, the secret store and
the token issuer, applied at every start, and that reverts drift on the
objects it tracks.

1. OpenTofu applies, at every start, the product's declarations and the
   adopter's configuration: one configurator, two inputs
   (`anima-configuration-design`). Its
   three providers are for the database server, the secret store and the
   token issuer. They are shipped components of `components.toml`, vendored
   with a lock file so that nothing is fetched at run time.
2. Its state lives in the database server, in its own `pg` backend, encrypted
   with a key derived from the root of trust
   ([ADR-0003](0003-secret-management.md)). No secret is in the state: secrets
   are given through write-only attributes.
3. An identity that names a role which does not exist is refused before any
   change.
4. The certificate authority is created by the secret store's own first-start
   initialization, never by the configurator: with a lost state the
   configurator created a second authority silently.
5. The guard for "expand only"
   (`anima-designing-for-production`) is a
   check on the planned actions: apply the previous release to throwaway
   containers, plan the new one, and fail unless the deletions equal the
   register `contractions.toml`. `prevent_destroy` protects against
   replacement but not against deleting the declaration. A narrowing in place
   is recognizable only with rules per type of object.
6. `keycloak-config-cli` is retired from the engine, from `components.toml`, the
   model, the ADRs and the skills; it stays only as a rejected option here.

Scope of the guardrails: they prevent leaving the declared state by accident.
Deliberate misuse by a holder of the superuser or of the root of trust is out
of scope.

### Consequences

- Good, because one tool and one declaration serve every store, so the
  installation is described in one place.
- Good, because drift on a tracked object is reverted at every start.
- Bad, because it sees only what is declared: a privilege granted by hand on
  something it does not track stays. "After an upgrade an installation equals a
  new one" therefore holds for declared objects only (R37).
- Bad, because with a lost or stale state it fails on existing objects instead
  of adopting them, so all state must be restored together: this is why all
  state lives in one store covered by one backup
  ([ADR-0003](0003-secret-management.md), R60).
- Bad, because the guard for "expand only" is a check on plans, not a property
  of the tool, and it needs per-type rules to see a narrowing in place.
- Bad, because the providers have defects that upstream could fix, registered
  in `gaps.toml` (GAP-026 to GAP-029); the contributions are to be proposed
  through our forks.
- Neutral, because a part of the guardrails does not stop a determined holder
  of the superuser or the root of trust.

### Confirmation

Verified by a spike on 2026-11-27, not by a test of this repository. Observed
with OpenTofu 1.13.10 and the providers cyrilgdn/postgresql 1.27.0,
hashicorp/vault 5.14.0 and keycloak/keycloak 5.11.0: a fresh installation of
54 resources in 8 s; a run with no change in 5 to 7 s; removals and hand-made
changes on tracked objects reverted; no network at run time, the providers
being vendored with a lock file; no secret in the state when write-only
attributes are used; an identity with an unknown role refused before any
change.

The configurator is written in this repository (`engine/configure/`: the
declarations, the run script, the image and the guard of deletions). Observed on
2026-11-27 in a pod of throwaway containers (the standalone proof, `mise run
engine:configure-prove`), which passed every one of its checks: a first run that
applies everything, a second run that changes nothing, hand-made changes on
tracked objects reverted, the state encrypted and holding no secret, and a failed
run that applies nothing and succeeds on the next. Observed on 2026-11-27 in the
engine by the system tests: the configurator runs as a unit with the superuser's
peer authentication and applies everything declared. Observed on 2026-11-28 with the
identity provider in its production mode: the configurator signs in as its own
client of the master realm, made at the first run with the temporary administrator
that the provider starts with, which it then deletes (R117). Written tests: R6, R7, R14, R22, R34, R36, R37, R39, R48,
R49, R63, R100, R101, R102, R104, R105 and R106 (the configurator's tests; those
that need the pod are skipped by `check`). Pending, not written: R43, R44 and the
rest of R7, R36 and R37 (see `tests/pending.toml`). Not run: an upgrade, because
no release exists to compare with, the rotation of credentials (a task is in the
backlog) and a token login of a person.

## Pros and Cons of the Options

### An idempotent SQL file for the database server plus commands for the secret store

- Good, because it handled more hand-made drift than the chosen option.
- Bad, because it is ours to maintain.
- Bad, because it gives no shared declaration across stores.

### Ansible `community.postgresql`

- Bad, because it was not run: no reason beyond that was recorded.

### `keycloak-config-cli` kept beside the chosen tool

- Bad, because by default it skips a file whose checksum is unchanged, so it
  does not repair drift at every start.
- Bad, because run beside OpenTofu in its full management mode it deleted
  roles that OpenTofu had created.

### Atlas

- Bad, because roles and permissions are a paid feature.

### pgbedrock and pgperms

- Bad, because they are dead projects.

### pgroles

- Bad, because it is months old and has one maintainer.

## More Information

The three forks `cocreiamo/anima-opentofu` and the
`anima-terraform-provider-*` forks exist but are not yet submodules. Until they
are, `components.toml` pins each component by the commit of the upstream
release tag, looked up with `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`.
OpenTofu and the postgresql and secret-store providers are MPL-2.0; the
token-issuer provider is Apache-2.0.
