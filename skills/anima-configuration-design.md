---
name: anima-configuration-design
description: "Use when touching anything under config/ or any setting the engine reads: what an adopter configures, defaults, profiles, the driver that selects an adapter, and where secrets are named."
family: capability
paths:
  - config/**
---

# Configuration design

What an adopter declares about their own instance, and how the engine reads it:
the capability `configuration` (directory `config/`, mirroring `engine/`). The
decisions are taken; their home is ADR 0007
(the configuration), ADR 0001 (the
two layers, drivers) and this skill.

## Use this when

- Adding, changing or removing a setting the engine reads.
- Touching anything under `config/`, including the local profile.
- Choosing which adapter of a port is active.
- Deciding whether something belongs to the engine or to the adopter.

## Rules

1. **Everything an adopter sets is declarative data.** Adapters are code and
   live in the engine; choosing one is configuration. Not: a script, or an
   adapter's native format (R49).
2. **One file or directory per capability under `config/`**, with the names of
   `engine/`. Not: one flat file; settings scattered by product.
3. **Each capability carries a driver**: a setting that names the active
   adapter, plus that adapter's own settings (ADR 0001). Exactly one adapter
   of a port is active (R59).
4. **Every setting has a production default shipped in the engine**, and an
   adopter writes only what differs (R65). Not: a setting that must be written
   for the engine to be sound.
5. **Two layers, two owners, one configurator with two inputs.** A fact is the
   engine's or the configuration's, never both. The engine's presets and the
   adopter's configuration are applied by the same configurator at every start
   (ADR 0006).
6. **Local is an overlay, never a copy.** A profile (for example
   `config/profiles/local/`) is an overlay over a production-shaped base. The
   merge order is fixed: the engine's defaults, the base, the profile, by the
   configurator's own functions. Not: a whole copy of the configuration per
   environment, which drifts and makes local something other than a special
   case of production.
7. **A profile may only select a stand-in or an adapter and set parameters and
   data.** It never changes the engine's wiring (R66, a fitness function). Not:
   a profile that edits a unit.
8. **An unknown or forbidden setting is refused before anything changes**, and
   the engine does not become ready; the message names the setting (R48).
9. **No secret value in a configuration file** (R7). A setting that needs a
   secret names it; the value arrives as a file from the host's secret
   mechanism. See `anima-secrets-design`.
10. **The format is a promise to adopters.** It is validated before ready and
    follows "expand only": a new version accepts every configuration the
    previous released version accepted (R43).
11. **The style is inspired by the configuration of application frameworks**
    (a file per concern, defaults shipped, values from the environment). It is
    inspiration, not an adopted tool.
12. **Facts of an installation are declared once, in these homes.** The fixed
    roles: one declaration of the roles, their kinds, memberships and scope;
    the database server's roles and privileges, the access rules, the scopes
    and realm roles of the identity provider's presets and the secret store's
    database roles derive from it. The identity provider's public URL: one
    installation parameter; its hostname, the issuer in the access rules, the
    name on the certificate and the host alias of the units derive from it.
    Secrets: the secret store only; consumers receive rendered copies in
    memory, none is in a repository, an image or a file on a volume (R7).
    Component versions: `components.toml`; tool versions: `mise.toml`.
    Unverified: none of the first three declarations is built, so their
    repetition is prevented only by the files not existing; the test that
    checks it is pending (R39).
13. **One configurator serves every state store.** The identity provider
    (realm, identities, roles, scopes), the secret store (policies, engines,
    roles) and the database server (roles, memberships, privileges, access
    rules, installed extensions) each have one declared file and are converged
    by the same configurator (ADR 0006). It sees only what is declared: something granted by
    hand on an object that no declaration tracks stays. The secret store's own
    self-initialization runs once only and is not converged (GAP-020). Not
    built: the configurator.

## Questions to answer before proposing

- Is this the engine's fact or the adopter's, and not both?
- What is the production default, and can the adopter omit the setting?
- Which driver selects the adapter, and what are the adapter's own settings?
- Does the local profile only select, set parameters and data?
- What happens to an unknown key, and does the message name it?
- Does any value in a file need to be a secret? Then name it instead.
- Which test, and which requirement (R-number), covers it?

## Where the result goes

A decision amends ADR 0007. The rule becomes a requirement and a test (see
`anima-specifying-requirements`). The example configuration lives in
`config/`.
