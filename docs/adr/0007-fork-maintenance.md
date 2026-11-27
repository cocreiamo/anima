---
number: 7
title: How forks follow upstream and carry our changes
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# How forks follow upstream and carry our changes

## Context and Problem Statement

Anima builds PostgreSQL, Keycloak, `pg_oidc_validator`, `pgvector`,
`pgbackrest` and OpenBao from forks ([ADR-0006](0006-repository-and-toolchain.md)), each a submodule under
`third_party/`, so that it can change them and contribute the changes
upstream.
A fork that drifts from upstream, or whose history is rewritten, defeats both
aims. The rules are set before the first patch exists.

How do the forks follow upstream and carry our changes, so that Anima can change PostgreSQL, Keycloak and the other forked components and contribute the changes upstream?

## Decision Drivers

- Anima must be able to change the forked components and contribute the
  changes upstream.
- A fork that drifts from upstream, or whose history is rewritten, defeats
  both aims.

## Considered Options

- Mirror branches, one `anima/<line>` branch per upstream line, merge and
  never rebase

No alternative was recorded when this decision was taken, so the chosen option is the only one listed.

## Decision Outcome

Chosen option: "Mirror branches, one `anima/<line>` branch per upstream line, merge and never rebase", because a fork then differs from upstream only by the commits on that branch and a pinned commit never disappears.

1. **Upstream branches are mirrors.** In a fork, the branches that exist
   upstream are never committed to. A scheduled workflow in `anima`
   fast-forwards them with `gh repo sync`.
2. **Our changes live on one branch per upstream line**, named
   `anima/<line>`, for example `anima/18` on top of `REL_18_STABLE`. The
   branch is created from the release in use on the day of the first change.
   Until then the submodule pins an upstream release commit.
3. **A new upstream release enters by merge.** Its tag is merged into
   `anima/<line>`. The branch is never rebased, so a commit pinned by `anima`
   never disappears.
4. **A change meant for upstream is written for upstream first**: on a topic
   branch from upstream's development branch, formatted with upstream's own
   tools and submitted the way upstream asks (mailing list for PostgreSQL,
   pull request for the other forks). It is then merged into
   `anima/<line>`.
5. **Adopting a new fork commit is deliberate.** It is a pull request in
   `anima` that moves the submodule and the matching entry in
   `components.toml`, and it passes every check. Renovate does not move
   submodules.
6. **Forks run no workflows of their own.** GitHub Actions stay disabled in
   the forks, so upstream's workflows do not run there. Changes to a fork are
   verified by the `anima` pipeline.
7. Changes in a fork keep the upstream licence ([ADR-0002](0002-licensing-and-cla.md)).

### Consequences

- Good, because a fork differs from upstream only by the commits on
  `anima/<line>`, so `git log upstream..anima/<line>` is always the full
  list of our changes.
- Neutral, because merging instead of rebasing keeps pins valid; the price
  is that a patch for upstream is prepared on its own topic branch, not cut
  from our branch.
- Neutral, because the sync workflow needs a token that can write to the
  forks, stored as the secret `FORK_SYNC_TOKEN`.

### Confirmation

`test_R11_every_dependency_pinned` checks that each submodule is a declared component and that `components.toml` and the submodule pin the same commit. The branch rules (mirrors, merge and never rebase, one branch per line, no workflow in the forks) are not checked automatically. The scheduled workflow `.github/workflows/sync-forks.yml` exists; no test verifies it.

## Pros and Cons of the Options

Only the chosen option was recorded, so there is no rejected alternative to weigh.
