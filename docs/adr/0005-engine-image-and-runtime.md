---
number: 5
title: The engine image, its units and how the system starts
status: proposed
date: 2026-11-27
category: architecture
decision-makers: [founder]
---

# The engine image, its units and how the system starts

## Context and Problem Statement

Anima is several processes: the database server, the identity provider and its
configurator, the secret store. They must run together on any machine an
agency or a developer has, without the machine being prepared for them, and
without the adopter installing or managing an orchestrator.

A first attempt ran the pod with `podman kube play` on the host, from one
Kubernetes manifest. A manifest is a description for an orchestrator; run by
`podman kube play` it only imitated what an init system gives by design. Start
order had to be obtained by restarts, the run-to-completion step had no
natural place, and the checks of a container were whatever the host's podman
version made of them: an older podman, observed on a development machine, ignores
`readinessProbe`, does not restart on a failed `livenessProbe` (GAP-019) and
copies the host's `/etc/hosts` into the pod's containers (GAP-018). A product
cannot be specified, tested and released as one thing if the runtime under it
differs from machine to machine.

How is Anima delivered and started as several processes on any machine an agency or a developer has, without preparing the machine and without an orchestrator?

## Decision Drivers

- Anima is several processes: the database server, the identity provider and
  its configurator, the secret store.
- They must run together on any machine, without the machine being prepared
  for them.
- The adopter does not install or manage an orchestrator.
- A product cannot be specified, tested and released as one thing if the
  runtime under it differs from machine to machine.

## Considered Options

- One engine image, started booted or as a container, whose containers are
  declared as native Quadlet units
- `podman kube play` on the host, from one Kubernetes manifest (the first
  attempt)

## Decision Outcome

Chosen option: "One engine image, started booted or as a container, whose containers are declared as native Quadlet units", because an init system gives by design what the manifest only imitated, and the runtime under the product no longer differs from machine to machine. Decided, not built.

### Status of this decision

**Decided, not complete.** The evidence of this ADR is a spike of 2026-11-27,
recorded under "Confirmation", not a test of this repository. Where the spike
found something that did not work, this ADR says so and does not claim the
design is proven on that point.

### The engine image: one image, two ways to start it

The engine is delivered as one image, the **engine image**: an image-based
operating system built from a container file, on the Fedora bootc base image
(`components.toml`). It holds the operating system, `systemd` as its init, the
container runtime of the base image and the engine's units. Images are built with
`buildah` or `podman build`; no Docker is used anywhere (`anima-repository-conventions`).

There are two ways to start the same image, and no other:

1. **Boot it** as the operating system of a machine. Disk images are produced
   from the same image by `bootc-image-builder`. The host is then immutable;
   its upgrade is atomic and can be rolled back (R51). Data volumes are not
   rolled back: only the operating system and the engine are. That is one
   more reason for "expand only" (`anima-product-principles`): the previous version must be able
   to run on the data the new version left (R43).
2. **Run it as a container**, with a container engine that needs no daemon and
   no root (podman, rootless). `systemd` is the init inside the container.
   Running it so needs two added capabilities and a volume for the inner
   container storage: `SYS_ADMIN`, for the nested mounts, and `SYS_PTRACE`,
   because the inner container runtime opens the namespace files of the inner
   processes when it executes a command in an inner container, and without it
   every health check fails (observed on 2026-11-27, see "Confirmation").
   No full privilege is needed. That is a cost of nesting, stated plainly. The
   same image booted as an operating system has no nesting and needs none of it.

What a machine must provide: to boot the image, nothing else; to run it as a
container, a container engine without daemon and without root (R29). It never
needs a Kubernetes cluster, a compose tool or any orchestrator, and the host's
own podman version, `/etc/hosts` or packages play no part (R29, GAP-018).

The two ways differ in how the image starts and nothing else: the units are
the same, and the checks that start the engine as a container test the
engine that is booted (R9, R41).

### The units are native Quadlet files

The engine's containers are declared as Quadlet units (`.pod`, `.container`
and the other files Quadlet reads), in `engine/image/`. There is no
Kubernetes manifest, no `podman kube play` and no compose file. What this gives
by design:

- **Start order is declared**, with `After=` and `Requires=`. It is not
  obtained by restarts, and there are no "wait for" scripts.
- **The configurator is a unit that runs to completion at every start**, and
  the other units wait for it. Configuring is part of every start, not only of
  the first (see "Converge, then become ready").
- **Startup, liveness and readiness checks are the units' health settings**,
  and a failed health check restarts the container. The three checks are
  declared by every unit (R41).
- **Nothing is published to the outside before the configurator has
  succeeded**, by ordering: the units that publish a port are ordered after
  the configurator (R40). How the configurator reaches the stores while
  nothing is published yet is one of the things the spike checks.
