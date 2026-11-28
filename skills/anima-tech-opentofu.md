---
name: anima-tech-opentofu
description: "Use when writing or debugging the configurator in Anima with OpenTofu and its PostgreSQL, secret-store and identity-provider providers: the unattended run, offline provider mirror, state in PostgreSQL, state encryption, write-only secrets, the adopter's identities file, stale state, destroy protection and the plan guard."
family: technology
paths:
  - "**/*.tf"
  - third_party/opentofu/**
  - third_party/terraform-provider-postgresql/**
  - third_party/terraform-provider-vault/**
  - third_party/terraform-provider-keycloak/**
---

# OpenTofu, the configurator

How OpenTofu behaves as the unattended configurator of a running engine. The
decision it implements is ADR 0006; the product's rules are in
`anima-designing-for-production`.

## Use this when

- Writing or changing a `.tf` file of the configurator, or the script that runs it.
- Building the configurator image so that it needs no network.
- Reading an adopter's file of identities into resources.
- Deciding how to keep a secret out of the state, or how to key the state.
- Reviewing a plan for deletions.

## Rules

1. **Run unattended with a saved plan.** Example: `engine/configure/converge.sh` runs `tofu init -input=false -lockfile=readonly`, then `tofu plan -detailed-exitcode -out=plan.bin`; apply that plan only when the exit code is 2 (changes); 0 means converged, non-zero means failed. With a target down it fails and applies nothing; the next run succeeds. Observed on 2026-11-27 with OpenTofu 1.13.10 and the providers PostgreSQL (cyrilgdn) 1.27.0, Vault 5.14.0 (used against OpenBao) and Keycloak 5.11.0.
2. **Mirror the providers at build time so the run needs no network.** Build time: `tofu providers lock -platform=linux_amd64 -platform=linux_arm64` and `tofu providers mirror <dir>`, with `.terraform.lock.hcl` committed for both architectures; run time `tofurc` is only `provider_installation { filesystem_mirror { path = "…"  include = ["registry.opentofu.org/*/*"] } }`.
3. **Copy the binary into a small base.** Example: `COPY --from=<opentofu image>-minimal /usr/local/bin/tofu …`. Not: using the official image as a base; an `ONBUILD` step fails on purpose, by upstream's design (GAP-030, closed: not a defect).
4. **Keep state in PostgreSQL.** Example: `engine/configure/declarations/providers.tf` has `backend "pg" { schema_name = "configurator" }` and the connection string comes from `PG_CONN_STR`; the backend creates its own schema and table; the only bootstrap outside it is the superuser. Not: expecting an older state row to be refused; it is accepted without any warning (GAP-040). Lost or stale state is not self-healing: roles, mounts and the realm fail with "already exists", policies and connections are silently overwritten, and a certificate authority created by the configurator was silently duplicated; create it elsewhere, once.
5. **Encrypt state and plan, and enforce it.** Example: `engine/configure/declarations/state-encryption.tf`, a `pbkdf2` key provider and an `aes_gcm` method, `enforced = true` for state and plan; the passphrase is derived from the root of trust, so whoever loses it loses the state. Not: a key provider that depends on the secret store, for the run that configures the secret store; it fails before planning (GAP-041). Key the state from something that exists before.
6. **Keep secrets out of the state with write-only attributes and ephemeral variables.** Example: `engine/configure/declarations/identities.tf` sets `client_secret_wo` with `client_secret_wo_version` on a confidential client. Not: a plain `password` or `initial_password`; it is persisted, so forbid them. Not: a confidential client without the write-only attribute; the provider persists its generated secret in the state, also with the signed-token authenticator (GAP-052).
7. **Read the adopter's file with `yamldecode(file(var.identities_path))` feeding `for_each`, and refuse early.** Example: `lifecycle { precondition { … error_message = "identity '${each.key}' has unknown role(s) …; allowed roles are …" } }` fails at plan time, before any change, naming the identity and the allowed roles.
8. **Give a role ADMIN OPTION on another with `ignore_changes`.** Example: `lifecycle { ignore_changes = [roles] }` on the role, a separate `postgresql_grant_role` with `with_admin_option = true`, and a `moved {}` block when an existing resource changes address. Not: `roles` on a role together with a grant-role resource on the same role; they flap forever and ADMIN OPTION cannot be stated in `roles` (GAP-027).
9. **Forget without destroying with `removed`.** Example: `removed { from = <address>  lifecycle { destroy = false } }`. Not: expecting `prevent_destroy` to protect a resource; it stops a change that forces replacement, not the deletion of the resource block.
10. **Read a plan with `tofu show -json plan.bin` and guard deletions.** `resource_changes[].change.actions` is create, update, delete or replace per resource and `resource_drift[]` lists changes made outside; a guard fails when deletions are not equal to a declared list. Not: expecting it to catch narrowing; an in-place narrowing (a list that loses an element) needs per-type rules.
11. **Write durations in seconds for the secret-store provider.** Not: "720h"; it gives a perpetual difference (GAP-028).
12. **Use the Vault provider against OpenBao.** Not: looking for a provider for OpenBao; none is published (GAP-042).
13. **Do not plan on a data source for databases, nor on declared imports.** There is no data source for databases, so a grant made by hand on a pair with no resource is invisible to the plan (GAP-026); roles, scopes, clients and users need internal ids, so a static `import` block cannot name them (GAP-029).
14. **Use the identity-provider resources that worked:** realm, realm roles, client scopes, `keycloak_generic_role_mapper` (role to scope), a public client with optional scopes, users with required actions, `keycloak_user_roles` (exhaustive).
15. **Reach the database server's socket with an empty host and `PGHOST`.** Example: `engine/configure/declarations/providers.tf` sets `host = ""` and `converge.sh` sets the socket directory. Not: looking for a socket setting; the PostgreSQL provider has none (GAP-051).
16. **An `import` block with `for_each` does nothing once the resource is in the state,** so it can adopt objects that exist before the configurator (the secret store's two database roles) without a second effect. Observed on 2026-11-27 in the proof of `engine/configure/`.
17. **The minimal binary image needs a temporary directory for the provider plugins, and a read-only root works with podman secrets only when `/run/secrets` is a temporary filesystem.** Example: `engine/configure/proof/pod.sh` runs the container with `--read-only --tmpfs /tmp --tmpfs /run/secrets` (GAP-031). Not: a read-only root without those filesystems.
18. Unverified: **the configurator in the engine image.** It was proven in a pod of throwaway containers (`mise run engine:configure-prove`; that proof was updated for the temporary administrator on 2026-11-28 and not run again). Observed on 2026-11-28 in the engine image: the configurator applied everything against the identity provider in its production mode, signing in as its own client of the master realm (client credentials, `KEYCLOAK_CLIENT_ID` and `KEYCLOAK_CLIENT_SECRET`; the provider block names no client), and token logins of an application and of a person worked. Also unverified: other providers than the three named, other backends than `pg` and `local`, and a run against a secret store that stores its data in PostgreSQL.

## Questions to answer before proposing

- Does the run apply only a saved plan, and fail closed when the target is down?
- What keys the state, and does it exist before the run that needs it?
- Does any secret reach the state, and is the attribute write-only?
- What does the plan guard compare deletions with?
- What did you run against a real target, and what did you only read?

## Where the result goes

The decision is ADR 0006 (one configurator for all state), with `anima-product-principles` (declared once) and ADR 0003, ADR 0004 for what it applies. Provider and tool limits go to `gaps.toml` (GAP-026 to GAP-031, GAP-040 to GAP-042, GAP-051 to GAP-053). Related skills: `anima-designing-for-production`, `anima-secrets-design`, `anima-access-design`, `anima-tech-keycloak`, `anima-tech-openbao`.
