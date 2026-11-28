---
id: PM-014
date: 2026-11-28
title: The identity provider's build failed while downloading its build tool, and failed the first release
class: a build input fetched at build time from a site nobody holds, with no retry and no check
status: guarded
guards:
  - kind: test
    ref: test_R165_build_downloads_no_build_tool
    added: 2026-11-28
recurrences: []
---

# PM-014: The identity provider's build failed while downloading its build tool, and failed the first release

## Overview

The build of the identity provider's image ran the source's Maven wrapper, which downloads Maven from the central repository with `wget`, once, with no retry and no checksum. The download failed three times on 2026-11-28; the last failure stopped the promotion run of the first release.

## What happened

The container file ran `./mvnw ... clean install`. The wrapper of the fork is of the type `only-script`: it fetches the Maven distribution with `wget` or `curl`, keeps it under the Maven user home and starts it. In CI nothing was cached, so every build began with that download, and the site answered with an error (`wget: Failed to fetch`). The build had no other source of Maven, so it stopped before compiling anything.

## Root causes

- The build tool itself was an input fetched at build time from a site that is not ours, with no retry and no checksum.
- The builder image pinned the Java toolchain but not the build tool, so the pin looked complete when it was not.
- Nothing checked what a build downloads.

## Resolution

The builder is the official Maven image, pinned by digest and registered with the mirror like the other base images; the build calls `mvn`, which the image holds, and no longer calls the wrapper. The Maven version of the image is recorded in the register and must equal the version the fork's wrapper names. The dependency downloads that remain retry ten times through the resolver's own settings (R166).

## Impact

Three failed builds on 2026-11-28, one of them the promotion run of the first release (run 46146056321 of the repository); nothing was published from it.

## Timeline

| When       | What                                                                           |
| ---------- | ------------------------------------------------------------------------------ |
| 2026-11-28 | Two builds fail on the download of Maven.                                      |
| 2026-11-28 | The promotion run of the first release fails the same way.                     |
| 2026-11-28 | A spike finds the wrapper's behaviour; the builder is changed, a test written. |

## How did we do

Went well: the failing line was in the log and the cause was one step. Did not go well: the first two failures were not investigated before the third stopped a release.

## Guards

- test `test_R165_build_downloads_no_build_tool` (requirement R165, with its `_detects_violation` companion): the build uses the register's pinned Maven image, calls neither the wrapper nor a download program; with `test_R165_maven_version_equals_the_forks_wrapper`, the Maven version of the image equals the fork's when the fork is checked out.
- Not protected: the downloads of dependencies, Node, pnpm and npm packages, which remain, are retried (R166) and can still fail.
