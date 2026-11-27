---
number: 12
title: Declared once, converged, generated — how the facts of an installation are kept
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# Declared once, converged, generated — how the facts of an installation are kept

## Context and Problem Statement

Anima is configured from many files: the database server's configuration, the
access rules, the identities file, the secret store's configuration, the
engine's units, the registers and the documents. A fact typed in several of them
drifts, and an installation that is changed over time ([ADR-0011](0011-engine-image-and-runtime.md)) drifts with
it. Several rules that the repository already followed were not written down;
this ADR writes them, so that a proposal can be judged against them. The
dependency rule that completes them is in [ADR-0001](0001-hexagonal-architecture.md).

What is built today is small and is said so in each section. Everything else
here is decided, not built.

How are the facts of an installation kept so that they do not drift: declared once, applied at every start and generated where they can be derived?

## Decision Drivers

- A fact typed in several files drifts.
- An installation that is changed over time ([ADR-0011](0011-engine-image-and-runtime.md)) drifts with it.
- Several rules that the repository already followed were not written down,
  so a proposal could not be judged against them.

## Considered Options

- The principles of this ADR: declared once, converged, generated, organized
  by capability

No alternative was recorded when this decision was taken, so the chosen option is the only one listed.

## Decision Outcome

Chosen option: "The principles of this ADR: declared once, converged, generated, organized by capability", as the only option recorded; it writes down rules the repository already followed, so that a proposal can be judged against them.

### 1. Single source of truth

Each fact is declared in exactly one place. Every other occurrence of it is
derived from that place, or checked against it by a test (R39).

| Fact                                                   | Single source                                                                                   | Derived or checked                                                                                                                                             | Built today                                                                           |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| The fixed roles ([ADR-0010](0010-roles-and-access.md)) | One declaration of the roles, their kinds, memberships and scope                                | The database server's roles and privileges; the access rules; the scopes and realm roles in the identity provider's presets; the secret store's database roles | Not built. Decided here; `engine/` and `config/` hold only placeholders.              |
| The identity provider's public URL                     | One installation parameter, in the configuration ([ADR-0011](0011-engine-image-and-runtime.md)) | The identity provider's hostname; the issuer in the access rules; the name on the certificate; the host alias set in the engine's units                        | Not built.                                                                            |
| Secrets                                                | The secret store only ([ADR-0009](0009-secret-management.md))                                   | Consumers receive rendered copies in memory; none is in a repository, an image or a file on a volume                                                           | Not built. R7 is pending.                                                             |
| Versions of shipped components                         | `components.toml`                                                                               | The submodule pins, checked equal by a test                                                                                                                    | Built: `test_R11_every_dependency_pinned`.                                            |
| Versions of tools                                      | `mise.toml`                                                                                     | `mise.lock`, written by `mise`; exact versions checked by a test                                                                                               | Partly: exact versions are tested; that the lock file is current is not tested by us. |
| A requirement and its test                             | The verification's name in `model/anima.sysml`                                                  | The test with the same name; `tests/pending.toml`, generated                                                                                                   | Built: `test_R10_every_requirement_verified`.                                         |
| Files that can be derived (below)                      | The file they derive from                                                                       | The generated file, committed; `mise run generate:check` fails when it is stale                                                                                | Built: `test_R38_derived_files_generated`.                                            |

The same rule gives the layout of the places that already exist: one home per
kind of fact (the table of `AGENTS.md`), and one name per concept: the name of
a role is written in the declaration of the roles, never typed again in four
files.

### 2. Declarative over imperative

Whatever can be declared as data is declared as data. An imperative step is an
exception: it is listed, and it is treated as something to remove. Today the
list has two entries, the two first-start steps of the secret store described
in [ADR-0009](0009-secret-management.md) (generating the seed values; rotating the management password).

### 3. Generated over hand-written

Whatever can be derived from another file is generated and never maintained by
hand. A generated file is committed, so that a reader sees it, starts with a
comment that says it is generated and by which task, and fails the checks when
it is stale (R38). `mise run generate` writes every generated file;
`mise run generate:check` fails when one is out of date and writes nothing;
`mise run format` generates first. Built today:

