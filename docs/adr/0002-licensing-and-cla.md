---
number: 2
title: AGPL-3.0-only with dual licensing and a contributor agreement
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# AGPL-3.0-only with dual licensing and a contributor agreement

## Context and Problem Statement

Anima is meant to be fully open source and to be deployed by agencies for
their customers. The copyright holder, Cocreiamo di Bilotta Francesco (a sole
proprietorship, to be succeeded by a company), also needs a way to fund the
work and to serve those who cannot accept copyleft terms.

Which licence, and which contribution terms, let Anima stay fully open source while Cocreiamo can still sell other terms?

## Decision Drivers

- The claim of being fully open source, and the agency model.
- A way to fund the work: commercial terms for those who cannot accept
  copyleft.
- Contributions must not block relicensing, and must survive the passage
  from the sole proprietorship to a company.

## Considered Options

- AGPL-3.0-only, dual licensing, Apache ICLA 2.2 adapted, signed with CLA
  Assistant
- A source-available licence (FSL, BSL, Elastic License, SSPL, "internal use
  only" terms)
- The contributor-assistant GitHub Action to collect signatures
- A DCO sign-off alone, with no CLA

## Decision Outcome

Chosen option: "AGPL-3.0-only, dual licensing, Apache ICLA 2.2 adapted, signed with CLA Assistant", because it is the only option that is fully open source and still lets Cocreiamo license contributions under other terms.

1. Anima is licensed under the GNU Affero General Public License, version 3
   only ([LICENSE](../../LICENSE)).
2. Cocreiamo also offers commercial licenses to those who cannot meet the
   terms of the AGPL (dual licensing).
3. Public commitment: the core will always remain available under the AGPL.
4. Contributions are accepted only under the [CLA](../../CLA.md): the Apache
   Individual Contributor License Agreement 2.2, adapted. "The Foundation"
   becomes Cocreiamo, the signature form and the non-profit sentence are
   removed, and section 9 extends the agreement to successors and assigns.
5. A forked component keeps the licence of the original software, and so does
   every change made to it. Changes to `anima-postgres` are under the
   PostgreSQL License, so they can be contributed upstream as they are.
6. The CLA is signed on pull requests with CLA Assistant (cla-assistant.io),
   linked to the whole `cocreiamo` organization.
   - The agreement text it shows is a public Gist identical to `CLA.md`.
   - Allowlist: the founder, who is the copyright holder, and bots, which
     cannot sign and whose pull requests the founder reviews and merges.

### Consequences

- Good, because the CLA is what makes dual licensing possible: Cocreiamo can
  license contributions under terms other than the AGPL.
- Good, because section 9 lets the future company take over without
  contributors signing again. Code written by the founder personally passes
  to the company by a separate deed, not by the CLA.
- Bad, because when `CLA.md` changes, the Gist must change with it, and
  every contributor is asked to sign again.
- Bad, because CLA Assistant records the GitHub user name and signing date
  of each signer, so a privacy notice must be linked before the first
  outside contribution.
- Neutral, because "Every modification of the core is AGPL" applies to
  Anima's own code. It does not apply to forked components, which follow
  point 5.
- Neutral, because anyone may host Anima, subject to the AGPL duty to
  publish modifications. The commercial lever is the trademark, see [ADR-0004](0004-trademarks-and-names.md).

### Confirmation

Verified today: R17, `test_R17_component_licenses_allowed` (every shipped component declares an allowed SPDX licence) and R18, `test_R18_every_file_licensed` (`reuse lint`). Not verified by a test of this repository: the signature of the CLA on pull requests, which is a GitHub App setting (CLA Assistant), and the privacy notice for it.

## Pros and Cons of the Options

### A source-available licence (FSL, BSL, Elastic License, SSPL, "internal use only" terms)

- Bad, because it contradicts the claim of being fully open source.
- Bad, because it contradicts the agency model.

### The contributor-assistant GitHub Action to collect signatures

- Bad, because it is archived.

### A DCO sign-off alone, with no CLA

- Bad, because it grants no right to relicense, so dual licensing is impossible.

## More Information

- SECURITY.md, SPDX headers and a REUSE check in CI.
- Licence review of each adopted capability before it is adopted.

The founder confirmed on 2026-11-27 that `LicenseRef-Fedora-Distribution` is an
allowed licence for the base image of the engine, a distribution image whose
packages each carry their own licence (`components.toml`, [ADR-0011](0011-engine-image-and-runtime.md)).
