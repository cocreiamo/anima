---
number: 9
title: Secret management — the secret store and the root of trust
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# Secret management — the secret store and the root of trust

## Context and Problem Statement

Anima needs secrets and certificates: the TLS certificates of the database server and
of the identity provider, and the credentials of the service roles in the
database server ([ADR-0010](0010-roles-and-access.md)). They were to be generated at first start by an init
container written for the purpose. It was the only piece of the product that
reinvented what an existing product does, against the rule of [ADR-0006](0006-repository-and-toolchain.md): no
tooling invented where an existing tool does the job.

A spike on 2026-11-27 with OpenBao 2.7.3 and PostgreSQL 18.7 verified the
facts recorded below.

Which existing product issues, stores and rotates these secrets, and what unseals it so that the system starts unattended?

## Decision Drivers

- No tooling invented where an existing tool does the job ([ADR-0006](0006-repository-and-toolchain.md)).
- An allowed licence ([ADR-0002](0002-licensing-and-cla.md)).
- No circular dependency with the database server the secrets serve.
- Issuance and rotation, not only storage.
- Unattended start (R26).

## Considered Options

- OpenBao, unsealed by a root-of-trust port
- HashiCorp Vault
- SOPS
- Infisical or Conjur
- podman secrets
- An init container written for the purpose
- Dynamic short-lived database users for the identity provider

## Decision Outcome

Chosen option: "OpenBao, unsealed by a root-of-trust port", because it is the only option that issues and rotates secrets under an allowed licence, and because its sealed data can lie in the database server without a circular dependency (see "The state lies in the database server").

Secret management is four ports ([ADR-0001](0001-hexagonal-architecture.md)):
**secret keeping**, the **certificate authority** and the **service
credentials**, whose default adapter is OpenBao for all three (MPL-2.0,
confirmed by the founder as an allowed licence), and the **root of trust**,
which unseals it.

### The state lies in the database server

This reverses an earlier decision of this ADR, that the secret store keeps its
state in its own integrated storage and never in the database server. The
founder reversed it on 2026-11-27, for one reason: one place holds all state,
so one backup restores everything together and the configurator's state
([ADR-0014](0014-one-configurator-for-all-state.md)) cannot be out of step with
the secret store's. The circular dependency that the earlier decision avoided
is removed by design, in this order:

1. The database server starts needing nothing, listening only inside the pod.
2. The secret store uses the database server as its storage, through the local
   socket with peer authentication, so that no password exists for that
   connection, and unseals from the root of trust.
3. The secret store issues the database server's certificate, and the server
   turns TLS on by a reload.
4. The configurator runs.
5. Only then is anything published outside the pod.

What protects the secrets is the seal, not the place where the sealed data lies.
Decided on 2026-11-27, not built and not verified by a spike; R60, R61 and R62
state it and are pending.

### Verified by the spike

1. **State.** The spike of 2026-11-27 verified OpenBao with its own integrated
   storage, never in the database server. That is no longer the design (see
   above); what the spike found about initialization and about the consumers
   below still holds.
2. **Self-initialization.** OpenBao initializes itself once from declarative
   `initialize` stanzas, with no manual step: policies, machine authentication
   with AppRole, PKI with a root CA and a server role, and the database
   secrets engine. The configuration will be versioned in this repository
   (`engine/secrets/`).
3. **Consumers get secrets through OpenBao Agent**, the official companion,
   as units of the engine ([ADR-0011](0011-engine-image-and-runtime.md)), each ordered before the unit it serves,
   that render certificates and credentials into shared in-memory volumes. Neither the database server nor the identity provider names the secret
   store product; each receives a certificate and a credential (R7).
4. **`svc_idp` is a static role** whose password OpenBao sets and rotates.
   Short-lived dynamic users are not used for the identity provider, because
   Keycloak cannot reload its database password while running (GAP-017).
5. **Two steps are not declarative.** They run in a first-start unit with
   the official `bao` command line: generating the seed values (the unseal key
   when none is given, the machine credential and the management password),
   and rotating the management password so that only the secret store knows
   it. The management role is `svc_secrets` ([ADR-0010](0010-roles-and-access.md)).