| Generated file                   | Derived from                                                  |
| -------------------------------- | ------------------------------------------------------------- |
| `docs/adr/README.md`             | `adrs export json`, filtered with `jq`: number, title, status |
| `skills/README.md`               | the front matter of each `skills/<name>.md`                   |
| `.claude/skills/<name>/SKILL.md` | the front matter of `skills/<name>.md`                        |
| `tests/pending.toml`             | the model's JSON export and the names of the written tests    |

### 4. Converge, do not initialize

Every place that holds state has one declared file and one configurator that
applies it at every start, removals included. The first start is only the
first convergence (R37, [ADR-0011](0011-engine-image-and-runtime.md)). A mechanism that runs only on an empty
system is not a configurator.

| State store                                                   | Declared file                                           | Configurator | Status                                                                            |
| ------------------------------------------------------------- | ------------------------------------------------------- | ------------ | --------------------------------------------------------------------------------- |
| Identity provider: realm, identities, roles, scopes           | The engine's presets and the configuration's identities | OpenTofu     | Decided ([ADR-0014](0014-one-configurator-for-all-state.md)); nothing built here. |
| Secret store: policies, engines, roles                        | The engine's secret-store policies                      | OpenTofu     | Decided; the secret store's own self-initialization runs once only (GAP-020).     |
| Database server: roles, memberships, privileges, access rules | The declaration of the fixed roles                      | OpenTofu     | Decided; nothing built here.                                                      |
| Database server: installed extensions                         | The declared list of extensions                         | OpenTofu     | Decided; nothing built here.                                                      |

One configurator serves every row ([ADR-0014](0014-one-configurator-for-all-state.md)).
It sees only what is declared: an installation equals a new one for declared
objects, and something granted by hand on an object that no declaration tracks
stays.

**Never startable in an inconsistent state.** The system does not accept work
until it has converged to its declared state and that has been checked. A start
that cannot converge leaves the system not ready and closed, never
half-configured and serving. This is "fail closed" (below) applied to start and
upgrade: there is no state in which the database server accepts connections with
yesterday's roles and today's access rules. The start sequence is converge,
then become ready ([ADR-0011](0011-engine-image-and-runtime.md)). Start order is declared in the engine's units,
not obtained by restarts: the configurator is a unit that runs to completion at
every start and the units that serve are ordered after it, so nothing is
published before it has succeeded. The requirement is R40; its verification is
pending, and so is the mechanism.

**One start path, also after a crash.** There is no separate recovery
procedure: starting after an abrupt stop is a normal start, because every start
converges and the init system starts the units in their declared order. A
system stopped abruptly at any moment, including in the middle of a first start
or of an upgrade, reaches the ready state with the same start command
(R42; verification pending, mechanism not built).

### 5. Organized by capability, not by product

Directories, configuration and names are organized by the capability they
serve, never by the product that currently provides it: `access`, not
`keycloak`. Replacing an adapter then changes the files of that capability and
nothing else: no directory, no configuration key and no name has to be
renamed. The capability names under `engine/` and
`config/` mirror each other. Today the layout of [ADR-0006](0006-repository-and-toolchain.md) follows this rule:
`engine/access/`, `engine/secrets/`, `engine/backup/`, `engine/vectors/`,
`config/access/`.

### 6. SOLID, read at the level of the system

The five principles of object design apply to Anima's architecture, with a
port where an interface is and an adapter where a class is.

- **Single responsibility.** One port per contract and one tool per concern.
  An adapter may fill several ports; it says so, and each contract is tested
  on its own.
- **Open/closed.** Anima grows by adding ports, adapters and plugins, not by
  modifying the database server. When something is missing, an interface is added and
  never a shortcut ([ADR-0003](0003-plugin-boundary.md) states this for plugins).
- **Liskov substitution.** Any adapter of a port, the local stand-in
  included, can replace another without a requirement changing. The
  verifications of a port are therefore written against the port, never
  against a product, and every adapter of the port must pass that contract
  suite (R58).
