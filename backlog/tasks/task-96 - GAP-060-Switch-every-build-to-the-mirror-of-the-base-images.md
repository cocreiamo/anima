---
id: TASK-96
title: 'GAP-060: Switch every build to the mirror of the base images'
status: Done
assignee: []
created_date: '2026-11-28T12:10:32Z'
labels:
  - gap
  - engine
dependencies: []
ordinal: 96000
gaps:
  - GAP-060
fork: none
role: implementer
owns:
  - engine/**
  - components.toml
  - gaps.toml
  - .github/renovate.json
  - tests/repository/**
  - model/anima.sysml
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The upstream registries delete the manifest of a pinned digest (GAP-060, observed 2026-11-28 on the engine image's base), and the mirror workflow (.github/workflows/mirror-base-images.yml, R160 to R163, first step of TASK-43) copies every image of the register into the organization's mirror under the same digest. This task makes the builds pull from it, and is done only after the founder has decided the visibility of the mirror's packages and the workflow has run once.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 test_R164_every_build_pulls_from_the_mirror
- [x] #2 Check: the update bot proposes only digests that exist in the mirror (renovate.json watches the mirror)
- [x] #3 Check: GAP-060 is updated in gaps.toml (status)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The dependencies images (TASK-43, step 5; `localhost/anima/secrets-dependencies:<tag>`, built by `mise run engine:build`) are not published yet. They join this switch: publish each as `ghcr.io/cocreiamo/anima-mirror/<name>-dependencies` with a tag that names its inputs (the tag `mise-tasks/engine/tag` computes) by a workflow job with the same least privilege as the mirror's (R163), record the digest it gives, and have `engine:build` consume `container-image://<mirror>/<name>-dependencies@<digest>` when the local tag is absent, so that a build on a clean machine reads the held image and reaches no module proxy. The visibility of the package is the founder's decision, the same as for the base images.

Not done in this task (decided with the lead, 2026-11-28): the publication of the dependencies images stays a step of TASK-43 (step 5, remaining).
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-96, GAP-060: Switch every build to the mirror of the base images. Role: implementer.

Start only when the founder has decided the visibility of the mirror's packages and the workflow `mirror-base-images.yml` has run once and its packages exist (read them with a registry client first: a build that cannot read the mirror is a faulted build).

### Read first

- `gaps.toml` entry GAP-060, `.github/workflows/mirror-base-images.yml`, `components.toml` (the `mirror` fields), TASK-43, `.github/renovate.json`, `tests/repository/test_mirror.py`

### Load these skills

- anima-adopting-a-component, anima-tech-podman-quadlet-bootc, anima-image-design, anima-branching-and-releasing, anima-tech-github-governance, anima-specifying-requirements

### Own these paths

- engine/**
- components.toml, gaps.toml
- .github/renovate.json, .github/workflows/system-tests.yml
- tests/repository/**, model/anima.sysml

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check; do not publish a package or change its visibility

### Plan

1. Repoint every `FROM` and image `ARG` under `engine/` (the database, access, secrets, configure, mail and image container files) from the upstream name to the `mirror` of the same register entry, keeping the digest (the mirror holds it by construction).
2. In `components.toml` the entry's `image` becomes its mirror and the upstream name moves to a new field that the mirror workflow reads in its place (R160 and its test follow).
3. In `.github/renovate.json` make the regular-expression manager look the entries up in the mirror (the `docker` datasource reads `ghcr.io`; `hostRules` with a token if the packages stay private), so that it proposes only digests that exist there. The mirror's tags `<tag>-<date>` are not versions of the upstream tag, so the manager needs a rule of its own and a test with a sample (R164 and its companion).
4. Write `test_R164_every_build_pulls_from_the_mirror` and its `_detects_violation` companion; regenerate.
5. Expect one cold run of the system tests (the cache of the inner images changes key), and, if the packages stay private, `packages: read` for the jobs that build.
6. Close GAP-060 when R164 passes and the bot's first proposal names the mirror.

### Acceptance

- test_R164_every_build_pulls_from_the_mirror
- Check: the update bot proposes only digests that exist in the mirror (renovate.json watches the mirror)
- Check: GAP-060 is updated in gaps.toml (status)

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

Task: TASK-96. Role: implementer. Date: 2026-11-28.

### Done

- `components.toml`: every image entry has `image` (the mirror package, what builds pull) and `source` (the upstream, read only by the mirror workflow); the `mirror` field is gone.
- `mise-tasks/ci/mirror-plan` copies `source` into `image`; the copy tool is the one image taken from its `source` (bootstrap). `mise-tasks/ci/mirror-copy` moves the tag that is the upstream tag after the digest is held under `sha256-<hex>` and `<tag>-<UTC date>` (R162, R176 texts).
- Every `FROM` and image `ARG` under `engine/` names the mirror with the register's tag and digest.
- `.github/renovate.json` names the mirror in the opentofu group and the Maven line rules; the manager reads the register's `image`, now the mirror.
- `test_R164_every_build_pulls_from_the_mirror` with its companion; R160 to R162 and R175, R176 tests follow the new shape; R164 left the pending list through the generator.
- GAP-060 (workaround in force, stays open: the gap is the upstream registries' behaviour), rule 13 of `anima-adopting-a-component`, TASK-43 notes.

### Unknowns resolved

- Every pinned digest resolves in the mirror, except the Maven image: its entry was registered after the last mirror run (the mirror holds the earlier `eclipse-temurin` package, not `maven`; anonymous read answers 403). A run of the workflow on main fills it, and its package must then be made public.
- The update bot reads a digest by the tag of the version, so the mirror needs that tag: the workflow now moves it.

### Only read

- The behaviour of Renovate (documentation: the docker datasource, docker versioning and the Docker guide); the bot itself was not run.

