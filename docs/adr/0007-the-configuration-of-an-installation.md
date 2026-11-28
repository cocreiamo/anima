---
number: 7
title: The configuration of an installation
status: proposed
date: 2026-11-27
category: architecture
decision-makers: [founder]
---

# The configuration of an installation

## Context and Problem Statement

The configuration is what an adopter declares about their own instance: it
lives outside the engine and is read by it at every start
([ADR-0001](0001-hexagonal-architecture.md),
`anima-configuration-design`). That
leaves open how it is organized: how an adopter writes only what differs from
a production installation, how local development differs from production, and
where secrets are.

How is the configuration organized so that an adopter writes only what
differs, local development is a special case of production, and no secret is
in a file?

## Decision Drivers

- Production is the default; local is the special case
  ([ADR-0005](0005-engine-image-and-runtime.md)).
- An adopter writes only what differs from the default.
- The configuration is a public interface and names no adapter's native format
  (R49).
- No secret value in a configuration file (R7, R103).
- A wrong setting is refused before the engine becomes ready (R48).

## Considered Options

- Declarative data, one file or directory per capability, a production default
  for every setting, and profiles as overlays over a production-shaped base
- Environment variables only
- One flat file
- An adapter's native formats
- Per-environment copies of the whole configuration

## Decision Outcome

Chosen option: "Declarative data, one file or directory per capability, a
production default for every setting, and profiles as overlays over a
production-shaped base", because a profile that is an overlay keeps local a
special case of production, and a copy would drift.

1. Everything an adopter sets is declarative data. Adapters are code and live
   in the engine; choosing one is configuration.
2. There is one file or directory per capability under `config/`, with the
   capability names of `engine/`.
3. Each capability carries a setting that names the active adapter, the
   driver, and that adapter's own settings
   ([ADR-0001](0001-hexagonal-architecture.md)). Exactly one adapter of a port
   is active (R59).
4. The engine ships a production default for every setting, and an adopter
   writes only what differs (R65).
5. Profiles are overlays over a production-shaped base. The local profile,
   `config/profiles/local/`, selects stand-ins, the loopback address and the
   example identities. They are merged in a fixed order, the engine's defaults,
   then the base, then the profile, by the configurator's own functions
   ([ADR-0006](0006-one-configurator-for-all-state.md)).
6. A profile may only select an adapter or a stand-in and set installation
   parameters and data. It never changes the engine's wiring (R66, a fitness
   function).
7. A setting that is unknown or forbidden is refused before anything changes
   and before the engine becomes ready, and the message names it (R48).
8. No secret value is written in a configuration file. A setting that needs a
   secret names it, and the value arrives as a file from the host's secret
   mechanism (R103).

The style resembles the configuration of application frameworks: a file per
concern, defaults shipped, values from the environment. That is inspiration,
not an adopted tool.

### Consequences

- Good, because an adopter's configuration is small: only the differences from
  the production default.
- Good, because local is an overlay, never a copy, so it cannot drift from
  production.
- Good, because a secret is never in a file that is versioned or copied.
- Bad, because every setting needs a production default shipped in the engine,
  which is work for each capability and a promise to adopters that cannot be
  narrowed without a declared contraction
  (`anima-designing-for-production`).
- Bad, because the merge order and the rules on what a profile may change are
  ours to implement and to test.
- Neutral, because the guardrails stop accidents, not a determined owner of the
  installation.

### Confirmation

Observed on 2026-11-27 by the system tests: the configuration is read in layers (the engine's defaults, the base, the profile), an unknown, forbidden or secret setting is refused naming it with nothing written, an absent setting takes its default, and a secret named by a `_file` setting arrives as a file and never as a value (R48, R95, R103, written). Pending, not written: R65 (`test_R65_every_setting_has_production_default`), R66 (`test_R66_profile_differs_only_in_selection_and_data`, marked as a fitness function), R59 and R7 (see `tests/pending.toml`). Written in the configurator's tests: R49. The configuration of the engine is the example one in `config/`; an adopter's own was not tried.

## Pros and Cons of the Options

### Environment variables only

- No reason was recorded.

### One flat file

- No reason was recorded.

### An adapter's native formats

- Bad, because the configuration would name an adapter, and replacing the
  adapter would break the adopter's files (R49).

### Per-environment copies of the whole configuration

- Bad, because copies drift, and local would stop being a special case of
  production.

## More Information

Configuration in the repository: `config/` holds the example configuration
that tests and local development use; an adopter mounts their own.
