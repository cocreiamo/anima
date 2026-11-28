---
name: anima-repository-conventions
description: "Use when adding or moving files in the anima repository, or changing mise tasks, git hooks, formatting, linting, REUSE annotations, caches or commit authorship: layout, toolchain and generated files."
family: product
paths:
  - CONTRIBUTING.md
  - .editorconfig
  - .gitignore
  - .prettierignore
  - .devcontainer/**
  - REUSE.toml
  - MODULE.bazel
  - BUILD.bazel
---

# Repository conventions

How files, tasks and checks are organised in the `anima` repository; decision
records are `anima-writing-a-decision-record`. Branching and releases are `anima-branching-and-releasing`; forks
are `anima-maintaining-a-fork`; what an agent loads and how it works is
`anima-working-as-an-agent`.

## Use this when

- Adding or moving files, or choosing where something lives.
- Changing mise tasks, hooks, formatting, linting or caches.
- Preparing a commit.

## Rules

1. **`mise run <task>` is the only entry point,** locally and in CI. Tools come from `mise.toml` (exact versions, `mise.lock` with checksums) and nowhere on the host. Example: `mise run check` runs `model:check`, `generate:check`, `adr:check`, `licenses:check`, `secrets:check`, `workflows:check`, `lint`, `build`, `test`. Not: a workflow step that calls a tool directly, or a wrapper action that downloads a tool.
2. **A script task is a mise file task** in `mise-tasks/` (`model:check`, `model:export`, `generate`). Not: a `tools/` or `scripts/` directory.
3. **Hooks are generated,** by `mise generate git-pre-commit` through `mise run hooks:install`: `pre-commit` (fast checks), `commit-msg` (`committed`), `pre-push` (every check). Not: a hand-written hook.
4. **Generated files are generated, never edited by hand.** `mise run generate` writes them, `mise run generate:check` (part of `check`) fails when one is stale, and `mise run format` generates first (R38). Each says so; `mise run generate:list` prints those the agent may not edit. Commit them with the change that made them stale. To add one, add its generator to `mise-tasks/generate/generators.py`. Not: an index kept by hand. **A committed generated file must let two branches add to it without conflict** (R150, PM-011): GitHub's merge and the merge queue run no custom merge driver and `merge=union` is not relied on, so a conflict costs a merge, a regeneration, a full check and a CI round. Not: a list sorted by id (new items take the next id and all land at the end), a total or a count of the whole, a "last" marker; sort by a key that spreads (the name), one entry per line, and leave a sum out. A file that cannot be made so is not committed.
5. **One ignored directory, `.cache/`.** Everything generated or cached goes there (the virtual environment, bytecode, caches); Python runs only through `mise`, which sets the cache prefix (PM-004, R91). Not: a new ignored directory; a `__pycache__` beside the source.
6. **Each top-level directory has one purpose,** organized by capability and never by product: `model/` (the requirements, `anima.sysml`), `docs/adr/` (decisions of architecture), `skills/`, `agents/`, `backlog/`, `engine/<capability>/` (the runtime Anima ships: `database`, `access`, `secrets`, `backup`, `vectors`, `image`, `configure`, `mail`), `config/<capability>/` (an instance's configuration, here the example one, which tests and local development use; the capability names mirror `engine/`), `tests/repository/` and `tests/system/`, `third_party/` (the forks), `mise-tasks/`, `.github/` and `.devcontainer/`. The registers `components.toml`, `gaps.toml`, `contractions.toml`, `waves.toml` and `resources.toml` sit at the root beside `mise.toml`.
7. **Each kind of source is built by the tool made for it.** Anima's own code with Bazel (`bazelisk`, `.bazelversion`, `MODULE.bazel` and its lock file; `third_party` excluded in `.bazelignore`); a fork with its upstream build; images from container files with `buildah` or `podman build`, which copy in what the two builds produce, for amd64 and arm64. The database server's image starts from the official `docker-library/postgres` container file pointed at the fork's source; the identity provider's image is built with upstream's own build; the engine image is built from the Fedora bootc base and disk images from it by `bootc-image-builder` (`anima-image-design`). Not: `rules_oci` and `rules_foreign_cc`, which would replace the upstream container files and builds.
8. **Formatting and linting tools, by what they cover:** `ruff` (Python), `shellcheck` (shell), `actionlint` and `zizmor` (workflows), `buildifier` (Bazel), Prettier (Markdown, YAML, JSON), `taplo` (TOML), `typos` (spelling), `.editorconfig`; a fork uses its upstream's tools. `mise run format` formats; `mise run lint` checks.
9. **REUSE for every file** (R18): `REUSE.toml` has a catch-all annotation and an `override` for each adopted text, naming the upstream authors and licence (`anima-licensing-and-brand`). An adopted text is adopted verbatim or says what was changed, and a text adopted or signed as it is is listed in `.prettierignore`.
10. **Commits are signed and made with the founder's approval.** Every commit is reviewed by the founder and signed with the founder's GPG key (fingerprint `4898A14E659F7175D2EDCE7F9B54A8DF5D99575C`); a commit made with AI assistance keeps the `Co-Authored-By` trailer naming the assistant, so that the history shows which changes had assistance; an unsigned commit on `main` is a defect. The ruleset in `.github/rulesets/main.json` contains `required_signatures`.
11. **Never commit or push without the founder's explicit approval,** and never change a repository setting (rulesets, apps, secrets) without it. Not: an agent committing because the work is done.
12. **Names in the repository are functional and unbranded:** no product prefix on roles, scopes or files, and no directory named after a product: `engine/access/`, not `engine/keycloak/` (R54). A prefix states the kind, not the brand (`svc_` for service roles).
13. **A workaround names its `GAP-nnn` in a comment,** and `tests/repository/test_repository.py` checks that every id used is registered (R25).
14. **No Docker.** Container work in development, tests, CI and documentation uses podman, daemonless and rootless; `test_R11_every_dependency_pinned` fails if `mise.toml`, `mise-tasks/`, `.github/workflows/` or `tests/` invoke a `docker` command. Docker is named only in `third_party/`, in records and skills where it is a rejected tool, and in the names of third-party actions and upstream files (`docker/metadata-action`, `docker-library/postgres`). The development container, `.devcontainer/devcontainer.json`, is the official base image plus the mise feature, both pinned by digest, and `mise install` installs every tool; it is not the output of `mise generate devcontainer`. It is Debian-family and is to be replaced by one in the family of the engine (GAP-021).
15. **CI caches:** `mise-action` caches the tools and the Pilot Implementation is kept with `actions/cache` keyed on its checksum; both are in use. A release build restores no cache (`anima-branching-and-releasing`).
16. Unverified: **that the founder's approval and the `Co-Authored-By` trailer are applied.** Neither is checked automatically, and that the rulesets are applied on GitHub is a setting no test of this repository verifies.
17. Unverified: **the caches that are adopted and not in use.** The image layer cache (the registry as layer cache for `buildah`) and the Bazel cache (`bazel-contrib/setup-bazel`, a remote cache later) are not configured.

## Questions to answer before proposing

- Which task runs this, locally and in CI, with the same command?
- Does the change add an ignored directory, a script or a tool outside mise?
- Can the new file be derived from another? Then generate it.
- Does every new file carry copyright and licence information (`mise run licenses:check`)?
- Does the change need a repository setting? Then ask the founder; do not apply it.

## Where the result goes

Layout and toolchain rules stay here; tools to `mise.toml`; tasks to `mise.toml` or `mise-tasks/`; the adopted tools and the ones dropped to `anima-adopting-a-component`; user-facing rules for contributors to `CONTRIBUTING.md`. Related skills: `anima-tech-mise`, `anima-writing-a-decision-record`, `anima-working-as-an-agent`.
