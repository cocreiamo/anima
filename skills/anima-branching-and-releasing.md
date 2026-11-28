---
name: anima-branching-and-releasing
description: "Use when opening or merging a pull request, changing CI or the promotion workflow, moving main-green, preparing or publishing a release, or choosing a version number: trunk-based development, the two tiers of verification, build once and promote, Semantic Versioning."
family: product
paths:
  - .github/workflows/**
  - .github/rulesets/**
  - .github/release-please-config.json
  - .github/release-please-manifest.json
---

# Branching and releasing

How Anima is kept releasable at any time, given that some suites are too long
for every pull request and "passed the pull request checks" and "fit to
release" are different facts that need different names. How GitHub accepts the
settings is `anima-tech-github-governance`.

## Use this when

- Opening, titling or merging a pull request.
- Changing a workflow, the ruleset or the promotion.
- Moving `main-green`, preparing a release or choosing a version.
- Deciding what an environment may run.

## Rules

1. **One trunk.** `main` is the only long-lived development branch. Work happens on short-lived branches and reaches `main` through a pull request, squashed, through the merge queue; no direct push, no force push, no deletion of `main`. There are no release branches until a fix must be backported; a backport branch then starts from a released tag.
2. **Titles and commits follow Conventional Commits,** checked by `committed` on commits and by `amannn/action-semantic-pull-request` on titles; releases and the changelog are generated from them. Example: `feat: accept tokens from a second issuer`.
3. **`main-green` points to the newest commit of `main` that passed every suite.** Nobody commits to it; only the Promote workflow moves it, and only forward. The ruleset cannot enforce that yet: it forbids force pushes and deletion but cannot restrict who pushes (GAP-008).
4. **Two tiers of verification.** Pull request: the fast checks, `mise run check`. Promotion: everything, `mise run promote:verify`, including the suites too long for a pull request; it runs nightly and on demand. The engine's system tests (`mise run engine:test`) are in both: on a pull request and in the merge queue as the check `System tests` (`system-tests.yml`), which reports on every change and runs only when the change touches the engine, its configuration, its pinned sources or its tests (R114); in the promotion on the commit being promoted, with the engine image built cold (R24).
5. **Releases come only from `main-green`** (R24). The version and the changelog are prepared on `main` by the `release-please` pull request (`prepare-release.yml`); the tag and the GitHub release are created by the Promote workflow (`promote.yml`) when the commit that carries the version is promoted. Not: a workflow named Release that only prepared a version (it became Prepare release).
6. **Build once, promote the artifact.** The images published for a release are the ones built and verified in the promotion run, identified by digest; nothing is rebuilt to be released, and a release build restores no cache. The Promote workflow archives the image that passed the system tests, a separate job that holds `packages: write` loads it, checks its id against the one that passed and pushes it to `ghcr.io/cocreiamo/anima` under the version, recording the digest that the release notes state; a tag that exists is never moved: the release then points at the digest it already holds and its notes say so (an interrupted release is finished, not repeated), and `latest` is never written (R115). The same pinned sources must also produce the same image, bit for bit, so that building again checks what was promoted (R47).
7. **Environments run released versions only.** Staging and production are given a version and its digests, never a branch or a commit.
8. **Versions follow Semantic Versioning 2.0.0.** A published tag is never moved or reused. Until the founder decides otherwise the first release is 0.0.1 and every release stays in 0.0.\*: only the patch number is raised, whatever the commit type, a breaking change included. The release configuration holds it durably: `initial-version` sets the first release (without it release-please proposes 1.0.0 when no release exists yet, whatever the manifest says) and the `always-bump-patch` versioning strategy sets every later one (R110); a one-shot `release-as` is not used.
9. **When `main` breaks, revert first.** The offending change is reverted and comes back through a new pull request. A failed promotion blocks every later release until `main` is fixed or reverted, which is the intended pressure.
10. **A workflow is pinned and least-privileged:** actions by commit SHA, minimal `permissions`, no untrusted input in a shell, `zizmor` clean. A workflow that provides a required check also runs in the merge queue.
11. **Only the founder commits, pushes or changes a repository setting** (`anima-repository-conventions`). A setting that cannot be a file is a founder task in the backlog.
12. **System tests run on GitHub-hosted runners, with a cache of the inner images on pull requests.** Observed on 2026-11-28 on a plain `ubuntu-24.04` runner with the rootless container runtime as installed, no privileged mode and no change to the runner: the system tests pass; a cold job took 23 to 40 minutes, the build of the identity provider dominating and varying, and 9.5 minutes with the six inner images restored from a cache made with `podman save --multi-image-archive` and `actions/cache`, keyed on the submodule status and on `engine/`, `mise-tasks/engine/` and `config/`. Not: caching the runtime's storage directory (it does not work), or the engine image itself (not worth it). Pushes to `main` save the cache; pull requests and the merge queue only restore it; the promotion restores none.
13. Unverified: **the release path.** The promotion's build, test and publish path (R24, R115) has been read, not run: the first run on `main` with a prepared version shows it, and so does that a pull request or the merge queue can read the cache saved from `main`, that the registry accepts the push, and that a release created with notes and generated notes carries both. The ARM image, the bill of materials and the attestation are not built (R16, R23).
14. Unverified: **that the ruleset is applied on GitHub.** The rulesets are files in `.github/rulesets/`; their being applied is a GitHub setting that no test of this repository verifies.

## Questions to answer before proposing

- Does the change reach `main` through a pull request with a Conventional Commits title?
- Is the check fast enough for a pull request, or does it belong to the promotion?
- Does anything rebuild an image that was promoted, or run a branch in an environment?
- Does the version stay in 0.0.\* (patch bump only) until the founder decides otherwise?

## Where the result goes

Workflows and rulesets go to `.github/`; the tasks to `mise.toml` (`promote:verify`); a platform limit to `gaps.toml` (GAP-008). Related skills: `anima-repository-conventions`, `anima-tech-github-governance`, `anima-designing-for-production`.
