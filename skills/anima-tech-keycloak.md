---
name: anima-tech-keycloak
description: "Use when writing or debugging the identity provider in Anima with Keycloak: the issuer URL, granting a scope per user through realm roles, realm import, health checks in its image, its database password, test tokens, and why keycloak-config-cli was retired."
family: technology
paths:
  - third_party/keycloak/**
  - engine/access/**
  - config/access/**
---

# Keycloak

How Keycloak, the adopted identity provider, behaves when run. What the product
wants of it is in `anima-access-design`.

## Use this when

- Setting the issuer a token carries, or debugging an "issuer mismatch".
- Declaring which user may obtain which scope.
- Importing a realm, or choosing how the realm is configured.
- Writing a health check or start order for its container.
- Connecting it to a database whose credentials change.
- Getting tokens in a test.

## Rules

1. **Set `KC_HOSTNAME` to the full public URL: scheme, host and port.** Observed on 2026-11-27 with Keycloak 26.8.2: the issuer in the discovery document and in tokens was exactly that URL plus the realm path, whatever name the request used. Example: `engine/configure/proof/pod.sh` passes `-e KC_HOSTNAME="$CFG_PUBLIC_URL"`, the configuration's one public URL. Not: the host name alone; the issuer changes with the port.
2. **Grant a scope per user declaratively with five parts together:** realm roles; client scopes with the attribute `include.in.token.scope = "true"`; realm-level `scopeMappings`, each tying a client scope to a realm role; the client lists those scopes under `optionalClientScopes`; users hold the realm roles. Observed on 2026-11-27 with Keycloak 26.8.2: a scope name with a colon (`anima:readonly`) is accepted. Example: `engine/configure/declarations/identity-provider.tf` (`include_in_token_scope = true`, `keycloak_generic_role_mapper`); the wiring is in `anima-tech-opentofu`.
3. **Check the `scope` claim of a decoded token in a test.** Not: expecting a user without the role to be told so; a scope assigned to the client is dropped silently from the token and the token request does not fail (GAP-043).
4. **Health check with bash on the management port.** The image has neither `curl` nor `nc`; enable health (`KC_HEALTH_ENABLED=true`) and use `bash -c "exec 3<>/dev/tcp/127.0.0.1/9000 && printf 'GET /health/ready HTTP/1.0\r\n\r\n' >&3 && grep -q UP <&3"` (`engine/access/access.container` has the command). Observed on 2026-11-27 with Keycloak 26.8.2. Not: `curl` or `nc` in a health command.
5. **Order its unit after the database server.** Keycloak exits when its database is not reachable, so its unit must start only after the database server is healthy (`anima-designing-for-production`). Not: relying on a restart policy to wait; the start order is declared, never obtained by restarts.
6. **Give it a static database role.** Not: a short-lived credential; Keycloak does not reload its database password while running and the credential cuts it off (GAP-017).
7. **Change the realm through the configurator, not through import.** Not: expecting `--import-realm` to apply a changed file; it imports only when the realm does not exist (`anima-tech-opentofu`).
8. **Do not reintroduce `keycloak-config-cli` beside another tool that owns roles.** Not: expecting it to repair drift; by default it skips a file whose checksum is unchanged, and in full management mode beside another configurator it deleted that configurator's roles (ADR 0006).
9. **Get test tokens with the password grant against a client with direct access grants enabled.** Create identities with a required action to set a password and no credential (`required_actions = ["UPDATE_PASSWORD"]`), so no password sits in a declared file.
10. **A scope that is not assigned to the client at all is refused, not dropped.** The token request fails with `invalid_scope`; only a user who lacks the mapped realm role loses the scope silently (GAP-043). Observed on 2026-11-27 in the proof of `engine/configure/`.
11. **An application authenticates as itself with client credentials and requests the scope of its roles itself.** The scopes are optional client scopes of its client, so a request without the scope gets none. Example: `engine/configure/declarations/identities.tf`. The secret of the client is derived from the root of trust, set write-only (`client_secret_wo`, GAP-052) and readable by an operator in the identity provider; its rotation is not built (TASK-71).
12. **The token validator identifies an identity by `preferred_username`, which people and applications both carry, not by the e-mail,** because a client's service account has none. Example: `engine/database/postgresql.conf`. Observed on 2026-11-27: an application's token opened a session as its role (`tests/system/test_tokens.py`). Unverified: a person's token.
13. **The management endpoint answers 400 to a request with no `Host` header once its host is set.** Example: the health commands of `engine/access/access.container` send `Host: 127.0.0.1`. Observed on 2026-11-27.
14. Unverified: running the server in production mode (`start`); the spikes and the proof of `engine/configure/` used the development mode of the image. Also unverified: tokens issued by a realm other than the one of the spikes, beyond the foreign-issuer refusal recorded in `anima-tech-postgresql-oauth`.

## Questions to answer before proposing

- What does the issuer look like when the port or the public name changes?
- Which realm role grants the scope, and which client may request it?
- How does a test prove the scope reached the token?
- Which tool owns the realm's roles, and is there exactly one?
- Does anything in the unit depend on a database password that rotates?

## Where the result goes

What the product wants is `anima-access-design` and ADR 0004; secrets are ADR 0003; the configurator that owns the realm is ADR 0006. Limits go to `gaps.toml` (GAP-017, GAP-043). Related skills: `anima-access-design`, `anima-tech-postgresql-oauth`, `anima-tech-opentofu`, `anima-designing-for-production`.
