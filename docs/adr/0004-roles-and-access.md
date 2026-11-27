---
number: 4
title: Roles and access — who may connect, and how
status: proposed
date: 2026-11-27
category: architecture
decision-makers: [founder]
---

# Roles and access — who may connect, and how

## Context and Problem Statement

The database server serves two kinds of caller: people and applications that act for
users, and the services of Anima itself. They need different guarantees. The
first must be identifiable as persons and must never use a password. The
second run inside the system, cannot do a token flow, and must be confined to
the one thing each of them does. The role names, the rule that admits each
kind and the way an identity maps to a role are one decision.

Which roles exist, which rule admits each kind of caller, and how does an identity map to a role, so that people are identifiable and never use a password while the services of Anima are confined to what each does?

## Decision Drivers

- People and applications that act for users must be identifiable as persons
  and must never use a password.
- The services of Anima run inside the system, cannot do a token flow, and
  must be confined to the one thing each of them does.

## Considered Options

- Functional role names, authorization by scope in `pg_hba.conf`, and the
  `idp` database closed by `pg_hba.conf`
- Role names with a product prefix
- Protecting the `idp` database with `GRANT`

## Decision Outcome

Chosen option: "Functional role names, authorization by scope in `pg_hba.conf`, and the `idp` database closed by `pg_hba.conf`", because the database server then keeps no per-user list, and a database created later cannot be left open.

### Roles

Names are functional, with no product prefix. They are reserved (below).

| Role          | Kind      | Reaches the database server by                      | What it is                                                                                      |
| ------------- | --------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `admin`       | token     | token, over TLS, from outside                       | May create databases and roles; not a superuser.                                                |
| `readwrite`   | token     | token, over TLS, from outside                       | Login role, member of `pg_write_all_data` and `pg_read_all_data`.                               |
| `readonly`    | token     | token, over TLS, from outside                       | Login role, member of `pg_read_all_data`.                                                       |
| `monitor`     | token     | token, over TLS, from outside                       | Login role, member of `pg_monitor`.                                                             |
| `svc_idp`     | service   | password, from the pod's loopback                   | The identity provider. Reaches only its own database, `idp`.                                    |
| `svc_backup`  | service   | password, from the pod's loopback                   | The backup.                                                                                     |
| `svc_secrets` | service   | password, from the pod's loopback                   | The management role of the secret store: `CREATEROLE` and `pg_signal_backend`, not a superuser. |
| `postgres`    | superuser | local socket inside the database server's container | No password. Reachable from nowhere else.                                                       |

`admin` is not a superuser; it may create databases and roles and nothing
more. The three other token roles are login roles that are members of
PostgreSQL's predefined roles, so the database server's own privilege system does the
work and no grant is written per database.

### Two rules

1. **A service role is never reached by token.** A role whose name begins with
   `svc_` authenticates only by password, only from the pod's loopback. No
   rule accepts a token for it and no rule lets it in from outside.
2. **A token role is reached only by token.** From outside the pod the database server
   accepts only TLS connections authenticated by token ([ADR-0005](0005-engine-image-and-runtime.md)). A password
   is accepted nowhere from outside. The one exception to "token only" is the
   local superuser, `postgres`, which has no password and no network access.

These rules are requirements (R4, R31). Their verifications are listed in
`tests/pending.toml` until written; nothing in this ADR is built yet.

### Authorization by scope

One `pg_hba.conf` rule per token role admits that role with the `oauth`
method. The rule requires a scope with the same name as the role and delegates
the mapping to the validator. The database server keeps no per-user list: `pg_ident.conf`
is empty. Verified by a spike on 2026-11-27 with `pg_oidc_validator` 1.1.0.

- In the identity provider, a scope is granted only to the holders of the
  matching realm role. Who may assume which role is therefore declared only in
  the configuration's identities file (R22), never in the database server.
- The person stays identifiable. The session's `system_user` is the token's
  identity, so an audit can name the person even though the session runs as a
  shared role. Statement logs carry only the role; the person is found by
  joining with the authentication line (GAP-014).
- Every rule that accepts tokens requires a non-empty scope. A test on our
  configuration forbids an empty one (R34), because with delegated mapping an
  empty scope would admit any valid token of the issuer (GAP-011).

### The `idp` database is closed by `pg_hba.conf`

