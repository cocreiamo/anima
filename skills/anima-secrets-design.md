---
name: anima-secrets-design
description: "Use when changing anything about secrets, certificates, keys or unsealing: where a secret comes from, how it reaches its consumers, the secret store, the root of trust, or anything under engine/secrets/."
family: capability
paths:
  - engine/secrets/**
---

# Secrets design

Where secrets come from and how they reach their consumers: the capability
`secrets` (directory `engine/secrets/`). The decisions are taken; their home is
ADR 0003 (secret management). Who may connect and as what is
`anima-access-design`.

## Use this when

- Changing a secret, a certificate, a key or the unsealing of the secret store.
- Changing the secret store's declarative setup, or how a consumer receives a
  secret.
- Changing the root of trust or its adapters.
- Touching anything under `engine/secrets/`.

## Rules

1. **Secrets come from the secret store only** (R7). It generates them at first
   start and issues the certificates; a consumer receives a certificate and a
   credential and never learns the name of the product behind the secret store.
   Consumers get them from the secret store's agent units, rendered into shared
   in-memory volumes. A setting of the configuration names its secret, and the
   value arrives as a file from the host's secret mechanism (ADR 0007). Not: a
   secret value in a repository, an image, the configuration or a file on a
   volume. `gitleaks` runs in `check`.
2. **The secret store's setup is declarative.** It initializes itself once from
   declarative stanzas (policies, machine authentication, PKI, the database
   secrets engine) kept in `engine/secrets/`. Two first-start steps are not
   declarative, the generation of the seed values and the rotation of the
   management password, and they stay on the list of imperative steps to remove
   (ADR 0003, `anima-product-principles`). Not: a third one.
3. **Self-initialization runs once and cannot be repaired.** A failed one leaves
   the storage unusable (GAP-015), so a first start is repeatable from an empty
   state with the same command (R36) and nothing precious is in the secret
   store before the first start has succeeded. Its policies do not converge
   after first start (GAP-020): do not describe them as converged.
4. **The identity provider's service role has a static name**, `svc_idp`,
   whose password the secret store sets and rotates. Not: dynamic short-lived
   users, because Keycloak cannot reload its database password (GAP-017); say
   who restarts what when a secret rotates. The role's confinement to its
   database is `anima-access-design`.
5. **The root of trust is a port** that gives the secret store the key that
   unseals it, so that the system starts unattended (R26). The default
   adapter is an external key management service; the stand-in is a local key
   given by the host outside the configuration, for local development and CI.
   Design the default adapter first (ADR 0003).
6. **A key beside the data is not protection at rest.** The local key says so,
   and an installation that needs protection waits for a root kept apart
   (GAP-016).
7. **The secret store's API is loopback-only**, without TLS, and is never
   published (ADR 0005). It would otherwise need a certificate it issues itself.
8. **The state lies in the database server, and the seal is the
   protection.** The secret store keeps its sealed data in the database
   server, reached through the local socket with peer authentication, so no
   password exists for that connection (R62). What protects the secrets is the
   seal, not where the sealed data lies. One backup covers all state (R60,
   R20) and the root of trust is kept apart from it. The start order breaks the
   circle: the database server starts first and needs nothing (R61), the
   secret store then uses it, unseals and issues the server's certificate, and
   nothing is published before the configurator has run (ADR 0003). Not: a
   second store for the secret store's state.
9. **The secret store is three ports and one adapter fills them:** keeping
   secrets, the certificate authority and the credentials of the service
   roles (ADR 0001). The certificate authority is created by the secret
   store's own first-start initialization, never by the configurator, because
   a lost configurator state created a second authority silently (ADR 0006).
10. Unverified: **rotation over time.** It is outside the first release
    (ADR 0003); say so rather than implying it.
11. Unverified: **the production adapter of the root of trust.** The external
    key management service is not built (its cloud seals are GAP-016); the
    local key is the only one built, and no installation yet needs the
    protection the production adapter gives.

## Questions to answer before proposing

- Where is the new secret kept, who rotates it, and who reloads it?
- Does it ever sit in an image, a repository, the configuration or a file on a
  volume?
- What does the consumer receive, and does it name the product behind it?
- What happens on an empty system, and on a failed first start?
- Does it need the root of trust, and is the stand-in described as one?
- What does an upgrade do to the secret store's existing state?
- Which test, and which requirement (R-number), covers it?

## Where the result goes

A decision amends ADR 0003. The rule becomes a requirement and a test (see
`anima-specifying-requirements`). The secret store's declarative setup and the
root of trust's wiring live in `engine/secrets/`. Limits go to `gaps.toml`.