- **systemd is the init**: stopping on request is clean, and starting after an
  abrupt stop is a normal start (R42).
- **The host alias and the published ports are settings of the units**, derived
  from the two installation parameters (below, `anima-product-principles`). The alias replaces
  `hostAliases` of the earlier design; that it behaves as the earlier spike
  found for `hostAliases` is not yet verified.

The inner images that the units name are identified by digest, never by a
tag alone (R11). They are carried inside the engine image as an OCI directory
pinned by digest, and a unit imports them into the inner container storage at
first start: a container storage cannot be baked into an image layer by a
rootless build (GAP-025). That costs image size and start time, and R9 (ready
within the time bound by its attribute in the model) must hold with it. The
engine image is built in the image format that keeps its health check settings.

### Validated without starting

The units are validated statically: Quadlet's own dry run produces the
services they generate, and `systemd-analyze verify` checks those. Both run
inside a container of the engine image, so that the check works on any machine
and needs nothing installed on it (R52). `kubeconform` and `kube-linter` are
no longer needed, because the engine is no longer declared as a Kubernetes
manifest. The check is adopted and not in use: it cannot run before the engine
image exists (`anima-repository-conventions`).

### Production is the default environment

An installation is a production installation unless it says otherwise. Local
development is the special environment: it replaces a production dependency
with a stand-in behind the same port ([ADR-0001](0001-hexagonal-architecture.md)). The root of trust is the
example. The production adapter is an external key management service; the
local key is its stand-in for local development and CI and does not protect
data at rest ([ADR-0003](0003-secret-management.md)). In 0.0.1 only the stand-in is built, and this ADR
says so plainly: no part of this design describes the local path as the normal
one. A stand-in is never a configuration option that production may choose
silently.

### One pod, loopback inside

All containers of the pod share its network namespace, so they reach each
other on the loopback. The rules:

1. **Nothing is reachable from outside the host unless configured.** Two
   installation parameters configure it (R30):
   - the full public URL of the identity provider: scheme, host and port;
   - the address the system listens on, by default `127.0.0.1`.

   Not built, and not yet decided in full: the address must hold in both ways
   to start the image. Run as a container, the outer publish restricts it;
   booted, the services themselves must bind to it, which the units do not
   yet do, so a booted machine would expose the ports on every interface (R30
   would not hold). Open point, with a backlog task.

   Both belong to the configuration (below). Each is declared once and
   everything that repeats it is derived from it (`anima-product-principles`).

2. **The public URL is the issuer.** The identity provider uses it as its
   fixed hostname and its certificate carries it. Inside the pod the same name
   resolves to the pod itself, by a host alias that is a setting of the units,
   so a container validates the same issuer as a client outside does. A spike
   of 2026-11-27 verified this for the earlier design; for the units it is
   verified by the spike now under way.
3. **From outside the pod the database server accepts only TLS connections
   authenticated by token.** Password authentication exists only on the pod's
   loopback and only for service roles ([ADR-0004](0004-roles-and-access.md)).
4. **The secret store's API listens only on the pod's loopback, without TLS,
   and is never published.** This removes a circle: the secret store would
   otherwise need a certificate that it issues itself.

### The configuration is mounted

The engine image holds the engine and nothing of the adopter. The adopter's
configuration (the identities and the two installation parameters) lives in a
directory outside the image, which the adopter mounts into the engine and which
the engine reads at every start ([ADR-0001](0001-hexagonal-architecture.md), `anima-configuration-design`). The
configuration is validated before the engine becomes ready: an invalid one
leaves the engine closed and not ready, with a message the adopter can act on
(R48). It holds no secret (R7). The configuration is not a state store: the
engine never writes to it. The repository's own `config/` is the example
configuration, used by tests and local development, which is the special
environment. Nothing of this is built.

### Converge, then become ready

The start sequence has two parts in this order: every place that holds state
is brought to its declared state (see "Upgrades converge"), then the system
becomes ready. The configurator is the unit that does the first part and runs
to completion at every start; the units that serve are ordered after it. The
system accepts connections from outside only after the first part has been done
and checked. A start that cannot converge leaves the system not ready and
closed, never half-configured and serving: there is no state in which the
database server accepts connections with yesterday's roles and today's access
rules (R40, `anima-product-principles`). The requirement is stated and its verification is
pending; the mechanism is not built.

The database server does not need the identity provider to start: the
validator reads the issuer at login time, not at start (R13). It does not need
the secret store either (R61): it starts first, listening only inside the pod.
The secret store then uses it as storage through the local socket, unseals from
the root of trust and issues the database server's certificate, and the server
turns TLS on by a reload; the configurator then runs; only then is anything
published outside the pod. That is a declared order, not a restart loop
([ADR-0003](0003-secret-management.md)).

### Checks and one readiness answer

