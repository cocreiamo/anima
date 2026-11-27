---
number: 2
title: Boundary between the core and plugins
status: proposed
date: 2026-11-27
category: architecture
decision-makers: [founder]
---

# Boundary between the core and plugins

## Context and Problem Statement

Agencies and third parties must be able to build on Anima without touching
its core, while every change to Anima itself stays in the core. The boundary
has to be precise enough to be checked by tools, not only stated in a text.
The licence that goes with the boundary is in `anima-licensing-and-brand`.

How is the boundary between the core and the plugins drawn in the structure of
the product, so that it is checked by tools?

## Decision Drivers

- Agencies and third parties must be able to build on Anima through public
  interfaces only.
- Every change to Anima itself stays in the core.
- The boundary has to be precise enough to be checked by tools, not only
  stated in a text.

## Considered Options

- Plugins as separate packages, kept out of the core's reach by Bazel
  `visibility`
- Nx to enforce the boundary between the core and the plugins

## Decision Outcome

Chosen option: "Plugins as separate packages, kept out of the core's reach by Bazel `visibility`", because Nx would be a second build tool beside Bazel (`anima-repository-conventions`).

### Terms

"Core" in this record means Anima's own code other than plugins. It is not the
PostgreSQL fork of [ADR-0001](0001-hexagonal-architecture.md), nor any other forked component: each keeps its
own licence (`anima-licensing-and-brand`). A plugin is a work that uses Anima
only through its public interfaces. Configuration and data lie outside the
core: this is the boundary between the engine, which the product owns, and an
instance's configuration, which the adopter owns ([ADR-0001](0001-hexagonal-architecture.md)).

### Marketplace

The marketplace is built in and lists official plugins only. No third-party
marketplace is planned.

### Rules for official plugins

These rules are enforced by automated checks, not by convention.

1. Each plugin is a separate package in `plugins/<name>/` with its own schema,
   commands, views, widgets and tests.
2. The core never imports a plugin. Bazel `visibility` enforces this: a plugin
   is not visible to the core, so a core target that depends on one does not
   build.
3. Official plugins use only the public interfaces available to agencies. If
   something is missing, an interface is added; there are no shortcuts.
4. Plugins are disabled by default and are enabled per application.
5. Official plugins live in the core repository.

### Consequences

- Good, because rule 3 makes the term "public interface" verifiable: what the
  official plugins use is, by construction, the public interface.
- Bad, because every capability an official plugin needs becomes a public
  interface that must be maintained.

### Confirmation

Not built. No plugin exists and there is no `plugins/` directory. The rules for official plugins say that they are enforced by automated checks, the rule that the core never imports a plugin by Bazel `visibility`; none of these checks exists yet and no requirement of the model verifies them. The licence terms of the boundary (the Plugin Exception) are a matter of `anima-licensing-and-brand`.

## Pros and Cons of the Options

### Nx to enforce the boundary between the core and the plugins

- Bad, because it would be a second build tool beside Bazel (`anima-repository-conventions`).
