---
id: TASK-43
title: Make the builds of the inner images reproducible
status: To Do
assignee: []
created_date: '2026-11-27T18:18:43Z'
updated_date: '2026-11-28T12:11:41Z'
labels:
  - engine
  - build
dependencies: []
ordinal: 43000
fork: none
role: implementer
gaps: []
owns:
  - engine/**
  - mise-tasks/engine/**
  - tests/system/**
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The database server's image installs distribution packages at build time with no snapshot pin, and the identity provider's build downloads from the Java and JavaScript package registries. The same pinned sources do not produce the same image bit for bit, so building again cannot check what was promoted. This is a defect of our own builds, not of something adopted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 test_R47_builds_reproducible
- [ ] #2 Check: distribution packages are taken from a dated snapshot and build-time downloads are pinned or vendored
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The ladder this task climbs, from what a release is today to what R47 asks:

- L0, published by digest: the released image is identified by its digest (R115). Reached.
- L1, rebuildable from pinned inputs that we hold: a build from scratch of the same commit finds every input it pins, because we hold it. Not reached: the upstream registries delete the manifest of a pinned digest (GAP-060, observed 2026-11-28), and the build downloads packages and archives that nobody here keeps.
- L2, rebuildable offline: every input is in the repository, in the mirror or in a cache that the build is given, and the build reaches no network.
- L3, bit for bit: two builds of the same commit give the same image (R47, test_R47_builds_reproducible).

Steps, in order. Each is its own change; this task stays open until L3.

1. Mirror the base images: the workflow that copies every image of the register into the organization's mirror, with the digest preserved (R160 to R163, GAP-060). Done by the change that introduced it; it has not run yet and its packages are not published.
2. Switch the builds to the mirror (TASK-96, R164): the container files, the register and the update bot point to it. Needs the founder's decision on the visibility of the mirror's packages and one run of the workflow.
3. Distribute the identity provider from a builder image that we pin, instead of the wrapper's download with bounded retries. Done (PM-015, R168, R169): the builder is the pinned Maven image, `mvn` replaces the wrapper, the resolver's retry settings bound the dependency downloads. What remains of the identity provider's build is step 5: the dependency graph, Node, pnpm and npm packages are still fetched at build time.
4. Take the distribution packages of every inner image from a dated snapshot of the distribution's archive (snapshot pins), instead of whatever the archive serves that day.
5. Offline dependency caches: the Java, JavaScript and Go dependencies of the builds are fetched once, by hash, into a cache we hold, and the builds read only it.

   Decided 2026-11-28 (class: a build that depends on inputs the repository does not hold): every component that Anima compiles gets its dependencies from a dependencies image fetched once per pinned fork commit, and its compile stage runs with the network off (R178, R179; rule 22 of `anima-tech-podman-quadlet-bootc`). Shape chosen: a separate image built by its own command (stage `dependencies` of the container file, built as `localhost/anima/<name>-dependencies:<tag>`, tag from the fork's commit, its lock files and the container file) and passed to the build as a named context, so that the system tests' image cache holds it. Done for the Go component of the secret store (engine/secrets): L2 for its compile stage. The only other Go-free builds under engine/ are not converted: the database server and its adapters are C builds (meson, make) whose compile stages install distribution packages (apt) and are step 4; the configurator fetches its providers by `tofu providers mirror` in a stage of its own (a download of release artefacts by hash, to convert in the same way); the mail catcher is not built. Remaining: the identity provider (Maven, Node, pnpm; pull request 42), the distribution packages of every stage (step 4), the providers of the configurator, publishing the dependencies image to the organization's registry and consuming it by digest (TASK-96), then L3.
6. L3: build twice, compare, remove what differs (timestamps, ordering, build identifiers), and write test_R47_builds_reproducible.
<!-- SECTION:NOTES:END -->

## Brief

Task: TASK-43, Make the builds of the inner images reproducible. Role: implementer.

### Read first

- The container files under `engine/`, `components.toml` and `anima-branching-and-releasing` rule 6.

### Load these skills

- anima-tech-podman-quadlet-bootc, anima-image-design, anima-branching-and-releasing, anima-specifying-requirements

### Own these paths

- engine/**
- mise-tasks/engine/**
- tests/system/**

### Do not touch

- third_party/**, generated files, lock files; do not weaken a check

### Acceptance

- test_R47_builds_reproducible
- Check: distribution packages are taken from a dated snapshot and build-time downloads are pinned or vendored

### Done when

- The review checklist (`docs/work/review-checklist.md`) passes.
- The report (`docs/work/handback-template.md`) is filled in.

## Report

(`docs/work/handback-template.md`, when done)