Every unit that runs a container declares three checks, as health settings:

- **startup**: the container has finished starting;
- **liveness**: it is still healthy; failing means restart;
- **readiness**: it can do its work now.

The engine exposes one readiness answer for the whole system: a systemd target
that is reached only when every unit is active and healthy and the
configurator has succeeded. When the image runs as a container, the health
check of that container asks this target, so that any container engine and the
tests can wait on it (R41). It is the system's own answer, declared in the
units, not inferred by a test.

A test is still what shows that the answer is honest: a system test performs a
real token login within the time limit of R9 and checks that the target was
reached by then, and not before the login could succeed (R9, `anima-product-principles`).

Observed on 2026-11-27 (see "Confirmation"): with both added capabilities, a
container became healthy through its declared checks. Not observed and not
claimed: that the readiness target is reached, that a failing check restarts
its container, and that the target stays unreached when the configurator fails.
The verification of R41 is pending. GAP-018 and GAP-019, which
concern an older podman and `podman kube play`, are closed: they no longer apply
to a design that does not use them.

### Development and tests use no Docker

Container work in development, tests, continuous integration and documentation
uses a daemonless, rootless container engine (podman), never Docker. Tests that
start the engine use Testcontainers through podman's own API service, started
on demand for the test session; no daemon and no host service is assumed. A
spike of 2026-11-27 (rootless podman 4.9.3, testcontainers 4.15.0) started
the system through that service and left nothing behind; two limits remain
(GAP-022).

The development container moves to the same family as the engine, Fedora with
the container runtime of its base image. How the pinned tools are installed in it is not settled
(GAP-021), so `.devcontainer/devcontainer.json` is unchanged and is to be
replaced.

### State: one volume

All state of the engine lives in one place, the database server, and the engine
is given one volume for it (R60), apart from the root of trust (below): the database server's data, which holds the
`idp` database of the token issuer, the secret store's sealed data
([ADR-0003](0003-secret-management.md)) and the configurator's state
([ADR-0006](0006-one-configurator-for-all-state.md)). One backup covers it (R20).
Restoring elsewhere needs the same root of trust, which is therefore kept apart
from the backups: it lives in its own declared volume, separate from the
database server's data and from the backups (R20). The inner container storage
is a further volume, but it holds no state of the engine.

When the image is booted, the volume is data of the machine, kept apart
from the operating system. An atomic upgrade or a rollback of the operating
system does not touch it.

### Upgrades converge

Code is static; an installation has state and a history. An upgrade replaces
what ships in the image. What lives in the volumes must be brought to the
new version's declared state at every start, not only at first start: roles
and privileges in the database server's catalog, identities, the secret store's
policies, and the extensions installed in databases.

The principle is in `anima-product-principles` (converge, do not initialize)
and the table of state stores and their configurators in
`anima-configuration-design`; this section applies them to the engine. A mechanism that runs only on an empty system
(`docker-entrypoint-initdb.d`, the secret store's self-initialization) is
enough for a first start but not for an upgrade. The database server's
`docker-entrypoint-initdb.d` may still create the empty cluster; everything
declared is applied by the configurator at every start. So the fixed roles are
declared as data and applied at every start ([ADR-0004](0004-roles-and-access.md)), and the extensions of
the template database are brought to the declared version in the same way.
The configurator is one for all state, OpenTofu with three providers
([ADR-0006](0006-one-configurator-for-all-state.md)); it sees only what is
declared.

The secret store's own self-initialization runs once only (GAP-020); its
policies converge through the configurator. The requirement is stated (R37)
and its verification is pending.

**When the image is booted**, the upgrade of the machine is atomic: it runs
wholly the previous version or wholly the new one, and a rollback returns to
the previous version (R51). The rollback restores the operating system and the
engine of the previous version. It does not restore the data written since:
data volumes are not rolled back. What is promised is therefore that nothing
written since is lost and that the previous version runs on it, which holds
only because a new version expands and never removes or narrows (R43,
`anima-designing-for-production`). Where a new version has already changed what it expands
in the volumes, a return is bounded by "expand only"; this ADR claims nothing
beyond it.

### Operations, Day 0 to Day 2

| Phase   | Covers                                 | Mechanism                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Day 0   | model, ADRs, build, images on GHCR     | `mise`, `buildah`, GitHub Actions, SysML v2 Pilot Implementation; disk images with `bootc-image-builder`                                                                                                                                                                                                                                                                                                                                                 |
| Day 1   | first start from an empty state        | the engine's units start in their declared order; a first-start unit with the `bao` command line generates the seed values; the secret store initializes itself and issues secrets and certificates ([ADR-0003](0003-secret-management.md)); the database server's `docker-entrypoint-initdb.d` may only create the empty cluster; the configurator unit applies everything declared, `keycloak-config-cli` for identities, and then the system is ready |
| Runtime | logins and refusals                    | PostgreSQL `oauth` method over TLS, `pg_oidc_validator`                                                                                                                                                                                                                                                                                                                                                                                                  |
| Day 2   | changed identities, backup and restore | the configurator applied again; `pgBackRest` for the database server, with the secret store and the root of trust ([ADR-0003](0003-secret-management.md)); for a booted host, the atomic upgrade and its rollback                                                                                                                                                                                                                                        |

- An adapter that runs in the database server's process is governed in three
  places: its fork and pin (`components.toml`), its build into the database
  server's image (the container file), and its activation. One that is on by default is created in the
  template database, so every database created later has it. `pgvector` is the
  first; `pg_oidc_validator` and `pgbackrest` are the other adapters that run
  in the database server's process ([ADR-0001](0001-hexagonal-architecture.md)). Its activation is reconciled at every start (see
  "Upgrades converge").
