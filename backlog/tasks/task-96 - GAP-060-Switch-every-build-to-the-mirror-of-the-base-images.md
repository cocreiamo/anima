---
id: TASK-96
title: 'GAP-060: Switch every build to the mirror of the base images'
status: To Do
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
- [ ] #1 test_R164_every_build_pulls_from_the_mirror
- [ ] #2 Check: the update bot proposes only digests that exist in the mirror (renovate.json watches the mirror)
- [ ] #3 Check: GAP-060 is updated in gaps.toml (status)
<!-- AC:END -->

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

(`docs/work/handback-template.md`, when done)
