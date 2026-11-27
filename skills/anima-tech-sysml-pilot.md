---
name: anima-tech-sysml-pilot
description: "Use when writing, validating or reading SysML v2 textual notation in Anima with the OMG Pilot Implementation: satisfy and verify references, thresholds with units, marking requirements with metadata, running the pilot as a checker, reading its JSON export."
family: technology
paths:
  - model/**
  - mise-tasks/model/**
  - tests/repository/sysml_model.py
---

# SysML v2 and the OMG Pilot Implementation

How the notation and the Pilot Implementation behave when run. The model's
conventions are in `anima-specifying-requirements`.

## Use this when

- Writing or changing `model/anima.sysml`.
- Adding a threshold (a duration, a size, a count) to a requirement.
- Marking requirements with a kind, a trigger or any other attribute.
- Changing `mise-tasks/model/check`, `mise-tasks/model/export` or `tests/repository/sysml_model.py`.
- Reading the model from a test.

## Rules

1. **Point `satisfy` and `verify` at requirement usages, not definitions.** A top-level requirement is `Package::name`; a nested one is `parent.child` with a dot. Example: `verify Runtime::invalidTokenRejected.tamperedTokenRejected;` in `model/anima.sysml`. Not: `satisfy x by <part>` with any part; a part whose type does not conform to the requirement's subject type gives "Bound features should have conforming types", and the check fails on warnings.
2. **Validate by feeding the interactive shell and failing on its output.** Write `%`, the model, `%`, then `%exit` and run `java -cp <jar> org.omg.sysml.interactive.SysMLInteractive <library dir> < input`; fail on any line containing `ERROR:` or `WARNING:` (`mise-tasks/model/check`). Observed on 2026-11-27 with the SysML v2 Pilot Implementation 0.63.1. Not: expecting a command-line validator; there is none and the exit status is always 0 (GAP-001).
3. **Export with the stand-alone exporter, from the directory holding a file named `model.sysml`.** Example: `java -cp <jar> org.omg.sysml.xtext.util.SysML2JSON -l <library> model.sysml "Kernel Libraries" "Systems Library" "Domain Libraries"` (`mise-tasks/model/export`). Not: `%export` as a shell command, which it is not; the output next to the input, because the exporter cuts the input path at the first dot and wrote outside the worktree once (GAP-003, PM-003); its own library, which fails on spaces in directory names (GAP-002, aliases with `%20`).
4. **Cache the export by the model's hash and write the cache atomically.** Not: expecting it to be fast; an export takes tens of seconds, dominated by loading the library, and two parallel exports once overwrote each other (`anima-tech-mise`).
5. **Qualify numbers: `ScalarValues::Integer`, `ScalarValues::Real`.** Not: unqualified `Integer` or `Real`.
6. **Hold a threshold as an attribute bound to a literal that a `require constraint` can refer to.** Example: `attribute maxStartTime : ISQ::DurationValue = 180 [SI::s];` with `require constraint { engine.startTime <= 180 [s] }` and `private import ISQ::*; private import SI::*;`; a count is `attribute max… : ScalarValues::Integer = <n>;`. Read the literal and unit from the export (`thresholds` in `tests/repository/sysml_model.py`). Not: a threshold from a `calc`, which cannot be read from the export; a byte or megabyte unit, because the library has bytes (`B`) but no prefixed byte units (GAP-037); trusting the unit, because a duration bound to `[B]` validates without a warning (GAP-035), so a test checks the unit in the export.
7. **Mark requirements with metadata and check the marker in a test.** Define `metadata def FitnessFunction { :> annotatedElement : SysML::RequirementUsage; attribute trigger : Trigger; }` with `enum def Trigger { enum commit; enum promotion; enum runtime; }` and apply it inside the requirement: `@FitnessFunction { trigger = Trigger::commit; }`. Not: expecting a missing required metadata attribute to be reported (GAP-036), or the `@` marking to produce an annotation relationship in the export; the marked element is the metadata usage's owner.
8. **Read the export through its wrapper.** Every element sits in a `payload` wrapper (`e.get("payload", e)`); read `ownedRelationship` then `ownedRelatedElement` (`relationships` and `children` in `sysml_model.py`). Not: expecting the export to be complete; it includes stubs of referenced library elements and omits most derived fields.
9. Unverified: other pilot releases than the pinned one. Also unverified: marking forms other than `@Name { … }` inside the requirement; the prefix `#` form and the standalone `metadata … about …` form are in `spike-sysml-fitness/m1_metadata.sysml`, but no finding records their result.

## Questions to answer before proposing

- Does `satisfy` point at a usage whose type conforms to the subject?
- Is every number a threshold in the model, with a unit where it is a quantity?
- Does a test check what the pilot does not (unit, marker attribute)?
- Does the check read the export, never the text?

## Where the result goes

Conventions to `anima-specifying-requirements`; the toolchain decision is `anima-repository-conventions` and the fitness functions `anima-product-principles`. Limits go to `gaps.toml` (GAP-001 to GAP-003, GAP-035 to GAP-037). Related skills: `anima-specifying-requirements`, `anima-repository-conventions`, `anima-tech-mise`.
