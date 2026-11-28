---
number: 8
title: The HTTP entry point of the engine
status: proposed
date: 2026-11-28
category: architecture
decision-makers: [founder]
---

# The HTTP entry point of the engine

## Context and Problem Statement

The engine speaks HTTP in several places: the identity provider's login and
token paths, which people and applications reach and which the database
server's validator reads; its administration console and its management
endpoints, which nobody outside should reach; and, later, other services of
the engine and of the product built on it. Until now the identity provider
was published directly, serving TLS itself with a certificate of the secret
store ([ADR-0001](0001-hexagonal-architecture.md),
[ADR-0005](0005-engine-image-and-runtime.md)). That gives every service its
own exposure, its own TLS and its own answer to what may be reached, and it
leaves no single place that says which paths of the engine the world can see.

The engine must also work when it is not reachable from the internet, and the
applications inside talk to it with the engine's own certificate, so its TLS
cannot depend on a public certificate service.

How does HTTP enter the engine through one paved way, which paths does it
expose, and where does its certificate come from?

## Decision Drivers

- One place that says which paths of the engine are reachable, with everything
  else refused.
- The engine works when it is not reachable from the internet; no dependency
  on a public ACME service.
- The certificate is renewed by the mechanism that already renews the database
  server's, and a renewed one is taken without a restart
  ([ADR-0003](0003-secret-management.md), R118, R119).
- An adopter who is reached by name from the world can supply a certificate of
  their own, by one parameter and not by a procedure.
- The identity provider's management, health and metrics endpoints are never
  reachable from outside; its administration console only when the adopter
  turns it on.
- A port is a standard contract with a replaceable adapter
  ([ADR-0001](0001-hexagonal-architecture.md), `anima-designing-a-port`).

## Considered Options

- Kestrel with YARP, hosted by a minimal host program owned by Anima, behind a
  new port, the HTTP entry point
- Kestrel alone
- The application that the YARP project packages

No other reverse proxy was weighed in the spike that preceded this decision.
The founder chose the Kestrel and .NET family deliberately, because a wider
plan needs it; this record states that as the decision and does not argue it
again.

## Decision Outcome

Chosen option: "Kestrel with YARP, hosted by a minimal host program owned by Anima, behind a new port, the HTTP entry point", because Kestrel alone cannot forward a request, the packaged YARP application is not yet shipped as stable, and a host program of a few lines makes all routing and TLS configuration.

1. **A new port, the HTTP entry point, named `entry`.** Its contract: it is the
   single paved way for HTTP into the engine; it terminates TLS and forwards
   only the path prefixes the installation declares, each to a declared
   backend on the pod's loopback; every other request is answered 404. The
   directory is `engine/entry/`, and `config/entry/` when the installation
   declares something about it. Its default adapter is Kestrel (ASP.NET Core)
   with YARP on top, hosted by a minimal host program that Anima owns; the
   program contains no routing and no TLS setting, which are all configuration
   of the entry. No alternative adapter is built.
2. **The identity provider is the first backend and is no longer published
   directly.** It listens on the pod's loopback; the entry is the only
   listener published to the outside, and the public URL of the identity
   provider, the issuer, is the entry's. The public URL of the example
   installation becomes `https://localhost:8443`.
3. **What is forwarded.** Only the identity provider's login and token paths:
   `/realms/`, `/resources/` and `/.well-known/`. Its health, metrics and
   management endpoints are never forwarded, by any configuration. Its
   administration console is behind a route that is off by default and that
   the installation turns on by one setting, a feature flag of the
   installation; the configurator keeps using the administration API from
   inside the pod, never through the entry.
4. **Forwarding headers.** The entry sets and overwrites the `Forwarded` header
   of RFC 7239 from the connection it terminates, and removes every forwarding
   header a client supplied, so that the backend trusts the entry's header and
   nothing else.
5. **The certificate, by default, is the engine's own.** It is issued by the
   engine's certificate authority in the secret store, and renewed by the
   same mechanism as the database server's certificate, with the same
   lifetime and renewal share; the entry takes a renewed certificate without a
   restart. Its names include the public host of the installation. Applications
   inside the engine reach the entry with this certificate and trust the
   engine's authority, so no public certificate service is involved.
6. **An adopter may supply the certificate instead,** for a name the world
   reaches, through the same file interface as a supplied secret
   ([ADR-0003](0003-secret-management.md), R103). Choosing between the engine's
   certificate and a supplied one is one installation parameter of
   `config/entry/`, not a procedure.
7. **A client can obtain the engine authority's certificate** to trust the
   engine's certificate: a public document, never a secret. The way it is
   provided is chosen in the task that builds it; the requirement fixes the
   outcome (R134).
8. **Where the software comes from, and the two exceptions.** The .NET runtime
   and SDK come from a distribution that builds .NET from source, in its own
   packages, not from a fork of ours: building it from a fork is impractical.
   YARP comes from its NuGet package, pinned by version and by the content
   hash of the package, with a mirror fork of its repository for upstream
   contributions. That is an exception to "fork and build from source"
   (`anima-maintaining-a-fork`), recorded as a gap (GAP-057). The host program
   is a gap too (GAP-058), resolved when upstream ships a stable, configurable
   application. The release cadence of YARP is a governance risk of its own
   (GAP-059).
