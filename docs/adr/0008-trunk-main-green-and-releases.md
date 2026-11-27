---
number: 8
title: Trunk-based development, `main-green` and releases
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# Trunk-based development, `main-green` and releases

## Context and Problem Statement

Anima must be releasable at any time without a release being a risky event.
Some suites are too long to run on every pull request, so "passed the pull
request checks" and "fit to release" are two different facts and need two
different names.

How is Anima kept releasable at any time, given that some suites are too long for every pull request and "passed the pull request checks" and "fit to release" are different facts?

## Decision Drivers

- Anima must be releasable at any time without a release being a risky
  event.
- Some suites are too long to run on every pull request.

## Considered Options

- Trunk-based development with a `main-green` pointer and two tiers of
  verification

No alternative was recorded when this decision was taken, so the chosen option is the only one listed.

## Decision Outcome

Chosen option: "Trunk-based development with a `main-green` pointer and two tiers of verification", as the only option recorded; it gives the two facts two names.

1. **One trunk.** `main` is the only long-lived development branch. Work
   happens on short-lived branches and reaches `main` through a pull request,
   squashed. There are no release branches until a fix must be backported; a
   backport branch then starts from a released tag.
2. **`main-green`** is a pointer to the newest commit of `main` that passed
   every suite. Nobody commits to it. The rule is that only the Promote
   workflow moves it, and only forward. The ruleset cannot enforce that rule
   yet: it forbids force pushes and deletion but cannot restrict who pushes
   (GAP-008).
3. **Two tiers of verification.**
   - Pull request: the fast checks, `mise run check`.
   - Promotion: everything, `mise run promote:verify`, including the suites
     too long for a pull request. It runs nightly and on demand.
4. **Releases come only from `main-green`.** The version and the changelog are
   prepared on `main` by the `release-please` pull request (the Prepare
   release workflow, `prepare-release.yml`). The tag and the GitHub release
   are created by the Promote workflow when the commit that carries the
   version is promoted.
5. **Build once, promote the artifact.** The images published for a release
   are the ones built and verified in the promotion run, identified by
   digest. Nothing is rebuilt to be released, and a release build restores no
   cache.
6. **Environments run released versions only.** Staging and production are
   given a version and its digests, never a branch or a commit.
7. **Versions follow Semantic Versioning 2.0.0.** Before 1.0.0 a breaking
   change raises the minor number and anything else the patch number. A
   published tag is never moved or reused.
8. **When `main` breaks, revert first.** The offending change is reverted and
   comes back through a new pull request.

### Consequences

- Neutral, because a change can be released one promotion after it lands,
  not at once.
- Good, because `main` may briefly hold a commit that fails a long suite;
  `main-green` never does, and that is the only branch releases and
  environments see.
- Bad, because `main-green` needs its own ruleset: no force push, no
  deletion, signed commits. It cannot yet be restricted to the Promote
  workflow (GAP-008).
- Neutral, because a failed promotion blocks every later release until
  `main` is fixed or reverted, which is the intended pressure.

### Confirmation

Built: the pull request tier is `mise run check` in `.github/workflows/ci.yml`, and `mise run promote:verify` runs the same checks until the long suites join it. R24, `test_R24_release_only_from_verified_commit`, is pending and not written. That only the Promote workflow moves `main-green` cannot be enforced by the ruleset (GAP-008).

## Pros and Cons of the Options

Only the chosen option was recorded, so there is no rejected alternative to weigh.
