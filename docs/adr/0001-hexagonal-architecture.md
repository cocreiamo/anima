---
number: 1
title: Hexagonal architecture — engine, ports and adapters
status: proposed
date: 2026-11-27
category: architecture
decision-makers: [founder]
---

# Hexagonal architecture — engine, ports and adapters

## Context and Problem Statement

Anima is a database product built piece by piece on a fork of PostgreSQL.
The fork may be modified over time, so Anima is not a repackaging of
upstream. The product needs capabilities that PostgreSQL does not provide by
itself; the first one is authentication against an identity provider. Each
capability is filled by an existing product, and that choice must stay
replaceable.

What Anima adds is the paved integration: the adopted products are configured
to work together out of the box, and that configuration is specified, tested
and released as one thing.

How is Anima structured so that each capability is filled by an existing product, that choice stays replaceable, and the integration stays specified, tested and released as one thing?

## Decision Drivers

- Each capability is filled by an existing product, and that choice must
  stay replaceable.
- What Anima adds is the paved integration, specified, tested and released
  as one thing.
- The PostgreSQL fork may be modified over time, so Anima is not a
  repackaging of upstream.

## Considered Options

- Hexagonal (ports and adapters) architecture

No alternative was recorded when this decision was taken, so the chosen option is the only one listed.

## Decision Outcome

Chosen option: "Hexagonal (ports and adapters) architecture", because it keeps each capability replaceable behind a standard, product-neutral contract. The original record gives no other justification.

Anima follows a hexagonal (ports and adapters) architecture.

1. **Dependency rule.** The database server knows ports, never adapters;
   adapters are named only by the engine's composition, that is, by its
   units and wiring. Nothing in the database server names an adapter
   product. The configuration that loads an in-process adapter into the
   database server belongs to the composition, not to the database server.
2. **Requirements.** Requirements are stated against Anima and its ports. In
   the model a port is a part definition specializing the abstract `Port`, and
   an adapter is a part usage of it that satisfies requirements; a product
   never appears in a requirement text.
3. **A default adapter, alternatives, and one that is active.** Each port has
   exactly one default adapter, shipped in the engine, and may have
   alternative adapters, also shipped in the engine (R28). The configuration
   selects which one is active: each capability carries a setting that names
   the active adapter, the driver, and that adapter's own settings, and
   exactly one adapter of a port is active in an installation (R59). Adapters
   are code and live in the engine; choosing one is configuration. A stand-in
   is simply the adapter that the local profile selects. An adapter may fill
   more than one port. Replacing an adapter means writing another against the
   same contract.
4. **An adapter is defined by replaceability, not by where it runs.** Being an
   adapter means being a replaceable product behind a standard contract. Some
   adapters run inside the database server's process (the token validator,
   vector search); one runs inside its container, invoked by it (backup);
   others run in their own container (the token issuer, the secret store) or
   as a unit that runs to completion (the configurator). For a capability that
   an external service provides, the adapter is the engine's own client and
   wiring for that service, selected and configured by the configuration: the
   service runs outside, its adapter is in the engine. That is a matter of
   deployment and does not change the rule: the database server knows the
   port, never the product. All of them are part of the engine. In the model
   every port specializes `Port`, and an adapter is a part of the engine.
5. **Production is the default.** The stand-in exists only because local
   development cannot have the production dependency. It is marked in the model
   by the definition `StandIn`, so a test tells it from the default adapter.
   An ADR never describes a stand-in as the normal path ([ADR-0005](0005-engine-image-and-runtime.md)).
6. **Every port has a contract suite.** The suite is a set of tests written
   against the port, never against a product, and every adapter of the port
   must pass it (R58, pending). This is what makes substitution true, the
   Liskov point of `anima-designing-a-port`.

### Terms

- **Anima** is the product: the engine plus an instance's configuration and,
  later, other components.
- **Engine** is the runtime Anima ships: the database server built from the
  PostgreSQL fork, together with every adapter (identity provider, token
  validation, secret store, vector search, backup, and so on) and the wiring
  that makes them work together. The adapters are inside the engine. The
  engine is owned by the product: it is versioned and released by us, and an
  adopter never edits it.
- **Database server** is the build of the PostgreSQL fork: one part of the
  engine.
