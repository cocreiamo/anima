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
2. **Passwords only on the pod's loopback and only for `svc_` roles.** A role
   whose name begins with `svc_` authenticates only by password, only from the
   loopback, and no rule accepts a token for it (R31). The `svc_` prefix states
   the kind, not the brand.
3. **The roles are fixed.** Token roles: `admin` (creates databases and roles;
   not a superuser), `readwrite`, `readonly`, `monitor`. The last three are
   login roles that are members of PostgreSQL's predefined roles
   (`readwrite`: `pg_write_all_data` and `pg_read_all_data`; `readonly`:
   `pg_read_all_data`; `monitor`: `pg_monitor`), so the database server's own privilege
   system does the work. Service roles: `svc_idp`, `svc_backup`, `svc_secrets`. Not: a grant
   written per database.
4. **`postgres` only through the local socket**, inside the database server's container,
   peer authentication, no password (R12).
5. **One access rule per token role**, requiring a scope with the same name as
   the role and delegating the mapping to the validator. The database server keeps no
   per-user list: `pg_ident.conf` is empty.
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
10. **Role scopes go only to the database server's own client**, because the validator
    does not check the audience (GAP-006). The scope acts as audience (R33).
    Not: granting a role scope to another client of the realm.
11. **A rule that accepts tokens never has an empty scope** (R34): with
    delegated mapping an empty scope would admit any valid token of the issuer
    (GAP-011). A test on our configuration forbids it.
12. **The names are reserved.** Creating a role with a fixed name, or
    importing identities that bring one, fails and says which name conflicts
    (R35). The names are unbranded on purpose: the trademark, not a prefix,
    protects the brand (`anima-licensing-and-brand`). The known cost is collision with common names
    such as `admin` and `monitor`, so the collision fails loudly rather than
    being resolved silently, and an installation with an existing `admin` renames
    it before importing.
13. **People come from an identity source, and the first credential is a
    link or an operator's act.** The identity source is a port: by default
    the identities declared in the configuration, later an organization's
    own directory reached by federation through the token issuer; the
    database side never changes (ADR 0001). An identity declared in the
    configuration has no password in any file: it receives a link by mail
    to set one (R63, R64), and a temporary password set by an operator
    outside any file remains possible.
14. **Known limits of the token validator are handled and registered.** A token
    without an expiry claim is accepted (GAP-010, accepted risk in 0.0.1: the
    provider issues tokens with an expiry). Refusal messages are generic
    (GAP-012) and every token login logs one `FATAL` first (GAP-013). Do not
    hide them in comments; each is a `gaps.toml` entry and a candidate first
    patch upstream.
15. Unverified: **an organization's own directory as the identity source.**
    Reaching it by federation through the token issuer (SAML, OpenID Connect,
    LDAP) is the intended alternative to the declared identities; none is
    built, so the database side has never been run against it (ADR 0001).

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
