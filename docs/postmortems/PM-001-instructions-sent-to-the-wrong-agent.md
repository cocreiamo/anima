---
id: PM-001
date: 2026-11-27
title: Instructions sent to the wrong agent, twice
class: error of judgement of the coordinating agent
status: mitigated
guards:
  - kind: rule
    ref: agents/coordinator.md
    added: 2026-11-27
  - kind: rule
    ref: agents/implementer.md
    added: 2026-11-27
  - kind: scenario
    ref: S-1
    added: 2026-11-27
recurrences:
  - 2026-11-27
  - 2026-11-27
---

# PM-001: Instructions sent to the wrong agent, twice

## Overview

During the setup of this repository the coordinating agent ran several agents at once and addressed its follow-up messages by identifiers it kept by hand. Twice it swapped two identifiers, so corrections meant for the agent editing the repository reached an agent running a spike. No file was damaged.

## What happened

Two agents ran at the same time: one edited the repository, one ran a spike outside it. Follow-up messages went to a hand-kept identifier of each. Twice the identifiers were swapped. The corrections for the agent editing the repository reached the spike agent, and the intended agent worked without them for a while.

## Root causes

The coordinator addressed agents by identifiers it held in its own context and did not check the recipient's role before sending. The error is one of judgement, so it is not deterministic.

## Resolution

The spike agent refused the instructions, because its brief forbade changing the repository, and reported them. The coordinator then resent the corrections to the right agent.

## Impact

No file was damaged. The intended agent worked for a while without its corrections.

## Timeline

| When       | What                                                                                    |
| ---------- | --------------------------------------------------------------------------------------- |
| 2026-11-27 | Two identifiers swapped; corrections reached the spike agent, which refused them.       |
| 2026-11-27 | The same swap happened again; the spike agent refused again and the coordinator resent. |

## How did we do

Went well: the receiving agent refused an instruction outside its brief. Did not go well: the coordinator did not check the recipient before sending, twice.

## Guards

- rule, `agents/coordinator.md`: work is addressed by task, never by a hand-kept identifier; the recipient's role is checked before sending.
- rule, `agents/implementer.md`: an agent that receives an instruction outside its brief, or one that asks it to change paths it does not own, refuses and reports it. Every role file carries the same rule.
- scenario `S-1` of `docs/evaluation/scenarios.md`: the behaviour evaluation, once it exists, replays the swap.

The status is mitigated and cannot be more: an error of judgement is not made impossible by a rule, and the scenario is specified and not run (R88 is pending).