The identity provider's database is not protected by `GRANT`. PostgreSQL
grants `CONNECT` on a new database to everyone by default, so a protection
written as grants would have to be remembered for every database created
later. The protection is written in `pg_hba.conf`, in this order:

1. one rule admits `svc_idp` into `idp`, from the loopback;
2. a `reject` rule keeps every other role out of `idp`;
3. no rule admits `svc_idp` into any other database.

This holds for databases created later too, without any further action
(R27, R32).

### Roles are declared once, as data, and converged at every start

The fixed roles, their memberships and privileges, and the `pg_hba.conf` rules
are owned by the engine ([ADR-0001](0001-hexagonal-architecture.md)): they are declared as data in this
repository, once, and an adopter never edits them. What the adopter owns is the
configuration: the identities and which fixed roles each holds (R22). The
database server's roles, the access rules, the scopes and realm roles of the
identity provider's presets and the secret store's database roles all follow
from the declaration of the fixed roles (`anima-configuration-design`). At every start
of the engine, not only at first start, a configurator applies it, revocations
included, and the database server takes no connection from outside before it
has (`anima-designing-for-production`; [ADR-0005](0005-engine-image-and-runtime.md)). After an upgrade an
installation therefore holds the same roles, privileges and access rules as a
new installation of the same version (R37, verification pending). The
declaration and the configurator are not built; the configurator is OpenTofu
([ADR-0006](0006-one-configurator-for-all-state.md)), which sees only declared
objects.

### Reserved names

The names above are reserved. Creating a role with one of them, or importing
identities that bring one, must fail and say which name conflicts (R35). Unbranded names such as `admin` and `monitor` will collide
with names that applications and tools already use; that is the known cost of
choosing functional names over a product prefix. The decision is that the
collision fails loudly rather than being resolved silently.

### Limits of the validator

The pinned token validator has three limits that matter here. In 0.0.1 each is
handled by configuration, and each is a gap, a candidate for our first
patches upstream (`anima-maintaining-a-fork`).

| Limit                                                                                                        | Handled by                                                                                               | Gap     |
| ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ------- |
| The audience of a token is not checked: a token issued to another client of the same realm opened a session. | Role scopes are granted only to the database server's own client, so the scope acts as audience (R33).   | GAP-006 |
| A token without an expiry claim is accepted.                                                                 | Not handled in 0.0.1; accepted risk, the identity provider is configured to issue tokens with an expiry. | GAP-010 |
| An empty scope with delegated mapping admits any valid token of the issuer.                                  | A test on our configuration must forbid an empty scope (R34).                                            | GAP-011 |

Two smaller gaps concern diagnosis: the validator's refusal messages are
generic and a refusal for signature or issuer carries no identity (GAP-012),
and libpq's discovery round makes every token login log one `FATAL` first
(GAP-013).

### Consequences

- Good, because the roles are data reconciled at every start, so an upgrade
  changes them in an existing installation as in a new one (R37, pending).
- Good, because who may assume which role is read in one file, the
  identities file; the database server's access rules are the same whatever
  the people are.
- Good, because a password exists only for service roles, and is issued and
  rotated by the secret store ([ADR-0003](0003-secret-management.md)).
- Good, because the `svc_idp` password never leaves the pod's loopback; a
  connection from anywhere else is refused by `pg_hba.conf` before
  authentication.
- Bad, because the `idp` rules must stay first and in order in
  `pg_hba.conf`; a test must verify the order (R27, R32).
- Bad, because statement logs name the role, not the person (GAP-014).
- Bad, because the names are taken: an installation that already uses a role
  named `admin` must rename it before importing.

### Confirmation

Not built: nothing in this ADR is built. Pending, not written: R4 (`test_R4_no_password_access`), R22, R27, R31, R32, R33, R34 (a test on our configuration forbids an empty scope), R35 and R37 (see `tests/pending.toml`); R27 and R32 include a test of the order of the `idp` rules in `pg_hba.conf`.

## Pros and Cons of the Options

### Role names with a product prefix

- Bad, because the decision is that names are functional, with no product prefix. The known cost of the functional names is that unbranded names such as `admin` and `monitor` will collide with names that applications and tools already use; the collision fails loudly rather than being resolved silently.

### Protecting the `idp` database with `GRANT`

- Bad, because PostgreSQL grants `CONNECT` on a new database to everyone by default, so a protection written as grants would have to be remembered for every database created later.
