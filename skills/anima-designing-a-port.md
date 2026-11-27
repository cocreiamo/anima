---
name: anima-designing-a-port
description: "Use when adding a capability to Anima, choosing or replacing the product that provides one, or deciding what the engine contains and whether something is an adapter: ports, adapters, state, circular dependencies."
family: product
paths: []
---

# Designing a port

How Anima adds a capability and chooses the product that provides it
(ADR 0001).

## Use this when

- Adding a capability Anima needs and PostgreSQL does not provide.
- Choosing, or replacing, the product that provides a capability.
- Deciding whether something is an adapter, or where an adapter runs inside
  the engine.

## Rules

1. **Name the capability and its standard contract before any product.** The
   contract is written in terms of a public standard, not of a product's API.
   Example: the token issuer port is "an OpenID Connect issuer (discovery
   document, signing keys) whose bearer tokens the database server accepts
   through its `oauth` authentication method". Not: "Keycloak, because it is
   what we know". A port whose production adapter is whatever the
   configuration names (outgoing mail: the SMTP service the adopter gives) has
   the standard itself as its contract.
2. **A default adapter, alternatives, and one active** (R28, R59). Every port
   has exactly one default adapter, shipped in the engine, and may have
   alternative adapters, also shipped in the engine. The configuration selects
   the active one with a driver setting; exactly one is active. Adapters are
   code and live in the engine; choosing one is configuration. A stand-in is
   the alternative that the local profile selects. Replacing the adapter means
   writing another against the same contract; no requirement changes. Say in
   the port table (ADR 0001) which alternatives exist and that none is built,
   if so.
3. **Adapter-ness is independent of where it runs.** Ask "is it replaceable
   behind a contract?", not "is it a separate process?". Example: pgvector,
   pgBackRest and `pg_oidc_validator` run inside the database server's process and
   are adapters all the same (ports: vector search, backup, token validation);
   Keycloak and OpenBao run in their own containers, the configurator in a unit that runs to completion, and
   are adapters too (ADR 0001). All of them are parts of the engine, which also
   contains the database server, the build of the PostgreSQL fork into which the
   composition loads the in-process adapters. Not: classifying something as
   not an adapter because of where it runs.
4. **The composition names the adapters, not the database server.** The
   database server knows ports, never adapters; adapters are named only by the
   engine's composition, its units and wiring (ADR 0001). Example: R8; the
   database server learns the issuer's URL,
   not the word Keycloak. A consumer of the secret store receives a certificate
   and a credential, not the name OpenBao (R7). Check with a search of
   `engine/database/` for any adapter's product name.
5. **The default adapter is designed first.** A stand-in is an alternative
   adapter behind the same port, named as a stand-in, for local development.
   Example: the root of trust is a port whose default adapter is an external
   key management service (Google Cloud KMS first); the
   local key is its stand-in. The local key is described as not
   protecting data at rest, never as the normal way.
6. **Every port has a contract suite, and every adapter passes it** (R58,
   Liskov, `anima-product-principles`). Any adapter of a port, the local stand-in included, can
   replace another without a requirement changing, because the suite is
   written against the port, never against a product. Not: a test that holds
   only for the local key.
7. **Keep the contract narrow and standard.** A port is an OpenID Connect
   issuer, not "the Keycloak API"; split a port when its contract bundles
   different things (the secret store is three ports: keeping secrets, issuing
   certificates, and the credentials of the service roles; identity is two:
   the token issuer and the identity source). An adapter may fill several
   ports, and each contract is tested on its own. Anima grows by adding a
   port, an adapter or a plugin,
   never by modifying the database server; when something is missing, add an interface,
   not a shortcut (ADR 0002, `anima-product-principles`).
8. **Write the port's requirements against the port**, with the port as
   subject, in the model (see `anima-specifying-requirements`). Add the port as
   a `part def` specializing `Port`, the adapter as a part usage, and
   `satisfy` lines.
9. **Decide where the adapter keeps its state, and what that does to backup
   and restore.** All state of the engine lives in the database server, so
   one backup covers it (R60): the token issuer in the database `idp`, the
   secret store's sealed data, the configurator's state. The circle is broken
   by the start order, not by a second store (ADR 0003). An adapter that
   needs a second place for state is a decision of its own. Every place that
   holds state is covered by the backup (R20) and the restore drill.
10. **Check circular dependencies.** For each pair, ask who needs whom to start,
    to authenticate and to obtain a certificate. Example: the database server does not
    need the identity provider to start (R13) but needs the secret store for its
    certificate; Keycloak needs the database server for `idp`; the secret store's API
    listens on the loopback without TLS so it does not need a certificate from
    itself (ADR 0005). Not: Infisical or Conjur, each needing a PostgreSQL of
    its own (ADR 0003).
11. **Start order is declared, not obtained by restarts or wait scripts.** A
    unit that needs another is ordered after it (`After=`, `Requires=`, ADR
    0011). Not: a container that exits until what it needs exists; a "wait
    for" script or an init container that polls.
12. **Say how the adapter is loaded.** An in-process adapter (the validator,
    vector search, backup) is built into the database server's image, forked and pinned
    (`anima-maintaining-a-fork`); the composition loads it, and the configuration that does so is
    the composition's, not the database server's. An adapter in its own container is run
    by a Quadlet unit of the engine. Either way it is the port's adapter.
13. **Say which configurator converges its state** (`anima-product-principles`): one declared
    file, one configurator applied at every start. Not: state created by a
    first-start script.
14. **Record the limits of the chosen product** as `GAP-nnn` entries, with the
    workaround in the capability's directory under `engine/`, naming the id.
15. Unverified: **a contract suite for any port, and a second adapter for any
    port.** No contract suite is written (R58 is pending) and no alternative
    adapter has been run against its port besides the local key, so no
    replacement of an adapter has been shown to leave the requirements
    unchanged (ADR 0001).

## Questions to answer before proposing

- What is the capability, and which public standard defines its contract?
- Which products could fill it, and what did each fail or pass (licence,
  governance, headless, own database)? See `anima-adopting-a-component`.
- Which port does it fill, and does it run in the database server's process or in its
  own container?
- Where does it keep state, and is that place in the backup?
- Who needs whom to start, authenticate and get a certificate?
- What is the stand-in for local development, and is it named as one?
- Which requirement would change if the product changed? It should be none.
- Does the port's contract suite pass with every adapter, the stand-in and
  the default one?
- Which configurator converges its state (one for all, ADR 0006), and what does it
  not see?

## Where the result goes

An ADR (amending the port table of ADR 0001, or a new one) records the port,
its contract, the adapter and the rejected alternatives. The model gets the
`part def`, the part usage, the requirements and `satisfy` lines. The adapter's
files go under `engine/<capability>/`, never a directory named after the
product; what an adopter declares about it goes under `config/<capability>/`; the component to `components.toml`; its
limits to `gaps.toml`.
