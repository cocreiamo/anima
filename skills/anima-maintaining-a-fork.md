---
name: anima-maintaining-a-fork
description: "Use when touching anything under third_party/, moving a pin, adding a fork as a submodule, syncing a fork with upstream, or preparing a contribution upstream: mirror branches, the anima/<line> branch, merging and never rebasing, the sync workflow."
family: product
paths:
  - third_party/**
  - .gitmodules
  - .github/workflows/sync-forks.yml
  - components.toml
---

# Maintaining a fork

How the forks follow upstream and carry our changes, so that Anima can change
the database server, the identity provider and the other forked components and
contribute the changes upstream. What a technology does is its technology
skill; what to adopt is `anima-adopting-a-component`.

## Use this when

- Adding a fork as a submodule, or moving the pin of one.
- Changing a file under `third_party/`, or writing a patch for upstream.
- Following a new upstream release, or touching the sync workflow.
- Deciding whether a fork's own test suite runs.

## Rules

1. **A component built from source is a real fork in its own repository,** named `anima-<name>` in the organization and added to `anima` as a git submodule under `third_party/<name>`; a commit of `anima` pins the exact commit of each, and one pipeline builds everything from source. `components.toml` lists every shipped component with its version, its commit or digest and its SPDX licence, and a test checks that every submodule is a declared component under `third_party/` (R11), except `shared`, the organization's shared repository, which is a submodule at `shared/` and not a component or a fork. Not: an edit of a fork in place from `anima`; a change is written for upstream first.
2. **Every tool that skips the forks skips the one directory `third_party`.** Bazel (`.bazelignore`), Prettier, `typos`, `ruff` and the formatter of TOML files (its include list names only our own files) all skip it; a formatter once rewrote a file of a fork (PM-002, R89). Each fork keeps its upstream's own tools and format.
3. **Upstream branches are mirrors.** In a fork the branches that exist upstream are never committed to; a scheduled workflow in `anima` fast-forwards them with `gh repo sync` (`.github/workflows/sync-forks.yml`). The workflow writes with an installation token of the organization's `cocreiamo-fork-sync` App (organization variable `FORK_SYNC_APP_ID`, secret `FORK_SYNC_APP_PRIVATE_KEY`), made for the one fork of each job (R195); the App is installed on the `anima-*` forks. A new fork is added to the matrix with its `repository` name, and the App must be installed on it by the platform team. A fork of a component that is taken as a package and not built from source (a mirror for upstream contributions, like `anima-yarp`) is synced the same way and has no submodule.
4. **Our changes live on one branch per upstream line,** named `anima/<line>` (for example `anima/18` on top of the stable branch of that line), created from the release in use on the day of the first change. Until then the submodule pins an upstream release commit. A fork then differs from upstream only by the commits on that branch, so `git log upstream..anima/<line>` is the full list of our changes.
5. **A new upstream release enters by merge,** its tag merged into `anima/<line>`. The branch is never rebased, so a commit pinned by `anima` never disappears. The price is that a patch for upstream is prepared on its own topic branch, not cut from ours. Not: rebasing a fork; "do not fork until there is a patch".
6. **A change meant for upstream is written for upstream first,** on a topic branch from upstream's development branch, formatted with upstream's own tools, in upstream's licence, and submitted the way upstream asks (the mailing list for the database server, a pull request for the other forks). It is then merged into `anima/<line>`. Changes in a fork keep the upstream licence (`anima-licensing-and-brand`).
7. **Adopting a new fork commit is deliberate:** a pull request in `anima` that moves the submodule and the matching entry of `components.toml` and passes every check. Not: Renovate moving a submodule. A fork not yet a submodule is pinned in `components.toml` by the commit of its release, looked up with `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha`, and fetched and built from that commit, never by a floating reference.
8. **A fork runs no workflow of its own.** Changes to a fork are verified by the `anima` pipeline; upstream's workflows are not to run in the forks (rule 11).
9. **Run a fork's test suite only while the fork carries changes of ours,** and then only for the parts changed. The regression suite of the database server's fork always runs: it is quick and the database server is the heart of the product. A fork that carries no change of ours, the identity provider's, does not run its suite.
10. **Follow the upstream project's own instructions for agents** when working inside a fork, if it ships any (`AGENTS.md` or similar in that fork); the sources of truth for an adopted technology are its technology skill and its pinned source and documentation under `third_party/`, never memory.
11. Unverified: **that GitHub Actions are disabled in the forks, the branch rules and the sync workflow.** Disabling Actions is a setting of each fork that no test verifies; mirrors, merge and never rebase and one branch per line are not checked automatically, and no test verifies the scheduled workflow; no `anima/<line>` branch exists yet because no patch does.

## Questions to answer before proposing

- Is the change written for upstream first, and in upstream's licence and tools?
- Does the pin in `components.toml` equal the submodule's commit?
- Is the fork merged, never rebased, and are upstream's branches untouched?
- Does the fork's suite need to run, given what we changed in it?

## Where the result goes

The pin and the licence go to `components.toml`; the sync list to `.github/workflows/sync-forks.yml`; a limit found in a fork to `gaps.toml`, with a backlog task labelled `upstream` that names the fork. Related skills: `anima-adopting-a-component`, `anima-licensing-and-brand`, `anima-tech-github-governance`.
