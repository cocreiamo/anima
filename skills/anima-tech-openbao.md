---
name: anima-tech-openbao
description: "Use when writing or debugging the secret store in Anima with OpenBao: declarative self-initialization stanzas, the static seal and unattended unseal, the database secrets engine against PostgreSQL, the PKI engine, running the container unprivileged."
family: technology
paths:
  - third_party/openbao/**
  - engine/secrets/**
---

# OpenBao

How OpenBao, the adopted secret store, behaves when run. What the product wants
of secrets is in `anima-secrets-design`.

## Use this when

- Writing or changing the `initialize` stanzas, the seal or the audit settings.
- Making the secret store start, unseal and configure itself with no human.
- Handing out database credentials, or issuing certificates.
- Choosing the storage of the secret store.

## Rules

1. **Declare the setup as `initialize` stanzas.** Example: `initialize "<name>" { request "<name>" { operation, path, data } }`; stanzas run in file order with a root token that is revoked afterwards; a value comes from the environment (`password = { eval_type = "string", eval_source = "env", env_var = "NAME", require_present = true }`) or a file (`eval_source = "file"` and `path = "…"`, for a policy). Observed on 2026-11-27 with OpenBao 2.7.3 (and PostgreSQL 18.7 for the database engine), in one file: policies from files, AppRole with a fixed role id and a custom secret id from the environment, a KV mount, a PKI mount with a root authority and a server role, the database secrets mount with a connection and a role. Example: `engine/secrets/openbao.hcl`.
2. **Validate the stanzas before shipping them.** Not: expecting a failed self-initialization to be retryable; there is no rollback, a failure leaves the storage unusable and the server refuses to unseal ("self-initialization failed: refusing to unseal"); start again from empty storage (GAP-015).
3. **Empty the storage before a start unless the first start is recorded as completed, and record it once the server answers.** An abrupt stop in the first start leaves one of three states, none repaired by the server: the key ring written and the seal configuration not (it never unseals), initialised and self-initialization not marked as started (it skips it for good and serves without the declared mounts and logins), marked as started and not finished (it refuses to unseal). Observed on 2026-11-28 with the pinned source (`internal/command/server.go`, `internal/vault/self_init.go`) by holding the write of each key with a trigger on the storage table and killing there: all three left the engine not ready. The listener starts only after self-initialization returns, so a healthy server whose storage was empty at this start has completed it. Example: `engine/secrets/first-start.sql` and the `ExecStartPre`/`ExecStartPost` of `engine/secrets/secrets.container` (PM-009). Not: relying on "runs once, on empty storage" to make a first start repeatable; nothing empties the storage unless the engine does.
4. **Do not expect the stanzas to run at every start.** They run once, on empty storage, and are not reconciled later, so a changed stanza does not reach an existing installation (GAP-020); what the configurator converges (policies, engines, roles) is outside the stanzas.
5. **Use an auto-unseal seal.** Example: `seal "static" { current_key_id = "…"  current_key = "file:///…/unseal.key" }` with a 32-byte key; after a restart, and after re-creating the container on the same volume, it came back unsealed. Not: self-initialization with a manual unseal, which it does not support; a static key on the same volume does not protect data at rest.
6. **Expect no recovery keys with auto-unseal.** A warning appears at every start; it is not a fault.
7. **Declare the database connection with `verify_connection = false`,** so the database need not be up at first start.
8. **Create dynamic database users that never block a drop.** Example: creation `CREATE ROLE "{{name}}" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}' IN ROLE <group>;` then `ALTER ROLE "{{name}}" SET role TO '<group>';` so objects belong to the group; revocation `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE usename = '{{name}}';` then `DROP ROLE IF EXISTS "{{name}}";`. The management role needs `CREATEROLE`, ADMIN OPTION on the group role, `CONNECT` and `pg_signal_backend`. Not: dynamic users for a service that cannot reload its password (GAP-017); use a static role. After `rotate-root` only the secret store knows the management password.
9. **Restrict a PKI role to subdomains of one domain.** Example: `allowed_domains = ["…"]`, `allow_subdomains = true`, `allow_bare_domains = false`, `allow_localhost = false`; it refused the bare domain, other domains and `localhost`.
10. **A snapshot of `sys/storage/raft/snapshot` applies only to the integrated storage, which the product does not use.** Its storage is the database server and its backup is the database server's (`anima-secrets-design`). Observed in a spike on 2026-11-27 with the integrated storage: restoring a snapshot needed `sudo` and the same seal key. Not: a snapshot of the secret store as the backup.
11. **Run the container unprivileged with all capabilities dropped.** It did so in the spike.
12. **Treat issuing a certificate and rotating a management password (as in the spike, with a password role) as API calls after start.** Not: expecting everything to be declarative; audit devices use the `audit` stanza, not self-initialization.
13. **Give the configurator its own machine authentication in a stanza file beside the main configuration.** Example: `engine/configure/secret-store-bootstrap.hcl`, mounted in the secret store's configuration directory, on its own mount, with the credential given as an environment variable. Without it the configurator cannot log in. Observed on 2026-11-27 in the proof of `engine/configure/` (a pod of throwaway containers, not the engine image).
14. Unverified: a cloud key-management seal. Cloud seals are external plugins fetched as images (read in the documentation, GAP-016). Also unverified: its PostgreSQL storage backend, and the agent sidecar's behaviour with consumers (read only).

## Questions to answer before proposing

- Is anything precious in the secret store before the first start has succeeded?
- Does the change need to reach an existing installation, given that stanzas run once?
- Who rotates the secret and who reloads it?
- Where does the seal key live, relative to the data?
- What did you run, and what did you only read?

## Where the result goes

What the product wants is `anima-secrets-design` and ADR 0003; the setup lives in `engine/secrets/`. Limits go to `gaps.toml` (GAP-015, GAP-016, GAP-017, GAP-020). Related skills: `anima-secrets-design`, `anima-designing-for-production`, `anima-tech-opentofu`, `anima-tech-keycloak`; `anima-repository-conventions` and `anima-product-principles` for how it runs and converges.