- **PostgreSQL fork** is the source component `anima-postgres`, the submodule
  `third_party/postgres`.
- **Engine image** is the one image in which the engine is delivered: an
  image-based operating system that carries its own init (`systemd`), the
  container runtime of its base image and the Quadlet units of the engine. It starts
  in two ways: booted as the operating system of a machine, or run as a
  container by a daemonless, rootless container engine ([ADR-0005](0005-engine-image-and-runtime.md)). Decided,
  not built.
- **Configuration** is what an adopter declares about their own instance:
  the identities and the installation parameters. It is owned by the
  installation, lives outside the engine, and is read by it at every start.
- **Composition** is the engine's units and wiring: the place that names
  the adapters and connects each to its port.
- **Port** is a capability Anima needs, defined by a standard,
  product-neutral contract.
- **Adapter** is a replaceable product that fills a port behind its contract.
- **Default adapter** is the adapter of a port that is active unless the
  configuration names another. **Alternative adapter** is another adapter of
  the same port, shipped in the engine. **Driver** is the setting of a
  capability, in the configuration, that names the active adapter.
  **Stand-in** is the alternative adapter that replaces a production
  dependency in local development and in CI; the local profile selects it.

### Ports and adapters

| Port                  | Contract                                                                                                                                                                                                                                 | Default adapter                                                                                        | Alternatives                                                                                                                             | Stand-in                                                         | Runs in                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Token issuer          | An OpenID Connect issuer (discovery document, signing keys) whose bearer tokens the database server accepts through its `oauth` authentication method. Always inside the engine, because the database server accepts only such tokens    | Keycloak                                                                                               | none built                                                                                                                               | none                                                             | its own container                                                       |
| Identity source       | Where the people of an installation come from                                                                                                                                                                                            | The identities declared in the configuration, applied to the token issuer                              | An organization's own directory (SAML, OpenID Connect or LDAP) reached by federation through the token issuer as intermediary; not built | none                                                             | the token issuer                                                        |
| Configurator          | Applies the product's declarations and the adopter's configuration to every store, at every start ([ADR-0006](0006-one-configurator-for-all-state.md))                                                                                   | OpenTofu with its three providers                                                                      | none built                                                                                                                               | none                                                             | a unit that runs to completion                                          |
| Secret keeping        | Keeps secrets and gives a consumer the one it needs; keeps its state in the database server ([ADR-0003](0003-secret-management.md))                                                                                                      | OpenBao                                                                                                | none built                                                                                                                               | none                                                             | its own container                                                       |
| Certificate authority | Issues certificates                                                                                                                                                                                                                      | OpenBao                                                                                                | none built                                                                                                                               | none                                                             | its own container                                                       |
| Service credentials   | Sets the credentials of the service roles                                                                                                                                                                                                | OpenBao                                                                                                | none built                                                                                                                               | none                                                             | its own container                                                       |
| Root of trust         | Gives the secret store the key that unseals it ([ADR-0003](0003-secret-management.md))                                                                                                                                                   | The engine's client of an external key management service, not built in 0.0.1 (Google Cloud KMS first) | none built                                                                                                                               | A local key                                                      | beside the secret store; the service itself outside                     |
| Token validation      | Validates a bearer token against an OpenID Connect issuer, through the database server's OAuth validator interface                                                                                                                       | `pg_oidc_validator`                                                                                    | none built                                                                                                                               | none                                                             | the database server's process                                           |
| Vector search         | Vector similarity search in SQL                                                                                                                                                                                                          | `pgvector`                                                                                             | none built                                                                                                                               | none                                                             | the database server's process                                           |
| Backup                | Backup and restore of the database server's data                                                                                                                                                                                         | `pgBackRest`                                                                                           | none built                                                                                                                               | none                                                             | the database server's container, invoked by it                          |
| Outgoing mail         | SMTP                                                                                                                                                                                                                                     | The engine's client of the SMTP service that the configuration names                                   | none built                                                                                                                               | A local mail catcher (to be forked as `anima-mailpit`; not done) | the service runs outside the engine; its own container for the stand-in |
| HTTP entry point      | The single way for HTTP into the engine: it terminates TLS and forwards only the declared path prefixes to declared backends on the pod's loopback, and answers 404 to the rest ([ADR-0008](0008-the-http-entry-point-of-the-engine.md)) | Kestrel with YARP, hosted by a minimal host program owned by Anima                                     | none built                                                                                                                               | none                                                             | its own container                                                       |

