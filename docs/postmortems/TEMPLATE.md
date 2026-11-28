---
id: PM-000
date: 2026-01-01
title: "What went wrong, in a few words"
class: "The kind of error, in a few words"
status: open
guards: []
recurrences: []
---

<!--
Adapted from the post-mortem template of PagerDuty, Inc. (Apache-2.0,
https://github.com/PagerDuty/postmortem-docs, commit 88e5e97be2131780cdf54624a35791ca560e03c7).
Changes: the sections Overview, What happened, Root causes, Resolution, Impact,
Timeline and How did we do are kept; the meeting, the call recording, the
responders and the messaging are removed (a postmortem here records an event of
the repository's work, not an outage); the action items become Guards, and the
page is closed only by a guard that exists. Copy this file to
docs/postmortems/PM-<next number>-<slug>.md; ids are never reused.

Front matter
- status, strongest first: closed-by-design (it cannot happen again; a guard of
  kind design, ref the number of a decision record), guarded (a check stops it;
  a guard of kind test, ref the name of a test that exists and has a
  _detects_violation companion), mitigated (it can happen again, less likely and
  noticed; guards of kind scenario, detection or rule), open (no guard yet).
- A guard is { kind, ref, added }: added is the date it was put in place. The
  guard carries the id of the postmortem (in a test file, a decision record, a
  scenario or the line of a role or skill file), so that the link is checked.
- A failure of judgement by a person or an agent is never more than mitigated.
- recurrences lists the dates on which the event happened again. After the first
  recurrence, every further one needs a guard added on or after it that is
  stronger than the strongest guard in force before it.
- From PM-014 the sections Root cause, Class and earlier occurrences, Design
  options and Decision on the options are required and not empty (R166).
- An open postmortem is closed, or it fails the checks, within the limit held in
  the model.
-->

# PM-000: What went wrong, in a few words

## Overview

Two sentences: the event, its root cause and its impact.

## What happened

A short, factual description. No names of people.

## Root cause

The root cause, not the symptom, with the evidence for it (what was run or read). Include anything done during the response that made it worse, with the intention of learning from it.

## Class and earlier occurrences

The class of the event (the front matter's `class`) and whether the class occurred before: the postmortems and the gaps that belong to it, or that there are none.

## Resolution

What solved the problem, temporary and long-term.

## Impact

Be specific: what was affected, for how long, what was damaged or not.

## Timeline

| When | What |
| ---- | ---- |
|      |      |

## How did we do

What went well. What did not go so well.

## Design options

The changes of design that would remove the class, not the instance, with one recommendation. A change of design is built only after the founder approves it.

## Decision on the options

What the founder decided on each option and when, or that the decision is awaited. An instance fix alone never closes a class that has recurred.

## Guards

One line per guard of the front matter: what it protects against and why it has the kind it has. Say plainly what is not protected.
