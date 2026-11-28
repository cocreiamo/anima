---
name: anima-writing-a-decision-record
description: "Use when a decision seems to need a record, or when creating, amending, superseding or checking one in docs/adr/: what a decision record is here (the architecture of the product only), where every other kind of decision goes, and how a record is written."
family: product
paths:
  - docs/adr/**
---

# Writing a decision record

A decision record in `docs/adr/` is a decision about the architecture of the
product, and nothing else. This skill says how to tell, where everything else
goes, and how a record is written. How the `adrs` tool behaves is
`anima-tech-adrs-madr`; where files live is `anima-repository-conventions`.

## Use this when

- A decision has been taken or is about to be, and you wonder where to write it.
- Creating, amending, superseding or deprecating a record.
- `mise run adr:check` fails, or a record cites another.

## Rules

1. **A record is a decision about the architecture of the product: what it is made of and how its parts relate.** Example: ports and adapters, secrets, roles and access, the engine image, the configurator, the configuration, the plugin boundary. The control question: does this decision change how the product is made, or how we work? If it changes how we work, it is not a decision record. Not: a record because a decision is important, taken with the founder or hard to reverse; importance does not make it architecture.
2. **Every other kind of thing has its home.** Legal and brand, process, tooling and principles: a rule of a skill (`anima-licensing-and-brand`, `anima-branching-and-releasing`, `anima-repository-conventions`, `anima-product-principles`). A rule a machine can check: the model, with its test (`anima-specifying-requirements`). A defect or limit of something adopted: `gaps.toml`. Something that went wrong: a postmortem in `docs/postmortems/`. Work to do: the backlog. How a technology behaves: its technology skill. Not: a record that collects any of these because it needs "somewhere to be written".
3. **Create the record with the record tool,** `adrs new "Title"` (the title in quotes), which gives the next number and the file `NNNN-slug.md`; then fill it in and run `mise run adr:check`. Not: writing the file by hand (the number may collide and the front matter may lack `number`, which hides the record without an error, GAP-044).
4. **The front matter is `number`, `title`, `status`, `date`, `category: architecture` and `decision-makers: [founder]`.** The decision maker is a role, never a person's name. `adrs new` writes the first four from the organization's template; the category and the decision maker are added by hand. Every record carries the category, and nothing but records and their generated index is in `docs/adr/` (R93).
5. **The sections are MADR 4.0.0:** Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome with Consequences (each prefixed Good, Bad or Neutral) and Confirmation, Pros and Cons of the Options (one subsection for each rejected option, with the reason) and More Information.
6. **Considered Options lists only options that were really considered.** Never invent one to fill the section; if none was, say so in one sentence, and say that no alternative was recorded. Not: a straw option written so that the choice looks reasoned; a rejected option whose reason nobody recorded is stated as "no reason was recorded", not given one.
7. **Confirmation names how the decision is verified:** the requirements and the tests (`test_R<id>_<what>`) that verify it, and says plainly what is not built and what no test checks. Evidence that came from a spike or a run carries its date and what was run, and says what was not observed. Not: "verified" for something that was only read.
8. **A version or a measured number appears in a record only as dated evidence, in Confirmation;** elsewhere the thing is named by its role. The rule is in `anima-specifying-requirements` (R57).
9. **A reference from one record to another is a Markdown link,** so that `adrs doctor` verifies it; a reference to a skill is its name in backticks. No text of the repository may name a record number that does not exist (R94). Not: a bare "ADR 0004" inside `docs/adr/`.
10. **Once a record is on `main` its number never changes,** and a withdrawn record is marked superseded or deprecated, never deleted. The decision of a superseded record stays readable.
11. **Write the requirement with the record.** A part of the decision that a machine can check becomes a requirement and a test in the same change; a part that is decided and not built is said so in Confirmation and in a pending verification.
12. **Do not write a record about how we work, and do not restate principles in one.** Not: fifteen records written in one day, eight of them about licensing, trademarks, authorship, the toolchain, forks, releases, the record format and principles; they were decisions about how we work and had to be moved into skills and deleted. Not: a record restating principles; one did, and it duplicated `anima-product-principles`, so that two texts had to be kept equal.
13. **Whether a record is really about architecture is judged case by case at review, and no check decides it** (confirmed by the founder on 2026-11-27). The checks are the category key and the layout (R93); none reads a record and judges its subject, and none is to be designed. Review applies the control question.

## Questions to answer before proposing

- Does this decision change how the product is made, or how we work? If the second, which skill, register or task is its home?
- Which options were really considered, and where is the reason each was rejected?
- Which requirements and tests verify it, and what is not built?
- Does the text state a version or number that a register holds, outside dated evidence?
- Does it supersede a record? Then the old one is marked, not deleted.

## Where the result goes

A new record to `docs/adr/` made with `adrs new`; its requirements to `model/requirements/` with their tests; the generated index by `mise run generate`. A decision about how we work goes to the skill that owns it. Related skills: `anima-tech-adrs-madr`, `anima-repository-conventions`, `anima-product-principles`.
