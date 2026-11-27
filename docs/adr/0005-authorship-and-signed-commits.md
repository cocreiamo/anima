---
number: 5
title: Authorship, AI assistance and signed commits
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# Authorship, AI assistance and signed commits

## Context and Problem Statement

Part of the work is written with an AI assistant. The copyright holder must
be able to stand behind every change, and readers must be able to see how a
change was produced.

How does the copyright holder stand behind every change, and how can readers see how a change was produced, when part of the work is written with an AI assistant?

## Decision Drivers

- The copyright holder must be able to stand behind every change.
- Readers must be able to see how a change was produced.

## Considered Options

- Review by the founder, signed commits and a `Co-Authored-By` trailer for
  AI assistance

No alternative was recorded when this decision was taken, so the chosen option is the only one listed.

## Decision Outcome

Chosen option: "Review by the founder, signed commits and a `Co-Authored-By` trailer for AI assistance", as the only option recorded.

1. Every commit is reviewed by the founder and signed with the founder's GPG
   key (fingerprint `4898A14E659F7175D2EDCE7F9B54A8DF5D99575C`).
2. Commits made with AI assistance keep the `Co-Authored-By` trailer naming
   the assistant, for transparency.
3. Nothing is committed or pushed without the founder's approval.

### Consequences

- Neutral, because an unsigned commit on `main` is a defect.
- Good, because the history shows which changes had AI assistance.

### Confirmation

The ruleset in `.github/rulesets/main.json` contains the rule `required_signatures`; that the ruleset is applied on GitHub is a GitHub setting that no test of this repository verifies. The `Co-Authored-By` trailer and the founder's approval are not checked automatically.

## Pros and Cons of the Options

Only the chosen option was recorded, so there is no rejected alternative to weigh.
