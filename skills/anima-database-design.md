---
name: anima-database-design
description: "Use when changing the database server of Anima, the adapters that run inside its process (token validation, vector search, backup and restore) or anything under engine/database/, engine/backup/ or engine/vectors/."
family: capability
paths:
  - engine/database/**
  - engine/backup/**
  - engine/vectors/**
---

# Database server design

The capabilities `database`, `backup` and `vectors` (directories
`engine/database/`, `engine/backup/`, `engine/vectors/`): the build of the
PostgreSQL fork and the adapters that run in its process. The decisions are
taken; their home is ADR 0001. Who may connect is `anima-access-design`.

## Use this when

- Changing the database server's build, its configuration or its container file.
- Adding or changing an adapter that runs in the database server's process.
- Changing backup, restore or the vector extension.
- Touching anything under `engine/database/`, `engine/backup/` or `engine/vectors/`.

## Rules

1. **The database server knows ports, never adapters.** The configuration that loads an in-process adapter belongs to the engine's composition; a product name in the server's own configuration is a fault (ADR 0001, R8). Check with a search of `engine/database/` for any adapter's product name.
2. **An in-process adapter is built into the server's image, from a pinned fork.** Token validation and vector search run in the server's process, and the backup program inside its container, invoked by it; they are adapters all the same (`anima-maintaining-a-fork`).
3. **The server starts without the identity provider and serves without the secret store.** It needs neither to start (R13, R61); its certificate comes from the secret store when that is up (`anima-secrets-design`).
4. **One backup of the database server covers all state** (R20, R60): it includes the identity provider's database and the secret store's sealed data; the root of trust is kept apart. The restore is proven by a drill run as a test, from the backup plus the root of trust into an empty system, with the same logins.
5. **Vector search is created in the template database,** so it is in every database (R19). The extension is part of the declared state, not of a script.
6. **A new database is closed by access rules, not grants:** the rule is in `anima-access-design`.
7. Unverified: **backup and restore.** The backup adapter's PostgreSQL support is to be confirmed by our own restore test (R20, GAP-009), and no restore drill exists yet.
8. Unverified: **vector search in every database.** The declaration that creates the extension in the template database is designed, and no test shows it in a database created later (R19).
9. **The database server runs inside its envelope with settings derived from it** (`engine/image/envelopes.toml`, R205): shared buffers and maintenance memory as shares of the memory limit, a modest connection limit that the identity provider's pool fits, written at every start into a file that `postgresql.conf` includes (`include`, not `include_if_exists`: a server that starts without them would run with the defaults of a large machine). To be observed under load: the starting size is the founder's, not a measurement of load.

## Questions to answer before proposing

- Does the server's own configuration name a product?
- Which state does the change add, and is it in the backup?
- Does it need the identity provider or the secret store to start?
- Does the restore drill still pass?

## Where the result goes

A decision amends ADR 0001; the fork rules are `anima-maintaining-a-fork`. The files live in `engine/database/`, `engine/backup/` and `engine/vectors/`; the component goes to `components.toml`; limits to `gaps.toml` (GAP-009). Related skills: `anima-access-design`, `anima-designing-for-production`, `anima-tech-postgresql-oauth`.
