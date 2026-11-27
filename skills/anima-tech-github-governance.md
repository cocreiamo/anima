---
name: anima-tech-github-governance
description: "Use when creating or changing rulesets, required status checks, the merge queue, GitHub Actions permissions, forks of upstream projects or workflows that commit or push in Anima's GitHub organization: what the platform accepts and refuses."
family: technology
paths:
  - .github/**
---

# GitHub governance

How GitHub rulesets, Actions permissions and forks behave when set up through
the command line and the REST API. The repository rules are in
`anima-repository-conventions`.

## Use this when

- Creating or updating a ruleset, or choosing who may bypass it.
- Adding a required status check, or a workflow that provides one.
- Letting a workflow open or approve pull requests.
- Forking an upstream project and adding it as a submodule.
- Writing a workflow that commits, pushes or moves a branch.

## Rules

1. **Create and update a ruleset through the REST API from a JSON file.** Observed on 2026-11-27 on github.com. Example: `.github/rulesets/main.json` and `.github/rulesets/main-green.json` are the source. Not: a settings page.
2. **Give every workflow that provides a required check the `merge_group` trigger, and let a job with nothing to do succeed.** Example: `on: … merge_group:` in `ci.yml` and `pull-request.yml`. Not: expecting a check that reports on a pull request to report in the merge queue.
3. **Do not plan on the GitHub Actions app as a bypass actor.** Not: expecting it to be one of a repository ruleset; it cannot ("must be part of the ruleset source or owner organization"), so a branch cannot be restricted to one workflow (GAP-008).
4. **Fork with the command line and update with `gh repo sync`.** Example: `.github/workflows/sync-forks.yml`. Not: expecting a fork to be small, because it copies all branches and tags; or workflows to run in it, because they are disabled by default.
5. **Fetch the release tag explicitly in a shallow submodule clone.** Not: expecting the tag to be there; it fetches only the default branch.
6. **Move a branch with a commit made through the API.** A commit made through the API by a workflow is signed by GitHub, which satisfies a signed-commits rule; Example: `promote.yml` moves a branch with `gh api --method PATCH` on `git/refs/heads/<branch>`.
7. **Let the organization allow "create and approve pull requests" before the repository does.** Not: enabling it on the repository alone; the call fails with 409 (GAP-046).
8. Unverified: which credential a chained workflow should use. A push made with the workflow token does not start other workflows, and no replacement has been tried.

## Questions to answer before proposing

- Who may bypass the ruleset, and can the platform express it?
- Does every workflow that provides a required check run in the merge queue?
- Does the change need an organization setting that only the founder may change?
- Does a workflow push, and which credential does it use?

## Where the result goes

Settings go to `.github/` as files (rulesets, workflows); a setting that cannot be a file is the founder's to-do in the backlog. Decisions amend `anima-repository-conventions` and `anima-maintaining-a-fork` or `anima-branching-and-releasing`. Limits go to `gaps.toml` (GAP-008, GAP-046). Related skills: `anima-repository-conventions`, `anima-adopting-a-component`.
