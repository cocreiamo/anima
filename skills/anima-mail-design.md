---
name: anima-mail-design
description: "Use when changing outgoing mail in Anima: the mail port, the engine's client of the adopter's SMTP service, the local mail catcher that stands in for it, the mail settings of the configuration, or anything under engine/mail/ or config/mail/."
family: capability
paths:
  - engine/mail/**
  - config/mail/**
---

# Mail design

Outgoing mail: the capability `mail` (directories `engine/mail/` and
`config/mail/`). The decisions are taken; their home is ADR 0001 (the port
table). What an adopter declares is `anima-configuration-design`.

## Use this when

- Changing how the engine sends mail, or the settings of the mail service.
- Changing the local mail catcher or the way the local profile selects it.
- Touching anything under `engine/mail/` or `config/mail/`.

## Rules

1. **The contract of the port is SMTP.** Its default adapter is the engine's client and wiring for the SMTP service that the configuration names; the service runs outside the engine and its adapter is inside it (ADR 0001, R64). Not: a mail server shipped as the production path.
2. **The local mail catcher is the stand-in,** selected by the configuration and never by a change to a unit; it keeps the messages in memory and delivers none, and neither its API nor its SMTP port is published. Not: the catcher as the production default.
3. **The mail settings have production defaults in the engine, and the adopter writes only what differs** (R65). The password of the mail service is never written in the configuration: the setting names a file that the host provides (R103).
4. **A declared identity receives a message with a link to set its credential** through this port (R96). Not: a credential written in a file (R63).
5. **The catcher keeps a message that is sent to it.** Observed on 2026-11-27: a message sent to the stand-in's SMTP port is listed by its API (`tests/system/test_services.py`, R64). Unverified: delivery through an adopter's SMTP service, and the configurator setting the identity provider's outgoing mail (R96, a task is in the backlog).
6. **The mail stand-in is bounded like every unit** (`engine/image/envelopes.toml`, R203); it is counted apart from the engine's total, because it runs only with the catcher driver (R204).

## Questions to answer before proposing

- Is the setting the engine's default or the adopter's, and is the default the production one?
- Does the stand-in stay a stand-in, selected by the configuration alone?
- Does any value in a file need to be a secret? Then name it instead.
- Which test, and which requirement (R-number), covers it?

## Where the result goes

A decision amends the port table of ADR 0001. The rule becomes a requirement and a test (`anima-specifying-requirements`). The units and the container file live in `engine/mail/`; the example configuration in `config/mail/`. Related skills: `anima-configuration-design`, `anima-designing-a-port`.