One adapter may fill several ports: OpenBao is the default adapter of secret
keeping, of the certificate authority and of service credentials, and a remote
service could later take one of the three. The secret-store port was split
into these contracts because they are different things. Identity has two
ports for the same reason: the database side never changes, whether people
come from the configuration or from an organization's directory.

Nothing alternative is built. In 0.0.1 the root of trust has only its
stand-in built. The default adapter of the root of trust, and the stand-in of
outgoing mail, are part of the model and of this table, but they do not exist
yet.

### Two layers, two owners

An installation of Anima is two layers, each with one owner. The engine is the
runtime the product ships; the configuration is what an adopter declares about
their own instance.

|            | Engine (runtime)                                                                     | Configuration                                                                                      |
| ---------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| Owner      | the product                                                                          | whoever adopts Anima                                                                               |
| Contains   | fixed roles, access rules, scopes, secret-store policies, the configurator's presets | the identities (who the users are and which fixed roles they hold) and the installation parameters |
| Lives      | inside the engine image, versioned with Anima                                        | outside the image, in a directory mounted into the engine                                          |
| Changed by | us, with a release                                                                   | the adopter, without touching the engine                                                           |

The rules that follow from the two layers are in `anima-configuration-design`. The
boundary coincides with the licence boundary already set by the plugin
exception ([ADR-0002](0002-plugin-boundary.md)): configuration and data are not covered by the AGPL.
In the repository the two layers are the directories `engine/` and `config/`,
whose capability names mirror each other; `config/` holds the example
configuration, which tests and local development use (`anima-repository-conventions`).

### Consequences

- Neutral, because identities live in the adapter, and are declared in the
  configuration; roles and privileges live in the database server and are
  fixed by the engine.
- Bad, because Keycloak stores its state in the database server, in a
  database named `idp`. The database server must therefore start, and accept
  that one service connection, without the identity provider being
  available. That connection uses a password issued by the secret store ([ADR-0003](0003-secret-management.md)), comes from the pod's loopback and is one of the service roles ([ADR-0004](0004-roles-and-access.md)); no connection from outside is authenticated by password.
- Good, because the `postgres` superuser is reachable only through the local
  socket inside the database server's container, with peer authentication
  and no password.
- Neutral, because libpq accepts only an HTTPS issuer, so the issuer is served
  over TLS with a certificate issued by the secret store ([ADR-0003](0003-secret-management.md)),
  by the HTTP entry point in front of the identity provider
  ([ADR-0008](0008-the-http-entry-point-of-the-engine.md)).
- Neutral, because roles, and who may reach them, are [ADR-0004](0004-roles-and-access.md); how the
  engine image is run is [ADR-0005](0005-engine-image-and-runtime.md).
- Neutral, because how the facts of an installation are declared once,
  converged and generated, how the two layers are kept apart, and how the
  architecture is read as SOLID, is `anima-product-principles`.

### Confirmation

Checked on 2026-11-27 (`mise run check`): R28, `test_R28_each_port_has_one_default_adapter` (each port has exactly one default adapter; alternatives are free), R67, `test_R67_every_adapter_is_part_of_the_engine` (every adapter is a part of the engine, including the client of an external service), R39 and R49 (the configurator's tests of the declared facts and of the configuration naming no adapter). Pending in `tests/pending.toml`, not written: R58 (every adapter of a port passes the port's contract suite), R59 (exactly one adapter of each port is active, the one the configuration names) and R8 (the database server depends on the token issuer only through the issuer contract). The dependency rule has no other automated check. The composition (the engine's units and wiring) is written and was seen working as a container run by the system tests of 2026-11-27 (`anima-image-design`); the booted way was not run.

## Pros and Cons of the Options

Only the chosen option was recorded, so there is no rejected alternative to weigh.

## More Information

The structure is fixed: a default adapter, alternatives, and one that is
active for each port; the secret-store port is three contracts, identity is the
token issuer and the identity source, there is one configurator, and outgoing
mail is a port. No alternative adapter is built; the adapters follow when they
are needed.