- Secrets and the TLS certificates are issued by the secret store, which
  initializes itself at first start ([ADR-0003](0003-secret-management.md)). Consumers get them from
  OpenBao Agent units through shared in-memory volumes.
- The first start is repeatable: a first start that fails is repeated from an
  empty state with the same command (R36, GAP-015).
- Upgrades are stated as a requirement (R37) and its verification is pending;
  see "Upgrades converge".

### Consequences

- Good, because the engine image is the unit that is tested, released and
  attested (R16, R24); the units it runs will live in `engine/image/`
  together with its container file, and will be validated without starting
  them (R52).
- Good, because an adopter is never asked to install or manage an
  orchestrator, and has one artefact with two ways to start it (R9, R50).
- Bad, because the image is an operating system, not only a program: it is
  bigger than a single-process image, and its base image is a distribution
  image whose licences are those of its packages (`components.toml`).
- Bad, because running the image as a container asks something of the
  container engine: two added capabilities (`SYS_ADMIN` and `SYS_PTRACE`) and
  a volume for the inner container storage.
- Good, because a change of the host's container engine cannot change the
  behaviour of the system, except through what the engine image asks of it.
- Good, because one store holds all state, so one backup restores everything
  together and no store can be out of step with another (R60, R20).
- Neutral, because readiness is declared by the units and costs nothing to
  ask; that it is honest costs a login, so its test needs a configured
  identity provider and a user.
- Good, because ready means converged: a start that cannot converge is not
  ready and takes no connection from outside (R40).
- Neutral, because each unit carries three checks and the engine one
  readiness answer (R41); a container became healthy through its declared
  checks, and the rest of what the health settings promise is not yet verified.
- Bad, because the operating system of a booted machine can be rolled back
  and the data cannot; the promise of R51 is bounded by "expand only".
- Neutral, because there are two installation parameters. The address has a
  safe default, `127.0.0.1`, so a system installed without it is reachable
  only from its own host; the public URL has no default and must be given.

### Confirmation

Pending, not written: R9 (`test_R9_single_command_start`), R29, R36, R40, R41,
R42, R48, R50, R51, R52, R60 and R61 (see `tests/pending.toml`). The evidence
below is from a spike, not from a test of this repository.

Observed on 2026-11-27 in a spike, with the pinned base image, which ships
podman 6.2.0 and systemd 262: the image builds from that base and runs as a
rootless container; the declared start order and the gate work, so nothing is
served before the configurator has succeeded; the inner images load from an OCI
directory by a unit at first start. Image size observed: 2.45 GB with two inner
images, of which 2.02 GB is the base image; there is no limit on the size of
the engine image.

Observed on 2026-11-27, running the engine image as a container with the two
added capabilities (`SYS_ADMIN` and `SYS_PTRACE`) and no full privilege: a
container became healthy through its declared checks. Before the second
capability, every exec into an inner container failed (GAP-034): the inner
container runtime opens the namespace files of the target process when it
executes a command in a container, a check that needs the capability, and a
health check is such a command. Not observed: the readiness target reached, a
failing check restarting its container, and the target staying unreached when
the configurator fails. **The design is unproven on those three points**, and
this record does not claim that the health settings behave as described
beyond a healthy container.

## Pros and Cons of the Options

### `podman kube play` on the host, from one Kubernetes manifest (the first attempt)

- Bad, because a manifest is a description for an orchestrator, and run by `podman kube play` it only imitated what an init system gives by design.
- Bad, because start order had to be obtained by restarts and the run-to-completion step had no natural place.
- Bad, because the checks of a container were whatever the host's podman version made of them: an older podman, observed on a development machine, ignores `readinessProbe`, does not restart on a failed `livenessProbe` (GAP-019) and copies the host's `/etc/hosts` into the pod's containers (GAP-018).
- Bad, because a product cannot be specified, tested and released as one thing if the runtime under it differs from machine to machine.
