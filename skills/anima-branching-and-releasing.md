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
4. **Two tiers of verification.** Pull request: the fast checks, `mise run check`. Promotion: everything, `mise run promote:verify`, including the suites too long for a pull request; it runs nightly and on demand. Until the long suites join it, `promote:verify` runs the same checks.
5. **Releases come only from `main-green`** (R24). The version and the changelog are prepared on `main` by the `release-please` pull request (`prepare-release.yml`); the tag and the GitHub release are created by the Promote workflow (`promote.yml`) when the commit that carries the version is promoted. Not: a workflow named Release that only prepared a version (it became Prepare release).
6. **Build once, promote the artifact.** The images published for a release are the ones built and verified in the promotion run, identified by digest; nothing is rebuilt to be released, and a release build restores no cache. The same pinned sources must also produce the same image, bit for bit, so that building again checks what was promoted (R47).
7. **Environments run released versions only.** Staging and production are given a version and its digests, never a branch or a commit.
8. **Versions follow Semantic Versioning 2.0.0.** Before 1.0.0 a breaking change raises the minor number and anything else the patch number. A published tag is never moved or reused.
9. **When `main` breaks, revert first.** The offending change is reverted and comes back through a new pull request. A failed promotion blocks every later release until `main` is fixed or reverted, which is the intended pressure.
10. **A workflow is pinned and least-privileged:** actions by commit SHA, minimal `permissions`, no untrusted input in a shell, `zizmor` clean. A workflow that provides a required check also runs in the merge queue.
11. **Only the founder commits, pushes or changes a repository setting** (`anima-repository-conventions`). A setting that cannot be a file is a founder task in the backlog.
12. Unverified: **the long suites and the release path.** The promotion runs the same checks as a pull request until the long suites exist; the verification of a release only from a verified commit is pending (R24); the image publish workflow is not written.
13. Unverified: **that the ruleset is applied on GitHub.** The rulesets are files in `.github/rulesets/`; their being applied is a GitHub setting that no test of this repository verifies.

## Questions to answer before proposing

- Does the change reach `main` through a pull request with a Conventional Commits title?
- Is the check fast enough for a pull request, or does it belong to the promotion?
- Does anything rebuild an image that was promoted, or run a branch in an environment?
- Is the version number consistent with Semantic Versioning before 1.0.0?

## Where the result goes

Workflows and rulesets go to `.github/`; the tasks to `mise.toml` (`promote:verify`); a platform limit to `gaps.toml` (GAP-008). Related skills: `anima-repository-conventions`, `anima-tech-github-governance`, `anima-designing-for-production`.