9. **Open, not decided: whether one listener must serve an internal name and a
   public name at once** (several certificates chosen by the name the client
   asks for, SNI). Today the entry presents one certificate for one set of
   names. The question is decided when an installation needs both names on the
   same listener; this record does not decide it.

### Consequences

- Good, because the exposure of the engine's HTTP is one list of path prefixes
  in one place, and everything not listed answers 404.
- Good, because the identity provider's TLS is no longer its own: it listens
  on the loopback in plain HTTP, and the entry holds the one certificate.
- Good, because the engine works with no internet reachability: its
  certificate comes from its own authority.
- Bad, because the engine now carries a .NET runtime and a host program of
  ours, and a library with a governance risk, for what a ready-made proxy
  would do.
- Bad, because the library and its pinning are an exception to building from
  source (GAP-057), and the host program a maintenance of ours (GAP-058).
- Bad, because the certificate and its key are two files: a renewal that
  replaces them one after the other could be read as a mismatched pair; the
  first test of the build is that they are replaced as one (TASK-87).
- Bad, because the entry's authority is the engine's own, so a client outside
  the engine must trust it, or the adopter supplies a certificate for a public
  name.
- Neutral, because the issuer URL changes with the entry: every place that
  repeats the public URL is derived from the one parameter, and the token
  validator must trust the engine's authority (TASK-88 checks that it accepts
  an authority's certificate file; that is unverified).
- Neutral, because the identity provider moves to production mode behind a
  TLS-terminating proxy (TASK-78): it serves HTTP on the loopback and takes
  the entry's `Forwarded` header, which the first build of the entry depends
  on.
- Neutral, because the YARP configuration has no deny route: a prefix cannot
  be forwarded with a sub-path refused. The `/realms/` prefix therefore also
  carries the identity provider's own administrative realm; whether that is
  refused by a route to nothing or by code is a check of the first task
  (TASK-86).

### Confirmation

Evidence of a spike on 2026-11-28; it is not a test of this repository, and nothing of the entry is built. Requirements R126 to R135 state the contract, and every verification is pending in `tests/pending.toml`: no test of the entry is written.

What the spike observed on 2026-11-28: Kestrel alone cannot forward a request, and YARP does (its package `Yarp.ReverseProxy`, MIT, last stable release 2.3.0 of 2025-02-27, targets .NET 8 and later and ran on .NET 10); the packaged application of the YARP project is preview only. .NET 10 is an LTS release (released 2025-11-11, supported to 2028-11-14). A host of the minimal form ran locally over plain HTTP, with a read-only root, all capabilities dropped, a non-root user, and answered the first proxied request 591 ms after its start, at 12 MB of idle memory, in an image of 235 MB (a Microsoft runtime image, not the base this record chooses). YARP's `Forwarded` transform (`for`, `host`, `proto`, action Set) overwrote forged headers; a trap: removing `X-Forwarded` in the same route also removed `Forwarded`. YARP had no stable release for about 21 months at that date, while its main branch was active.

What was only read, not run: Kestrel (version 8 and later) watches the certificate files named in its configuration and rebinds the endpoint when they change (aspnetcore pull request 49979); it does not react to a deletion; the endpoint gets a few seconds to drain. Whether replacing a key file and a certificate file one after the other can load a mismatched pair is unverified. Kestrel has no built-in ACME, and the known integration library is archived; neither matters here, because the certificate comes from the engine's authority. The distribution's package `aspnetcore-runtime-10.0` is published for Fedora 43 to 45, and its `dotnet10.0` package builds the official source-build tarball. The identity provider's pinned documentation says that behind a TLS-terminating proxy it runs in production mode with its hostname set to the full public URL, HTTP enabled and bound to the loopback, the `Forwarded` header trusted from the loopback, and its management interface on its own loopback port that is never proxied; its `hostname-admin` setting does not block the administration API.

Not run: TLS termination, the certificate reload, the host in the engine image, the engine's authority issuing the entry's certificate, a supplied certificate, the token validator trusting the engine's authority, the administration console route.

## Pros and Cons of the Options

### Kestrel alone

- Bad, because it cannot forward a request: observed in the spike of 2026-11-28.

### The application that the YARP project packages

- Bad, because the packaged application is preview only (not marked as shipping), so it would be a dependency on something upstream does not release; the own host is the gap (GAP-058) that this is meant to close when upstream ships it.

## More Information

The port table of [ADR-0001](0001-hexagonal-architecture.md) gains the row of the HTTP entry point. [ADR-0005](0005-engine-image-and-runtime.md) is amended: the public URL parameter is the entry's, and the entry is the one unit published to the outside. The skills `anima-access-design` and `anima-tech-keycloak` describe the identity provider behind it once built. Tasks: TASK-86 (the entry in front of the identity provider), TASK-87 (its certificate, renewal and pickup), TASK-88 (the public URL and the trust of the engine's authority), TASK-89 (a supplied certificate and the authority's certificate), TASK-90 (the administration console route). TASK-86 depends on TASK-78 (the identity provider in production mode).
