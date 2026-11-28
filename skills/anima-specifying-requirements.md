---
name: anima-specifying-requirements
description: "Use when adding or changing Anima behaviour, writing a requirement, verification or test, or touching model/anima.sysml, tests/ or tests/pending.toml: SysML v2 conventions, test naming, traceability."
family: product
paths:
  - model/**
  - tests/**
---

# Specifying requirements

How behaviour is specified and verified in `model/anima.sysml` and `tests/`.

## Use this when

- Adding or changing behaviour of Anima.
- Writing a requirement, a verification or a test.
- Touching `model/anima.sysml`, `tests/` or `tests/pending.toml`.

## Rules

1. **The model is SysML v2 textual notation**, one file, `model/anima.sysml`,
   in the package `Anima`. Requirements are grouped in the packages `Day0`,
   `Day1`, `Runtime` and `Day2`, by when the rule must hold: before the
   system starts, at first start, in service, when a running system changes.
2. **A requirement never names a product.** It states what the system shall
   do, with "shall". Example: R8 says "the database server shall depend on the identity
   provider only through the OpenID Connect issuer contract", not "on
   Keycloak". Not: "Keycloak shall issue tokens with a scope".
3. **The subject is the port or part that must satisfy it** (`subject sys : System;`),
   not the product. A port is a `part def` specializing the abstract `Port`, and its
   adapter is a part usage, whether it runs in the database server's process or in its
   own container (ADR 0001).
4. **A product is a part usage, and `satisfy` links it** to the requirements
   it fulfils (`satisfy Day1::unattendedStart by anima.engine.openbao;`). Adding or
   changing an adapter changes usages and `satisfy` lines, never a requirement.
   Each port has one default adapter, alternatives may be selected, exactly
   one is active, and an adapter may fill several ports (R28, R59, tested by
   `tests/repository/test_architecture.py`). Every requirement is linked by
   one `satisfy` line.
5. **Each requirement has at least one verification** (R10), and each
   verification is a `verification def` whose objective is `verify <package>::<name>;`.
6. **Naming.** A verification is named exactly like its test:
   `test_<id>_<what>`, with the dot of a sub-requirement written as an
   underscore. Example: R3.1 is `test_R3_1_tampered_token_rejected`.
7. **Ids are stable and never reused.** A removed requirement leaves its id
   unused. New requirements take the next number; the order in the file does
   not matter.
8. **`tests/pending.toml` only shrinks, and is generated.** It lists the
   verifications whose test is not written, computed from the model's export
   and the names of the tests by `mise run generate`; never edit it. It grows
   only when a requirement is added, and it is empty at 0.0.1. Write the test
   and regenerate, or add the verification and regenerate.
   `tests/repository/test_traceability.py` fails when a verification is neither
   tested nor pending, when a pending one has been written, and when the file
   is not the generated one.
9. **The model is validated by the OMG Pilot Implementation**
   (`mise run model:check`) and warnings fail the check. Nothing validates it
   by eye. The pilot has no command-line validator (GAP-001); the task is the
   workaround.
10. **The traceability test reads the model's JSON export** (`mise run model:export`,
    GAP-002), never the text of the file. Not: a regular
    expression over `anima.sysml`.
11. **A design decision that a machine can check becomes a requirement and a
    test.** Example: ADR 0004's "every rule that accepts tokens requires a
    scope" is R34; "the identity provider's database stays closed for databases
    created later" is R27 and R32.
12. **Negative cases get their own requirement.** Example: R3 is split into
    R3.1 tampered, R3.2 expired and R3.3 foreign issuer. Not: one "invalid
    tokens are refused" test that covers one case.
13. **A known trap becomes a test that forbids it.** Example: R33, a token
    issued to another client of the same realm is refused (GAP-006); R34 forbids
    an empty scope (GAP-011).
14. **Where a test lives.** Verifications that need only the repository are in
    `tests/repository/`; those that start the engine image with Testcontainers
    through podman's API service, never Docker, are in `tests/system/` (ADR
    0005). Tests are
    written with `pytest`; a test may run an adopted tool and assert on its
    result. Token logins use `oauth_hook_client`.
15. **A requirement that cannot be verified is not accepted.** If no test can
    show it, rewrite it until one can, or do not add it.
16. **Nothing is checked outside the model.** Every check of the repository is a
    requirement with a verification named like its test, marked as a fitness
    function with its trigger, and with a `_detects_violation` companion; a
    test that is neither is a fault (R71). Every limit or count a check uses
    is a threshold in the model (`maxSkillLines`, not a constant in the test),
    and the requirement text states no number. A helper test that verifies
    nothing is justified in one line where it lives.
17. **Texts that do not age (R57).** A text states a version, a size, a
    duration or any other measured number only at the single source that pins
    or limits it (`components.toml`, `mise.toml`, a threshold in the model) or
    as dated evidence (a paragraph or list item that says it was
    observed and carries a date: "observed on 2026-11-27 with <name> <version>").
    This is the one home of this rule; other texts point here.
    Everywhere else it names the thing by its role: "the container runtime of
    the base image", not a version; "the pinned base", not a tag. A check
    fails when a skill or a requirement states the version of a component or
    tool.
18. **A fitness function is a requirement marked in the model** with the metadata `FitnessFunction` and a trigger: at every commit, when an image is promoted, or against the running system. It is an automated, objective check of a property of the architecture, with its verification written as a test, so that it runs with every `mise run check`. A check that has never been seen to fail proves nothing: each has a companion `<name>_detects_violation` that feeds it a deliberately wrong input, which is why the logic of a check is a function of its inputs; R56 verifies the pairing, and the exceptions, each with its reason, are listed in one place in its module. The list of fitness functions is generated into `docs/catalog.md` from the markers. A threshold is one named attribute of the requirement with its unit, the requirement's text states no number, and the test reads the value and asserts its unit because the Pilot Implementation does not check that a unit fits (GAP-035 to GAP-037).
19. Unverified: **the end-to-end test of the device flow of `psql` in a browser** (Playwright). It is decided and no such test is written.

## Questions to answer before proposing

- Which port or part is the subject?
- Is any product name in the text? Remove it.
- Which package: Day 0, Day 1, Runtime or Day 2?
- What is the verification, and what is the test's exact name?
- Which negative cases does it have, and does each have its own requirement?
- Is a gap involved (`GAP-nnn`) that a test must forbid?
- Does the requirement hold for what is created after installation, and after
  an upgrade?
- Is the test written now, or left pending (run `mise run generate`)?

## Where the result goes

The requirement, its `verification def` and its `satisfy` line go to
`model/anima.sysml`; the test to `tests/repository/` or `tests/system/`; an
unwritten test appears in `tests/pending.toml` by generation. If the requirement follows from a
decision, the ADR cites its id (R-number).
