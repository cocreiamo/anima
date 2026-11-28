---
name: anima-entry-design
description: "Use when changing how HTTP enters the Anima engine: the HTTP entry point (its host program, its routes, its listener and certificate, the headers it sets), what it forwards and refuses, or anything under engine/entry/ or config/entry/."
family: capability
paths:
  - engine/entry/**
  - config/entry/**
---

# Entry design

How HTTP enters the engine: the capability `entry`, the HTTP entry point
(directories `engine/entry/` and `config/entry/`). The decisions are taken; their
home is ADR 0008. The identity provider behind it is `anima-access-design` and
`anima-tech-keycloak`; the certificate it presents is `anima-secrets-design`.

## Use this when

- Adding, changing or removing a path prefix that the engine exposes.
- Changing the headers the entry sets, or what it does with those a client sent.
- Changing its listener, its certificate or its container.
- Touching anything under `engine/entry/` or `config/entry/`.

## Rules

1. **One list says what the world can reach, and everything else is 404.** The list is the routes of `engine/entry/appsettings.json`: `/realms/`, `/resources/` and `/.well-known/`, each to the identity provider on the pod's loopback (`http://127.0.0.1:8080/`). Not: a second place that exposes a path, a service published beside the entry (R128, R135). Observed on 2026-11-28 by `tests/system/test_entry.py`.
2. **The host program holds no route and no TLS setting.** `engine/entry/Program.cs` loads the library and its configuration; the routes are `appsettings.json`, the listener and the certificate paths are `Kestrel__...` settings of the unit and of the listen address file (`engine/entry/entry.container`, `engine/image/anima-listen`). Not: a route, a port or a certificate path in code (GAP-058).
3. **A request under `/realms/master/` is refused by the route that does not match it, with 404.** The path of the realms route is `/realms/{realm:regex(^(?!master$).+$)}/{**rest}`: a request for the identity provider's administrative realm, in any case and with an encoded or dot-segment spelling, matches no route and the entry answers 404. Observed on 2026-11-28: `/realms/master`, `/realms/master/`, `/realms/Master/...`, `/realms/%6daster/...` and `/realms/anima/../master/...` were answered 404 by the entry alone and through the engine, where the provider would have answered 200 (`tests/system/test_entry.py`, R128). The choice for the check of ADR 0008: neither a route to nothing (not tried; a cluster with no destination is a route that matches and then fails, so it would not be a 404) nor code (the host program stays free of routing). Not: a deny route; the library has none.
4. **What is never forwarded is a list in the host program, not in the configuration.** A path with a segment `health`, `metrics`, `management` or `q`, in any case, is answered 404 before any route is looked at, so a configuration that declares a catch-all or a route to such a path still does not forward it (R129). Observed on 2026-11-28 with the entry alone: routes declared for `/{**rest}`, `/health/{**rest}`, `/metrics` and `/management/{**rest}` forwarded only `/robots.txt`. The identity provider's management interface is on its own loopback port (9000) that no route names. Not: a deny list in the configuration, which the configuration could empty.
5. **The entry makes the `Forwarded` header and removes the others.** Each route sets `Forwarded` (`for,host,proto`, action `Set`, `ForFormat` `IP`: the address of the client, not an obscured name) and removes each `X-Forwarded-*`, `X-Original-Forwarded-For`, `X-Real-IP`, `Front-End-Https` and `X-Url-Scheme` header one by one (R132). Observed on 2026-11-28 with a stand-in backend: forged values of all of them were replaced or removed, and a request that sent none got the same `Forwarded`. Not: the transform `X-Forwarded` with the action `Remove`; observed in the spike of 2026-11-28 (ADR 0008) to remove `Forwarded` as well. Not: the default `ForFormat` (`Random`), which names the client by a generated token that the identity provider cannot use for its events.
6. **The identity provider trusts the loopback and nothing else.** It runs with `--proxy-headers=forwarded --proxy-trusted-addresses=127.0.0.1/32` and listens on `127.0.0.1` in both ways of starting; the entry is the only listener that follows the way of starting (`anima-image-design`, rule 9). Not: the provider published, or trusting the header from another address (R135).
7. **The first build presents a certificate issued once per start.** `engine/entry/entry-certificate` (unit `entry-certificate.service`) signs a request with the secret store's role of the database server, for `localhost` and `127.0.0.1`, into `/run/anima/entrytls` in memory, owned by the entry's user; no renewal, and the entry does not reload (R126; R127 stays pending, TASK-87). Its role of its own, the public host of the installation and the supplied certificate are TASK-87, TASK-88 and TASK-89. Not: a certificate in an image, or a key in a volume.
8. **The entry runs read-only, with a user of its own and no capability.** User 1011, a read-only root, a tmpfs for `/tmp`, `DropCapability=ALL`, `NoNewPrivileges`; its checks are a connection to the listener, because the image has no TLS client (`engine/entry/entry-check`). Observed on 2026-11-28 (`tests/system/test_engine.py`, R41). Not: a health route (R128: nothing answers that is not declared).
9. **The software comes from packages and a pinned package, not from a fork (GAP-057).** The base is the distribution's minimal image, by the digest of its image index; the runtime and the SDK are its packages, by version; the library is its NuGet package, by version, by the SHA-256 of the file (checked by the build) and by the content hash in `packages.lock.json` (a locked restore). The register is `components.toml` and a test compares (`tests/system/test_entry_static.py`). Not: a floating tag, an unlocked restore. Unverified: how long the distribution's repository keeps a package version; when it drops one, the build fails and the pin is moved.
10. **The entry's own tests run its image alone.** `tests/system/test_entry.py` starts the image on the host's network, read-only, non-root and with no capability, in front of a stand-in backend that records what it receives, with the backend's address and a plain listener set by environment: it can read what the backend was sent, which the identity provider cannot show. Not: a test of the headers through the identity provider only.

## Questions to answer before proposing

- Which prefix is new, to which backend on the loopback, and does a sub-path of it need refusing (the library has no deny route)?
- Does anything new reach the outside by another way than this entry?
- Does a client-supplied header reach the backend, and does the backend trust a header it should not?
- Which requirement, which test, and which `_detects_violation` companion cover it?

## Where the result goes

A decision amends ADR 0008. A prefix, a route or a transform is `engine/entry/appsettings.json` and a test of `tests/system/test_entry.py`; what the adopter declares about it goes to `config/entry/` and `anima-configuration-design`. The rule becomes a requirement and a test (`anima-specifying-requirements`); limits go to `gaps.toml` (GAP-057 to GAP-059). Related skills: `anima-image-design`, `anima-tech-keycloak`, `anima-adopting-a-component`, `anima-designing-a-port`.