- **Interface segregation.** A port is a narrow, standard contract: an OpenID
  Connect issuer, not "the Keycloak API".
- **Dependency inversion.** The database server knows ports, never adapters;
  adapters are named only by the engine's composition, its units and
  wiring ([ADR-0001](0001-hexagonal-architecture.md)).

### 7. Principles that were followed and are now written

- **Fail closed.** When something is wrong the system refuses rather than
  degrades: a check fails on a warning (`model:check`), a lock file that is out
  of date is an error, a role without the scope is refused (R34), a secret
  store whose initialization failed stays sealed (GAP-015), a start that
  cannot converge stays closed (R40).
- **Close classes of bugs by design.** Prefer a design in which a kind of
  error cannot happen over a check that catches instances of it. A database is
  closed with access rules rather than grants, so no database created later
  can be left open ([ADR-0010](0010-roles-and-access.md)); the secret store's API listens only on the
  loopback, so the question of its own certificate never arises ([ADR-0011](0011-engine-image-and-runtime.md));
  start order is declared, so no start can depend on a restart loop;
  derived files are generated, so they cannot drift from their source; a fact
  declared once cannot disagree with its copies; versions are pinned by
  digest, so "it changed underneath us" cannot happen; a new version only
  expands, so going back cannot meet a state it does not understand.
- **History is immutable.** Forks are merged, never rebased. A published tag
  is never moved. A requirement id or a gap id is never reused, and a closed
  gap stays in the register.
- **Exactly one.** One entry point (`mise run`), one declaration of the
  engine's units, one default adapter per port, and exactly one of them active (R28, R59), one home per kind of
  fact, one tool per concern, one way to run the system. The engine image is
  one artefact with two ways to start it: booted as the operating system of a
  machine, or run as a container ([ADR-0011](0011-engine-image-and-runtime.md)). Not: a second image, or a second
  declaration of the same containers, for one of the two ways. One container
  engine family, daemonless and rootless; no Docker.
- **Unattended at run time, deliberate at design time.** Start, restart,
  unlock and renewal need no person (R26). Decisions, version bumps and
  releases are made by a person, through a pull request.
- **Convention over invention.** Files and directories take the name and the
  place their ecosystem expects: `third_party/`, `mise-tasks/`, `CODEOWNERS`,
  `SECURITY.md`, `LICENSES/`.
- **The test is the judge.** "Ready", "compatible" and "restorable" mean that a
  named test passed, not that a component said so (R9, R20, R21).
- **A spike answers a question that can change a decision; otherwise the
  implementation is the verification.** A spike is throwaway code outside the
  repository, to find out whether something works. It is justified only while
  a decision is open and its answer could change it. Once the decision is
  taken, it is verified by building it in the repository with its tests. What
  a spike found goes into the repository as evidence, in the Confirmation of an
  ADR or an entry of `gaps.toml`; what worked in a spike is promoted, not
  rewritten.
