---
id: PM-014
date: 2026-11-28
title: The identity provider's build failed while downloading its build tool, and failed the first release
class: a build that depends on inputs the repository does not hold
status: guarded
guards:
  - kind: test
    ref: test_R167_build_downloads_no_build_tool
    added: 2026-11-28
recurrences: []
---

# PM-014: The identity provider's build failed while downloading its build tool, and failed the first release

## Overview

The build of the identity provider's image ran the source's Maven wrapper, which downloads Maven from the central repository once, with no retry and no checksum. The download failed three times on 2026-11-28; the last failure stopped the promotion run of the first release.

## What happened

The container file ran `./mvnw ... clean install`. The wrapper of the fork is of the type `only-script`: it fetches the Maven distribution with `wget` or `curl`, keeps it under the Maven user home and starts it. In CI nothing was cached, so every build began with that download, and the site answered with an error (`wget: Failed to fetch`). The build had no other source of Maven, so it stopped before compiling anything.

## Root cause

The build fetched its build tool from the network at build time, unverified and without a retry. Evidence: the wrapper's properties file (`distributionType=only-script`, no `distributionSha256Sum`) and its script, read in a spike, show one download with neither check nor retry; the failing line of three build logs is that download; the same build, run locally after the change, makes no such download. The builder image pinned the Java toolchain but not the build tool, so the pin looked complete when it was not.

## Class and earlier occurrences

The class is a build that depends on inputs the repository does not hold. Earlier occurrences, all on 2026-11-28 or before: a base image whose digest its registry deleted (GAP-060); the three failures of this download, one of them the promotion run 46146056321 of the first release. The other inputs of the same kind are still fetched at build time: the dependency graph, the Node, pnpm and npm packages, and the distribution's packages (TASK-43).

## Resolution

The builder is the official Maven image, pinned by digest and registered with the mirror like the other base images; the build calls `mvn`, which the image holds, and no longer calls the wrapper. The Maven version of the image is recorded in the register and must equal the version the fork's wrapper names. The dependency downloads that remain retry up to ten times through the resolver's own settings (R168).

## Impact

Three failed builds on 2026-11-28, one of them the promotion run of the first release; nothing was published from it.

## Timeline

| When       | What                                                                           |
| ---------- | ------------------------------------------------------------------------------ |
| 2026-11-28 | Two builds fail on the download of Maven.                                      |
| 2026-11-28 | The promotion run of the first release fails the same way.                     |
| 2026-11-28 | A spike finds the wrapper's behaviour; the builder is changed, a test written. |

## How did we do

Went well: the failing line was in the log and the cause was one step. Did not go well: the first two failures were not investigated before the third stopped a release.

## Design options

The ladder of TASK-43, each step removing more of the class:

1. Inputs we hold, by digest: every base image is copied into our mirror (TASK-96, R160 to R164), and the build tool is part of a pinned builder image (this change). Removes the deletion of a pinned image and the download of the build tool. Does not remove the dependency downloads.
2. Offline build: the Java, JavaScript and distribution packages are fetched once, by hash, into a cache we hold, and the build reaches no network. Removes the dependency downloads; costs a cache to build and keep. Recommended next.
3. Bit for bit: two builds of the same commit give the same image (R47). Lets a rebuild check what was promoted; needs step 2 first.

## Decision on the options

Approved by the founder: mirroring the base images (in progress, TASK-96) and this step, the build tool taken from a pinned builder image. Not decided: the offline cache of dependencies (step 2) and the reproducible build (step 3); they stay in TASK-43, which remains open, so this postmortem is guarded and not closed by design.

## Guards

- test `test_R167_build_downloads_no_build_tool` (requirement R167, with its `_detects_violation` companion): the build uses the register's pinned Maven image and calls neither the wrapper nor a download program; with `test_R167_maven_version_equals_the_forks_wrapper`, the Maven version of the image equals the fork's when the fork is checked out. A test, because the file can be read and the property is fixed by its text.
- Not protected: the downloads of dependencies, Node, pnpm and npm packages, which remain, are retried (R168) and can still fail.
