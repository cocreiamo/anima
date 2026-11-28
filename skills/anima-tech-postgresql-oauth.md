---
name: anima-tech-postgresql-oauth
description: "Use when writing or debugging token logins, pg_hba.conf oauth rules, the pg_oidc_validator module, or a test client that connects with a bearer token, with PostgreSQL's oauth authentication and libpq in Anima: what the validator really checks, what the log says, how to build and configure it."
family: technology
paths:
  - third_party/postgres/**
  - third_party/pg_oidc_validator/**
  - engine/database/**
---

# PostgreSQL oauth, libpq and pg_oidc_validator

How PostgreSQL's `oauth` authentication, libpq and the token validator module
behave when run. The access design is in `anima-access-design`; this file is
only about what the technology does.

## Use this when

- Writing or changing an `oauth` line in `pg_hba.conf`, or the validator's settings.
- Building `pg_oidc_validator` into an image.
- Writing a test or script that must log in with a token already in hand.
- Reading the server log to find out why a token login was refused.
- Alerting on `FATAL` lines of the database server.

## Rules

1. **Build the validator from the pinned source, never from the nightly package.** Example: `engine/database/Containerfile`; essential lines `ADD validator.tar /build/` then `cd /build/pg_oidc_validator && make USE_PGXS=1 && make USE_PGXS=1 install`. Observed on 2026-11-27 with PostgreSQL 18.7 and pg_oidc_validator 1.1.0: a C++23 compiler built the module inside a PostgreSQL 18 image; 0 errors over 20 sessions. Not: the nightly package; it was an older version and logged "could not find block containing chunk" at the end of the first session (GAP-005, closed).
2. **Name the module in both settings.** `shared_preload_libraries` and `oauth_validator_libraries` both name `pg_oidc_validator`; `pg_oidc_validator.authn_field` picks the claim used as identity (default `sub`; `email` was used in the spike).
3. **Write one access rule per role.** Example: `host all <role> all oauth issuer=<url> scope="<scope>" delegate_ident_mapping=1`. A token holding the scope may log in as that role; a token without it is refused; a role with no rule gets "no pg_hba.conf entry"; `session_user` is the shared role and `system_user` is `oauth:<identity>`. Not: expecting the requested role to be checked against the token; the validator never looks at it, the role comes only from the `scope` of the matching rule.
4. **Never write a rule without a scope.** Not: expecting an empty `scope` to refuse; with no required scope every valid token is authorized (GAP-011).
5. **Grant role scopes only to the database's own client.** Not: expecting the audience to be checked; it is not, and a token issued to another client of the same issuer opened a session (GAP-006).
6. Unverified: **a token without `exp` is refused.** Expiry is checked only if the claim is present (GAP-010).
7. **Log in with a token already in hand through libpq's `PQsetAuthDataHook` and `PQAUTHDATA_OAUTH_BEARER_TOKEN`.** Example: PostgreSQL's own test client `src/test/modules/oauth_validator/oauth_hook_client` in `third_party/postgres`, called as `oauth_hook_client --token TOKEN CONNINFO` (read, not run); a client of a few lines (written in a spike on 2026-11-27, run, not kept) did it: a hook that for `type == PQAUTHDATA_OAUTH_BEARER_TOKEN` sets `req->token` from an environment variable, else calls `PQdefaultAuthDataHook`, installed with `PQsetAuthDataHook(hook)`. Not: a connection parameter for a token; libpq has only the device flow built in (GAP-007).
8. **Pass `oauth_issuer=<url> oauth_client_id=<id>` even when a hook supplies the token.** Not: expecting the hook to make them unnecessary; the client fails with "server requires OAuth authentication, but oauth_issuer and oauth_client_id are not both set".
9. **Give the client an https issuer and no debug mode.** Observed on 2026-11-28 (`tests/system/test_tokens.py`): with the issuer `https://localhost:8443/realms/anima` the hook client logged in with no `PGOAUTHDEBUG`; the hook supplies the token, so the client never contacts the issuer and needs no trust anchor. Not: `PGOAUTHDEBUG=UNSAFE` for a plain-HTTP issuer; it was needed only while the issuer was plain HTTP (libpq refused "OAuth discovery URI … must use HTTPS"), and it also switches on traffic printing and a replaced CA list.
10. **Read the log with `log_connections = 'all'`.** The line `connection authenticated: identity="…" method=oauth` appears for successes and for scope refusals, with "Authorization failed because of scope mismatch. Required scopes: … Received scopes: …". Not: expecting a useful message for the other refusals; a wrong issuer logs "claim value does not match expected value", a token signed by an unpublished key "wrong algorithm", a tampered token "failed to verify signature", none with an identity (GAP-012); diagnose with the issuer's discovery document and a decoded token. The statement log carries only the role, so join it with the `connection authenticated` line of the session (GAP-014).
11. **Make alerts on `FATAL` ignore the discovery round.** Not: expecting one clean line per login; every token login first logs `FATAL: OAuth bearer authentication failed`, then the client retries ("retrying connection with new bearer token") (GAP-013).
12. **Do not rely on `pg_ident.conf` to map the identity.** With `delegate_ident_mapping=1` the validator's "authorized" is the only gate and `pg_ident.conf` is skipped (read in `auth-oauth.c`); core records the identity even when the token is not authorized.
13. **A new database is open to everyone by default.** The rule that closes it is in `anima-access-design`. Not: expecting `CONNECT` to be refused on a new database.
14. **Give ADMIN OPTION when `CREATEROLE` must change another role's password.** Observed on 2026-11-27 with PostgreSQL 18.7: `CREATEROLE` alone is not enough; it also needs ADMIN OPTION on that role.
15. Unverified: how the validator decides, from the pinned source (read): required scopes are the rule's `scope` split on spaces; received scopes are the union of the token's `scp` and `scope` claims; authorized means received includes required; it checks the issuer against the rule's `issuer` and the signature against the issuer's published keys.
16. **TLS is switched on by a reload after the secret store signed a certificate request.** Observed on 2026-11-27: `engine/database/tls-enable` makes the key in memory, sends only a signing request to the secret store's authority and includes `ssl.conf` once it exists; token logins over TLS then worked (`tests/system/test_tokens.py`). The unit stays up and renews the certificate by the same reload, with no restart of the server (R118); see `anima-secrets-design` rule 14.
17. **The validator needs both libraries and an identity field.** Example: `engine/database/postgresql.conf` sets `shared_preload_libraries`, `oauth_validator_libraries` and `pg_oidc_validator.authn_field = 'preferred_username'`, a claim that people and applications both carry.
18. **Make the cluster in a temporary directory and rename it.** Example: `engine/database/database-init.container` runs `initdb` into `cluster.tmp` and `mv` to `cluster`, so a kill during the first start leaves no half-made cluster (R42). Observed on 2026-11-27.
19. Unverified: that names beginning with `pg_` are reserved and `pg_read_all_data`, `pg_write_all_data`, `pg_monitor` and `pg_signal_backend` are predefined roles that cannot log in themselves (all read in the documentation); `oauth_hook_client` itself was only read, not run.

20. **The validator trusts no certificate authority you can name: it has no setting for one (GAP-061).** Read in the pinned source on 2026-11-28 (`src/http_client.cpp`): it uses libcurl with its compiled-in system store, sets no CA option, and the library does not read `CURL_CA_BUNDLE`. Not: giving it the engine authority's certificate file, as TASK-88 first hoped; it cannot take one, so it cannot fetch over the entry's TLS (observed: with the public https issuer and no override, token logins failed with "OAuth bearer authentication failed").
21. **Give the validator the identity provider's own address, and make the provider publish its keys there.** `pg_oidc_validator.discovery_url_override` (reloadable) replaces where the discovery document is fetched; the token's `iss` is still checked against the issuer of the access rule. The keys are fetched from the `jwks_uri` inside that document, so the provider must publish it at the same internal address. Example: `engine/configure/rendering/access-rules.tf` renders `discovery_url_override = 'http://127.0.0.1:8080/realms/anima'` into `/etc/anima/database/validator.conf`, included by `postgresql.conf`; the provider runs with `--hostname-backchannel-dynamic=true` (`anima-tech-keycloak`). Observed on 2026-11-28 with PostgreSQL 18.7 and the validator 1.1.0 (`tests/system/test_tokens.py`, R2, R182): with the override and without the flag, the document's `jwks_uri` was `https://localhost:8443/…/certs` and the login failed; with both, token logins succeeded, an application's and a person's from the device flow, also while the entry was stopped. Not: the override alone.
22. **For an adopter: a person who logs in with the device flow needs the engine authority's certificate in the system trust store, or a publicly trusted certificate on the entry.** The client library chooses its trust anchors from the system store only; its CA-file variable (`PGOAUTHCAFILE`) is honoured only in the unsafe debug mode (`libpq-oauth/oauth-curl.c`, read on 2026-11-28; the comment there says the roots are expected to be changed system-wide). Unverified: a device-flow login by libpq itself against the entry with the engine's authority installed in the system store; the tests use a hook with a token already in hand.

## Questions to answer before proposing

- Which scope does each rule require, and who may obtain it?
- Which client may obtain a role scope, given that the audience is not checked?
- How will a refused login be diagnosed, given the generic messages?
- Does an alert count the `FATAL` of the discovery round as normal?
- What did you run, and what did you only read in the source?

## Where the result goes

The access design goes to `anima-access-design` and ADR 0004; the build to `engine/database/`. Limits found go to `gaps.toml` (GAP-005 to GAP-007, GAP-010 to GAP-014, GAP-061); the toolchain side is `anima-repository-conventions`. Related skills: `anima-access-design`, `anima-secrets-design`, `anima-tech-keycloak`.