- **Texts that do not age.** A text states a version, a size, a duration or any
  other measured number in two places only: the single source that pins or
  limits it (`components.toml`, `mise.toml`, a threshold in the model) and
  dated evidence (the Confirmation of an ADR: "observed on a date with a
  version"). Everywhere else it names the thing by its role: "the container
  runtime of the base image", not a version; "the pinned base", not a tag
  (R57).
- **Guardrails stop accidents.** What the configurator and the checks prevent
  is leaving the declared state by accident. Deliberate misuse by a holder of
  the superuser or of the root of trust is out of scope.

### 8. Expand only

A new version adds; it does not remove or narrow what an earlier released
version provided: roles, privileges, scopes, databases, installed extensions,
installation parameters, requirements. Version N+1 therefore runs on the state
left by version N, and going back to N after a failed upgrade is possible. This
matters most when the engine image is booted: its host is rolled back
atomically, but data volumes are not rolled back, so the previous version must
be able to run on the data the new one left (R51, [ADR-0011](0011-engine-image-and-runtime.md)).

Contraction, removing or narrowing something, is rare and ad hoc, and has one
paved way:

1. Things that hold data (a database, a volume, the secret store's mounts) are
   protected from destruction outright by the configurator's own guard, and an
   upgrade never removes them (R44).
2. Every other contraction is declared explicitly in one register, the root
   file `contractions.toml`: what is removed or narrowed, why, the released
   version that deprecated it and the version that removes it. It is a
   breaking change in the sense of Semantic Versioning and Conventional
   Commits. The register is built and empty; its fields are checked by
   `test_R45_contractions_register_well_formed`.
3. A check compares what the new version would remove from an installation of
   the last released version with the register, and fails unless the two are
   equal: nothing removed that is not declared, nothing declared that is not
   removed (R43).
4. A contraction is allowed only for something that a previous released
   version already marked as deprecated.

Not built: the check in point 3 and the guard in point 1. Their mechanism
depends on the configurator ([ADR-0014](0014-one-configurator-for-all-state.md)):
the guard of point 3 is a check on its planned actions. The rule applies to the model
too: a requirement id present at the last release must still exist, which is
the rule that ids are never reused (section 7). That comparison cannot run
before a first release exists, and none does.

### 9. Declared and tested upgrade paths

The versions from which an upgrade is supported are declared; to start with,
only from the previous released version. Each declared path is a test (R46;
verification pending). R37 states the outcome of any upgrade, that the
installation equals a new one; R46 states which upgrades are promised and that
each is exercised.

The declaration is the rule itself for now: an upgrade is supported only from
the immediately previous released version. There is no separate file until a
second path exists; when it does, where the declaration lives is decided then.

### 10. Reproducible builds

The same pinned sources produce the same image, bit for bit, so that "build
once, promote the artifact" ([ADR-0008](0008-trunk-main-green-and-releases.md)) can be checked by rebuilding (R47;
verification pending, not built; see [ADR-0006](0006-repository-and-toolchain.md)).

### 11. Two layers, two owners

An installation is two layers, each with one owner ([ADR-0001](0001-hexagonal-architecture.md) has the table):
the engine, owned by the product, which holds the fixed roles, the access
rules, the scopes, the secret-store policies and the configurator's presets,
inside the engine image and versioned with Anima; and the configuration, owned
by whoever adopts Anima, which holds the identities (who the users are and
which fixed roles they hold) and the installation parameters, outside the
image, in a directory mounted into the engine. The engine changes with a
release; the configuration changes without touching the engine. The boundary
coincides with the licence boundary of [ADR-0003](0003-plugin-boundary.md): configuration and data are not
covered by the AGPL.

Rules:

1. **Every fact has exactly one owner**: the engine or the configuration,
   never both. A fact the engine owns is not repeated in the configuration, and
   the reverse.
2. **The configuration is a public interface.** It is validated before the
   engine becomes ready: an invalid configuration leaves the engine closed and
   not ready, with a message the adopter can act on (R48). "Expand only"
   (section 8) applies to it: a new version does not break the files of those
   who already adopted (R43).
3. **The configuration's format is product-neutral.** It never uses an
   adapter's native format, so replacing an adapter breaks no adopter's files.
   An adopter needs to know neither the configurator nor any adapter (R49).
4. **No secret in the configuration.** Secrets stay in the secret store (R7).
5. **One configurator, two inputs.** The engine's presets and the adopter's
   configuration are applied by the same configurator at every start (section
   4). That configurator is OpenTofu ([ADR-0014](0014-one-configurator-for-all-state.md)); nothing of it is built by this record.

None of this is built: the directories `engine/` and `config/` hold only
placeholders, and the verifications of R48 and R49 are pending.

### 12. Fitness functions

A fitness function is an automated, objective check of a property of the
architecture. Here each one is a requirement of the model with a
verification written as a test in `tests/repository/`, so it runs with
every `mise run check`. Today:

<!-- fitness-functions:begin -->

- R7, secrets generated, when an image is promoted: `test_R7_secrets_generated` (pending).
- R9, single command start, when an image is promoted: `test_R9_single_command_start` (written).
- R10, every requirement verified, at every commit: `test_R10_every_requirement_verified` (written).
- R11, every dependency pinned, at every commit: `test_R11_every_dependency_pinned` (written).
- R17, component licenses allowed, at every commit: `test_R17_component_licenses_allowed` (written).
- R18, every file licensed, at every commit: `test_R18_every_file_licensed` (written).
- R25, every gap registered, at every commit: `test_R25_every_gap_registered` (written).
- R28, each port has one default adapter, at every commit: `test_R28_each_port_has_one_default_adapter` (written).
- R30, nothing reachable by default, against the running system: `test_R30_nothing_reachable_by_default` (written).
- R37, upgrade converges, when an image is promoted: `test_R37_upgrade_converges_to_new_installation` (pending).
- R38, derived files generated, at every commit: `test_R38_derived_files_generated` (written).
- R39, each fact declared once, at every commit: `test_R39_each_fact_declared_once` (pending).
- R40, serves only when converged, when an image is promoted: `test_R40_serves_only_when_converged` (pending).
- R41, probes and single readiness, when an image is promoted: `test_R41_probes_and_single_readiness` (written).
- R42, one start path after crash, when an image is promoted: `test_R42_abrupt_stop_recovers_with_same_start` (pending).
- R43, upgrade only expands, when an image is promoted: `test_R43_upgrade_removes_only_declared` (pending).
- R44, upgrade never destroys data, when an image is promoted: `test_R44_upgrade_never_destroys_data` (pending).
- R45, contractions register well formed, at every commit: `test_R45_contractions_register_well_formed` (written).
- R47, builds reproducible, when an image is promoted: `test_R47_builds_reproducible` (pending).
- R49, configuration names no adapter, at every commit: `test_R49_configuration_names_no_adapter` (pending).
- R52, engine parts validated without starting, at every commit: `test_R52_engine_parts_validated_without_starting` (written).
- R53, no product in requirement, at every commit: `test_R53_no_product_in_a_requirement` (written).
- R54, directories named by capability, at every commit: `test_R54_directories_named_by_capability` (written).
- R55, checks stay fast, at every commit: `test_R55_checks_stay_fast` (written).
- R56, every check seen to fail, at every commit: `test_R56_every_check_seen_to_fail` (written).
- R57, texts do not age, at every commit: `test_R57_texts_do_not_age` (written).
- R58, every adapter passes its contract suite, when an image is promoted: `test_R58_every_adapter_passes_its_contract_suite` (pending).
- R65, every setting has production default, at every commit: `test_R65_every_setting_has_production_default` (pending).
- R66, profile differs only in selection and data, at every commit: `test_R66_profile_differs_only_in_selection_and_data` (pending).
- R67, every adapter is part of the engine, at every commit: `test_R67_every_adapter_is_part_of_the_engine` (written).
- R68, limits held in model, at every commit: `test_R68_limits_are_held_in_the_model` (written).
- R69, fitness markers complete, at every commit: `test_R69_fitness_markers_are_complete` (written).
- R70, renovate finds every image, at every commit: `test_R70_renovate_finds_every_image` (written).
- R71, every test verifies requirement, at every commit: `test_R71_every_test_verifies_a_requirement` (written).
- R72, skills have one schema, at every commit: `test_R72_skills_have_one_schema` (written).
- R73, unverified rules counted, at every commit: `test_R73_unverified_rules_counted` (written).
- R74, skill paths match something, at every commit: `test_R74_skill_paths_match_something` (written).
- R75, every capability directory covered, at every commit: `test_R75_every_capability_directory_has_a_skill` (written).
- R76, routing reaches every skill, at every commit: `test_R76_routing_reaches_every_skill` (written).
- R77, role files well formed, at every commit: `test_R77_role_files_well_formed` (written).
- R78, vendor roles limited to permissions, at every commit: `test_R78_vendor_roles_limited_to_permissions` (written).
- R79, every open gap has task, at every commit: `test_R79_every_open_gap_has_a_task` (written).
- R80, task acceptance names verifications, at every commit: `test_R80_task_acceptance_names_verifications` (written).
- R81, size limits kept, at every commit: `test_R81_size_limits_kept` (written).
- R82, postmortem guards exist, at every commit: `test_R82_postmortem_guards_exist` (written).
- R83, postmortem status agrees with guards, at every commit: `test_R83_postmortem_status_agrees_with_guards` (written).
- R84, postmortem recurrence needs stronger guard, at every commit: `test_R84_postmortem_recurrence_needs_stronger_guard` (written).
- R85, postmortem not open too long, at every commit: `test_R85_postmortem_not_open_too_long` (written).
- R86, agent settings refuse generated files, at every commit: `test_R86_agent_settings_refuse_generated_files` (written).
- R87, catalog synonym keys exist, at every commit: `test_R87_catalog_synonym_keys_exist` (written).
- R88, agent layer evaluated at promotion, when an image is promoted: `test_R88_agent_layer_evaluated_at_promotion` (pending).
- R89, submodule working trees clean, at every commit: `test_R89_submodule_working_trees_clean` (written).
- R90, export writes nothing outside cache, at every commit: `test_R90_export_writes_nothing_outside_cache` (written).
- R91, no bytecode outside cache, at every commit: `test_R91_no_bytecode_outside_cache` (written).
- R92, advisory hook never blocks, at every commit: `test_R92_advisory_hook_never_blocks` (written).

<!-- fitness-functions:end -->

The rule: a fitness function that has never been seen to fail proves
nothing. Each has a companion test, named like it with the suffix
`_detects_violation`, that feeds the check a deliberately wrong input and
asserts that it reports the fault; the logic of the check is a function
that takes its inputs as arguments, so that the companion can do this.
R56 verifies that every verification in `tests/repository/` has its
companion. The exceptions, each with its reason, are listed in one place,
in the module of R56.

A requirement is marked as a fitness function in the model, with the
metadata `FitnessFunction` and a `trigger`: at every commit, when an image is
promoted, or against the running system. The list above is generated from
those markers by `mise run generate`; it is never written by hand. A threshold
is one named attribute of the requirement, with its unit, and the requirement's
text states no number; the test reads the value and asserts its unit, because
the Pilot Implementation does not check that a unit fits (GAP-035 to GAP-037).

### Consequences

- Good, because a proposal that adds a fact says where it is declared once
  and what derives from it; one that adds a file says whether it can be
  generated.
- Neutral, because the configuration is a promise to adopters: its format
  cannot change in a way that breaks an installed file without a declared
  contraction.
- Bad, because the roles, the public URL and the secrets are the facts most
  likely to be typed twice. None of their declarations is built yet, so the
  repetition is prevented today only by the files not existing; the tests
  that check it (R39) are pending.
- Bad, because the configurator is decided and nothing of it is built here.
  Until it is, R37 cannot be verified and [ADR-0011](0011-engine-image-and-runtime.md)'s "Upgrades converge"
  is a decision, not a mechanism.
- Neutral, because the two imperative steps of [ADR-0009](0009-secret-management.md) stay on the list
  until a configurator removes them.
- Neutral, because a release is the first point at which "expand only" and
  the upgrade paths can be checked against something; until one exists, R43,
  R44 and R46 have no baseline.

### Confirmation

Built and verified in `tests/repository/`: R10 (`test_R10_every_requirement_verified`), R11 (`test_R11_every_dependency_pinned`), R28 (`test_R28_each_port_has_one_default_adapter`), R38 (`test_R38_derived_files_generated`), R45 (`test_R45_contractions_register_well_formed`), R57 (`test_R57_texts_do_not_age`) and the fitness functions of section 12 (R53 to R56); the markers and the thresholds in the model have tests of their own. Pending, not written: R39, R37, R40, R42, R43, R44, R46, R47, R48, R49, R58, R59, R65 and R66 (see `tests/pending.toml`). The configurator is decided and nothing of it is built by this record.

## Pros and Cons of the Options

Only the chosen option was recorded, so there is no rejected alternative to weigh.
