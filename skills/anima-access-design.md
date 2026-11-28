---
name: anima-access-design
description: "Use when changing who can connect to the Anima database server and as what: roles, pg_hba.conf, scopes, tokens, access rules, the identity provider's wiring, the identities file, or anything under engine/access/ or config/access/."
family: capability
paths:
  - engine/access/**
  - config/access/**
---

# Access design

Who may connect to the database server and as what: the capability `access`
(directories `engine/access/` and `config/access/`). The decisions are taken;
their home is ADR 0004 (roles and access). Where a secret or a certificate is
involved, the rule is in `anima-secrets-design`.

## Use this when

- Changing roles, `pg_hba.conf`, `pg_ident.conf`, scopes or tokens.
- Changing the access rules or the closing of a database.
- Changing the identity provider's wiring, its configuration, or the identities
  file and the roles the identities hold.
- Touching anything under `engine/access/` or `config/access/`.

## Rules

1. **From outside, only TLS and only tokens.** From outside the pod the database server
   accepts only TLS connections authenticated by token (R15, R4). A password is
   accepted nowhere from outside.
2. **A service role is never reached by token and never from outside the
   engine.** A role whose name begins with `svc_` authenticates, from inside,
   by password on the pod's loopback (the roles of components that speak the
   database protocol over TCP: `svc_idp`, `svc_backup`) or, for the secret
   store's two roles `svc_secrets_store` and `svc_secrets_manage`, by
   operating-system peer authentication over the local socket with no secret and
   no password; no rule accepts a token for it (R31). The `svc_`
   prefix states the kind, not the brand.
3. **The roles are fixed.** Token roles: `admin` (creates databases and roles;
   not a superuser), `readwrite`, `readonly`, `monitor`. The last three are
   login roles that are members of PostgreSQL's predefined roles
   (`readwrite`: `pg_write_all_data` and `pg_read_all_data`; `readonly`:
   `pg_read_all_data`; `monitor`: `pg_monitor`), so the database server's own privilege
   system does the work. Service roles: `svc_idp`, `svc_backup`, `svc_secrets_store` and
   `svc_secrets_manage`. Not: a grant
   written per database.
4. **`postgres` only through the local socket**, inside the database server's container,
   peer authentication, no password (R12). The configurator is the one other caller: it runs as the operating-system user of the same name inside the pod and reaches the superuser on the socket by peer authentication.
5. **One access rule per token role**, requiring a scope with the same name as
   the role and delegating the mapping to the validator. The database server keeps no
   per-user list: the one mapping of `pg_ident.conf` is the secret store's
   operating-system user to `svc_secrets_store`, none concerns a person.
6. **Scopes are granted in the identity provider only to the holders of the
   matching realm role.** So who may assume which role is declared only in the
   configuration's identities file (R22), never in the database server.
7. **The person stays identifiable.** The session's `system_user` is the
   token's identity, so an audit names the person although the session runs as
   a shared role. Statement logs carry only the role (GAP-014).
8. **Close a database with access rules, not with grants.** PostgreSQL grants
   `CONNECT` on a new database to everyone, so a grant must be remembered for
   every later database. The `idp` database is closed in `pg_hba.conf`, in this
   order: admit `svc_idp` into `idp` from the loopback; `reject` every other
   role from `idp`; no rule admits `svc_idp` anywhere else (R27, R32). A test
   verifies the order, and the rules hold for databases created later.
9. **The identity provider's service role is confined here.** `svc_idp` is a
   static name that may enter only the `idp` database (rule 8). The role's
   password belongs to `anima-secrets-design`.
10. **Role scopes go only to the engine's own client and to declared
    applications**, because the validator does not check the audience
    (GAP-006). The scope acts as audience (R33, R102). Not: granting a role
    scope to another client of the realm.
11. **A rule that accepts tokens never has an empty scope** (R34): with
    delegated mapping an empty scope would admit any valid token of the issuer
    (GAP-011). A test on our configuration forbids it.
12. **The names are reserved.** Creating a role with a fixed name, or
    importing identities that bring one, fails and says which name conflicts
    (R35). The names are unbranded on purpose (`anima-licensing-and-brand`). The
    known cost is collision with common names such as `admin` and `monitor`, so
    the collision fails loudly rather than being resolved silently, and an
    installation with an existing `admin` renames it before importing.
13. **People come from an identity source, and the first credential is a
    link or an operator's act.** The identity source is a port: by default
    the identities declared in the configuration, later an organization's
    own directory reached by federation through the token issuer; the
    database side never changes (ADR 0001). An identity declared in the
    configuration has no password in any file (R63): it receives a link by mail
    to set one (R96, R64), and a temporary password set by an operator
    outside any file remains possible.
14. **Known limits of the token validator are handled and registered.** A token
    without an expiry claim is accepted (GAP-010, accepted risk in 0.0.1: the
    provider issues tokens with an expiry). Refusal messages are generic
    (GAP-012) and every token login logs one `FATAL` first (GAP-013). Do not
    hide them in comments; each is a `gaps.toml` entry and a candidate first
    patch upstream.
15. **Three things are called "user"; keep them apart.** Database roles are few and fixed, and nothing is ever created in the database for a person. Declared identities are the few, known people and applications that may reach the database, declared by the installation. End users of an application built on Anima are many, created at run time in the identity provider and never written in any file. The two worlds are not synchronized and meet at one point, the scope in the token (ADR 0004). Not: an end user as a database role.
16. **Declare people and applications; the first administrator is the installer's.** An application authenticates as itself and connects with a token that carries the scopes of its roles (R6). No default person ships with the product. A configuration in which no identity holds the administrator role is refused before ready, with a message that says so (R100).
17. **Only declared identities hold the scope of a role.** An identity created at run time is never touched by the configurator and never receives a role scope (R101); a client not declared does not obtain one (R102, beside R33, which refuses the token of another client).
18. Unverified: **a realm of its own for end users.** Decided and not built: end users live in a realm separate from the engine's, and the database server trusts only the engine realm's issuer, so an end user's token cannot open a session even by a mistake of configuration (rule 17 made impossible to break; R3.3 refuses the foreign issuer). No such realm exists and no test checks the design.
19. Unverified: **an organization's own directory as the identity source.**
    Reaching it by federation through the token issuer (SAML, OpenID Connect,
    LDAP) is the intended alternative to the declared identities; none is
    built, so the database side has never been run against it (ADR 0001).
20. **Identities are told apart by a claim that applications also carry.** The token validator identifies a person or an application by `preferred_username` (`engine/database/postgresql.conf`), never the e-mail, which an application's service account does not have. Observed on 2026-11-27: an application's token opened a session as its role over TLS and was refused for a role it does not hold (`tests/system/test_tokens.py`, R2, R5).Observed on 2026-11-28: a person's token (device flow, scope `readwrite`) opened a session as `readwrite` over TLS, the log named the person, and the token was refused for `admin` (`tests/system/test_tokens.py`, R2). Unverified: the role of the manage role in use by the secret store.
21. **The access rules and the identity map are generated, not committed.** The configurator's task renders them from the one declaration of the roles at build time into `.cache/` (`mise run engine:configure-render`), and they are inputs of the image tag (`mise-tasks/engine/tag`), so a changed role changes the image. Observed on 2026-11-27: the engine started with them and token logins as application roles worked; the rule of `readwrite` also worked with a person's token (2026-11-28). Unverified: the rules of the other token roles with a person's token, and the manage role in use by the secret store.

22. **The public URL is one declaration, and the database server does not use it to fetch.** `engine/access/public-url.env` states it (`https://localhost:8443` in the local engine, the entry's); the build, the proofs and the tests read that file and nothing else repeats it (publicUrlDeclaredOnce). The issuer of every token is that URL, but the database server's token validator trusts no certificate authority (GAP-061), so it reads the discovery document and keys over the pod's loopback from the identity provider directly, and token logins do not depend on the entry (tokenValidatorReachesProviderOverLoopback; `anima-tech-postgresql-oauth`, rule 21). Not: pointing the validator at the public URL; it fails, and a CA file cannot be given to it.

## Questions to answer before proposing

- Is the caller a person or a service, and does the rule for its kind hold?
- Does the rule hold for a database, role or identity created later?
- What does `pg_hba.conf` admit by default if the new rule is absent or empty?
- Which audience does the token carry, and who checks it?
- What does an upgrade do to an existing installation's roles?
- Which test, and which requirement (R-number), forbids the trap?

## Where the result goes

A decision amends ADR 0004. The rule becomes a requirement and a test (see
`anima-specifying-requirements`). The fixed roles and access rules live in
`engine/access/` and `engine/database/`; the identities and the fixed roles
they hold only in the configuration's identities file under `config/access/`.
Limits go to `gaps.toml`.