6. **A failed self-initialization cannot be repaired.** There is no rollback;
   the storage is left unusable and the server then refuses to unseal
   (GAP-015). A first start must therefore be repeatable from an empty state
   with the same command (R36), and the configuration is validated in
   continuous integration.

### The root of trust is a port

A third port unseals the secret store, so that the system starts unattended
(R26). Its contract: it gives the secret store the key that unseals it.

- **Production adapter: an external key management service**, Google Cloud
  KMS first. It keeps the root apart from the data, which is what protects
  data at rest. **It is not built in 0.0.1.** In the pinned release the cloud seals
  are external plugins fetched as images, to be pinned by digest (GAP-016).
- **Stand-in: a local key**, given to the engine by the host,
  outside the configuration (`engine/secrets/`), for local development and CI. A key stored
  beside the data does not protect data at rest; the stand-in is not a way to
  run production. **It is the only adapter built in 0.0.1.**
- When no key is given, the first-start unit generates one for the
  stand-in. Whoever uses the stand-in must keep that key apart from the data if
  the data matters at all.

### State and backup

All state lives in one place, the database server, so one backup covers
everything (R60, R20). Restoring elsewhere needs the same root of trust, which
is therefore kept apart from the backups.

### Consequences

- Good, because one store holds all state and one backup covers it (R60,
  R20); the root of trust is kept apart.
- Bad, because the database server becomes the storage of the secret store
  while the secret store issues the database server's certificate: the order
  of the start sequence above is what breaks the circle, and it is not built.
- Good, because start order is declared ([ADR-0011](0011-engine-image-and-runtime.md)): the secret store, then
  the agent unit that renders what a consumer needs, then the consumer. A
  consumer does not start before its secrets exist, and no restart loop
  stands in for the order. Decided, not built.
- Neutral, because OpenBao is a fork (`anima-openbao`, submodule
  `third_party/openbao`) maintained under [ADR-0007](0007-fork-maintenance.md), and an entry of
  `components.toml`. OpenBao Agent is part of the same release.
- Bad, because a failed first start is repaired by starting again from an
  empty state (GAP-015), so nothing precious may be in the secret store
  before the first start has succeeded.
- Bad, because 0.0.1 builds only the stand-in of the root of trust, which
  does not protect data at rest; an installation that needs that protection
  waits for the production adapter (GAP-016 for the cloud seals).
- Bad, because the rotation of secrets over time is not part of 0.0.1.
- Bad, because self-initialization runs once only, so the secret store's
  policies do not converge after first start (GAP-020).

### Confirmation

Not built. `engine/secrets/` holds only a `.gitkeep` file. The facts under "Verified by the spike" were observed in a spike of 2026-11-27, not by a test of this repository. Pending, not written: R7 (`test_R7_secrets_generated`), R26 (`test_R26_unattended_start`), R36 (`test_R36_failed_first_start_repeatable`), R20 (`test_R20_backup_restores_into_empty_system`), R60 (`test_R60_all_state_in_one_store`), R61 (`test_R61_database_server_serves_without_secret_store`) and R62 (`test_R62_storage_connection_uses_no_secret`). Validating the OpenBao configuration in continuous integration is intended and not built.

## Pros and Cons of the Options

### HashiCorp Vault

- Bad, because its BUSL licence is excluded by [ADR-0002](0002-licensing-and-cla.md). OpenBao is its open-source continuation under MPL-2.0.

### SOPS

- Bad, because it stores secrets encrypted but neither issues nor rotates them.

### Infisical or Conjur

- Bad, because each needs a PostgreSQL of its own, which makes a circular dependency with the database server they would serve.

### podman secrets

- Bad, because it is storage only, with no issuance.

### An init container written for the purpose

- Bad, because it was the original plan and it reinvents the secret store.

### Dynamic short-lived database users for the identity provider

- Bad, because Keycloak cannot reload its database password while running (GAP-017).

## More Information

Outside 0.0.1: Periodic rotation of secrets. Upgrades: R37 states that an installation
converges on upgrade and its verification is pending; the secret store's own
convergence after first start is not solved (GAP-020, [ADR-0011](0011-engine-image-and-runtime.md)).
