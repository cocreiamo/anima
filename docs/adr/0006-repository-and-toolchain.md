---
number: 6
title: One repository, its toolchain and pinned dependencies
status: proposed
date: 2026-11-27
decision-makers: [founder]
---

# One repository, its toolchain and pinned dependencies

## Context and Problem Statement

Anima is assembled from a PostgreSQL fork and adopted products ([ADR-0001](0001-hexagonal-architecture.md)). The
founder wants a single place to work in, the ability to contribute patches
upstream, and no tooling invented where an existing tool does the job. How the
assembled product is delivered and operated is [ADR-0011](0011-engine-image-and-runtime.md).

How are the model, the decisions, the composition, the tests and the release kept in one working repository, with which toolchain, and how are dependencies pinned, so that no tooling is invented where an existing tool does the job?

## Decision Drivers

- A single place to work in.
- The ability to contribute patches upstream.
- No tooling invented where an existing tool does the job.

## Considered Options

- One repository with the forks as submodules, `mise` as the one entry point
  and each kind of source built by its own tool
- `rules_oci` and `rules_foreign_cc` to build everything with Bazel
- `gitleaks-action`
- `hadolint-action`
- `trivy-action`
- `step-security/harden-runner`
- `kubeconform`, `kube-linter` and the `manifest:check` task (dropped)

## Decision Outcome

Chosen option: "One repository with the forks as submodules, `mise` as the one entry point and each kind of source built by its own tool", because it gives a single place to work in, keeps patches contributable upstream and invents no tooling.

### Repository

1. `anima` is the single working repository: model, ADRs, composition, tests
   and release.
2. A component built from source is a real fork in its own repository, added
   to `anima` as a git submodule under `third_party/`:
   `third_party/postgres` (`anima-postgres`), `third_party/keycloak`
   (`anima-keycloak`), `third_party/pg_oidc_validator`
   (`anima-pg-oidc-validator`), `third_party/pgvector` (`anima-pgvector`),
   `third_party/pgbackrest` (`anima-pgbackrest`) and `third_party/openbao`
   (`anima-openbao`). A commit of `anima` pins the exact commit of each, and
   one pipeline builds everything from source. Every tool that skips the forks
   (Bazel, Prettier, `typos`, `ruff`) skips the one directory `third_party`.
3. `components.toml` lists every shipped component with its version, its
   commit or digest, and its SPDX licence. A test checks that every submodule
   is a declared component and lives under `third_party/`.
4. **Layout.** Each top-level directory has one purpose. Directories are
   organized by capability, never by the product that currently provides it
   ([ADR-0012](0012-declared-once-converged-generated.md)).

   | Directory                    | Holds                                                                  |
   | ---------------------------- | ---------------------------------------------------------------------- |
   | `model/`                     | the requirements model, `anima.sysml`                                  |
   | `docs/adr/`                  | the architecture decision records                                      |
   | `skills/`                    | design criteria, as agent-neutral skill documents                      |
   | `engine/`                    | the runtime: everything Anima ships, owned by the product              |
   | `engine/database/`           | the database server: build of the PostgreSQL fork, its configuration   |
   | `engine/access/`             | identity provider, token validation, fixed roles and access rules      |
   | `engine/secrets/`            | secret store and root of trust                                         |
   | `engine/backup/`             | backup and restore                                                     |
   | `engine/vectors/`            | vector search                                                          |
   | `engine/image/`              | the engine image: its container file and the Quadlet units             |
   | `config/`                    | an instance's configuration, owned by the adopter                      |
   | `config/access/`             | identities and the roles they hold                                     |
   | `tests/repository/`          | verifications that need only the repository                            |
   | `tests/system/`              | verifications that start the engine image with Testcontainers          |
   | `third_party/`               | the forks, as submodules                                               |
   | `mise-tasks/`                | the tasks that are scripts                                             |
   | `.github/`, `.devcontainer/` | continuous integration, repository settings, the development container |

   The capability names under `engine/` and `config/` mirror each other.
   `config/` in this repository holds the example configuration, which is also
   the one used by tests and local development (the special environment, [ADR-0011](0011-engine-image-and-runtime.md)); an adopter mounts their own.

   `components.toml` and `gaps.toml` sit at the root beside `mise.toml`, being
   registers read by tests and by people alike. The leaf directories of
   `engine/` and `config/` hold only a `.gitkeep` until the step that fills
   them.

5. `mise` pins the tools and defines the tasks. Developers and CI run the same
   `mise run <task>`; `mise run check` runs every check. A task that is a
   script is a mise file task in `mise-tasks/` (`model:check`,
   `model:export`). Everything generated or cached goes under `.cache/`, the
   one ignored directory.
6. Each kind of source is built by the tool made for it; none is forced into
   another.
   - Anima's own code is built and tested with Bazel (`bazelisk`,
     `.bazelversion`, `MODULE.bazel` with its lock file).
   - A forked component is built with its upstream build system. `third_party`
     is excluded from Bazel in `.bazelignore`.
   - Images are built from container files with `buildah` or `podman build`,
     which copy in what the two builds above produce. Docker is not used, in
     development, tests, CI or documentation. The database server's image
     starts from the official `docker-library/postgres` container file,
     pointed at the fork's source; the engine image carries it, with the other
     images, inside. The Keycloak image is built with upstream's own build from
     the fork's source. The engine image is built from the Fedora bootc base
     image ([ADR-0011](0011-engine-image-and-runtime.md)); disk images are produced from it by
     `bootc-image-builder`. Images are published for amd64 and arm64.
7. The development container is today the one `mise generate devcontainer`
   produces: the official `devcontainers/base` image plus the mise dev
   container feature, both pinned by digest. `mise install` then installs
   every tool. Tools come from `mise` and from nowhere on the host, so
   development is as machine-agnostic as the product ([ADR-0011](0011-engine-image-and-runtime.md)). **It is to be
   replaced**: it is a Debian-family image, and the development container is
   to move to the same family as the engine, Fedora with its own container runtime. How the
   pinned tools are installed there is not settled (GAP-021).

### Pinned versions

Every image, tool, action and source dependency is referenced by a fixed
version together with its digest or commit. `latest` and other floating
references are never used. Renovate proposes the updates. An image is
pinned by digest wherever it is referenced outside `third_party/`: the
shipped components of `components.toml`, the images used only by tools
and tests (the separate `[[tool_image]]` section of `components.toml`,
not shipped), the workflows, the tests, the mise tasks, the development
container and, later, the units under `engine/`. An image referenced by
a tag alone is a defect (R11). The same pinned
sources must also produce the same image, bit for bit, so that building again
checks what was promoted (R47, [ADR-0012](0012-declared-once-converged-generated.md)); the verification is pending and
nothing of it is built.

### Caches in CI

- Image layers: `buildah` uses the registry (GHCR) as layer cache. This is
  the cache that matters for PostgreSQL and Keycloak built from source. Not in
  use yet: no image is built.
- Bazel: `bazel-contrib/setup-bazel` keeps Bazel's disk cache in the GitHub
  Actions cache. Not in use yet: there is no Bazel target to build. A remote
  cache follows when there is code to build.
- Tools: `mise-action` caches the tools; the Pilot Implementation is kept
  with `actions/cache`, keyed on its checksum. Both are in use.
- A release build restores no cache ([ADR-0008](0008-trunk-main-green-and-releases.md)).

### Verification

1. Every requirement in `model/anima.sysml` has a verification, and every
   verification is an automated test with the same name
   (`test_<id>_<what>`). `tests/repository/test_traceability.py` reads the
   model through the Pilot Implementation's JSON export and fails if the two
   sets differ. A verification whose test is not written yet is listed in
   `tests/pending.toml`; that list shrinks as tests are written, grows only
   when a requirement is added, and is empty at 0.0.1.
2. Tests are written with `pytest`. A test may run an adopted tool and assert
   on its result. Token logins use `oauth_hook_client`, the test client in
   PostgreSQL's own source (`src/test/modules/oauth_validator`), which takes a
   bearer token on the command line (GAP-007).
3. Tests that need the running system start the engine image with
   Testcontainers ([ADR-0011](0011-engine-image-and-runtime.md)), through podman's own API service, started on
   demand for the test session. No daemon and no host service is assumed, and
   the host's own podman setup plays no part. A spike of 2026-11-27 (rootless podman 4.9.3, testcontainers 4.15.0)
   started the system through that service and left nothing behind; two
   limits remain (GAP-022). Flows and
   drills, such as backup and restore, are tests like any other. Such tests
   live in `tests/system/`; those that need only the repository live in
   `tests/repository/`.
   The units of the engine are checked without starting them, with Quadlet's
   dry run and `systemd-analyze verify` inside a container of the engine image
   (R52). Not in use: it needs the engine image.
4. One end-to-end test drives the device flow of `psql` in a browser with
   Playwright.
5. PostgreSQL's own regression suite runs against the database server built
   from the fork, on every run: it is quick and the database server is the
   heart of the product.
6. The test suite of any other fork runs only while that fork carries changes
   of ours, and then only for the parts changed. Keycloak carries none, so its
   suite does not run.

### Adopted tools and actions

The last column says whether the entry is in use today (it appears in
`mise.toml`, in `.github/workflows/` or as a file of this repository) or is
adopted for a named later step.

| Concern                             | Adopted                                                                                                                                                                                                        | Today                                                                                    |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Licence and copyright of every file | REUSE: `reuse lint`, `fsfe/reuse-action`, `LICENSES/`, `REUSE.toml`                                                                                                                                            | In use                                                                                   |
| Vulnerability reports               | `SECURITY.md` with GitHub private vulnerability reporting                                                                                                                                                      | `SECURITY.md` in use; the reporting is a GitHub setting                                  |
| Community files                     | Contributor Covenant 3.0 as `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CODEOWNERS`                                                                                                                              | In use                                                                                   |
| Secrets in the repository           | `gitleaks`; GitHub secret scanning with push protection                                                                                                                                                        | `gitleaks` in use; scanning is a GitHub setting                                          |
| Vulnerable dependencies             | Dependabot alerts                                                                                                                                                                                              | A GitHub setting                                                                         |
| Formatting and linting              | `ruff` (Python), `shellcheck` (shell), `actionlint` (workflows), `buildifier` (Bazel), Prettier (Markdown, YAML, JSON), `taplo` (TOML), `typos` (spelling), `.editorconfig`; upstream's own tools in the forks | In use                                                                                   |
| Git hooks                           | generated by `mise generate git-pre-commit` and installed by `mise run hooks:install`: `pre-commit` (fast checks), `commit-msg` (Conventional Commits with `committed`), `pre-push` (every check)              | In use                                                                                   |
| Tool versions                       | `mise.toml` with `mise.lock`, which records the download URL and checksum of every tool                                                                                                                        | In use                                                                                   |
| Hardening of the database server    | `pgdsat`, the CIS Benchmark for PostgreSQL as a test suite                                                                                                                                                     | Not in use: joins `promote:verify` once the engine image exists (GAP-004)                |
| Gaps of adopted components          | `gaps.toml`, the register of known gaps and defects: one `GAP-nnn` entry each, named in a comment by every workaround in the repository (R25)                                                                  | In use                                                                                   |
| Workflow security                   | actions pinned by commit, minimal `permissions`, `zizmor`, OpenSSF Scorecard                                                                                                                                   | In use (`scorecard.yml`, `workflows:check`)                                              |
| Static analysis of first-party code | CodeQL, on the workflows and the Python tests                                                                                                                                                                  | In use (`codeql.yml`)                                                                    |
| Dependency updates                  | Renovate                                                                                                                                                                                                       | Configuration in use (`.github/renovate.json`); the app is installed on the organization |
| Pull requests                       | `actions/dependency-review-action`, Conventional Commits titles with `amannn/action-semantic-pull-request`                                                                                                     | In use (`pull-request.yml`)                                                              |
| Rules on `main`                     | GitHub ruleset in `.github/rulesets/main.json`: pull request required, required checks, signed commits, no force push, no deletion                                                                             | The file is in use; the ruleset is applied on GitHub                                     |
| Decision records                    | MADR 4.0.0 files in `docs/adr/`, created and checked with `adrs`; the index is generated from `adrs export json` filtered with `jq` ([ADR-0013](0013-decision-records-in-madr-managed-with-adrs.md))           | In use (`adr:check`, `generate`)                                                         |
| Container files                     | `hadolint`                                                                                                                                                                                                     | Not in use: not yet in `mise.toml`; joins with the first container file under `engine/`  |
| Units of the engine                 | Quadlet's dry run with `systemd-analyze verify`, run inside a container of the engine image (R52)                                                                                                              | Adopted, not in use: needs the engine image and the units in `engine/image/`             |
| Disk images                         | `bootc-image-builder`: disk images produced from the engine image ([ADR-0011](0011-engine-image-and-runtime.md))                                                                                               | Adopted, not in use: needs the engine image                                              |
| Versions and releases               | `release-please`: release pull request and changelog from Conventional Commits; the tag and the GitHub release come from the Promote workflow ([ADR-0008](0008-trunk-main-green-and-releases.md))              | In use (`prepare-release.yml`, `promote.yml`)                                            |
| Bazel cache                         | `bazel-contrib/setup-bazel`                                                                                                                                                                                    | Not in use: adopted for the first Bazel target                                           |
| Build and publish                   | `redhat-actions/buildah-build`, `podman-login`, `push-to-registry`; tags and OCI labels from `docker/metadata-action`                                                                                          | Not in use: adopted for the first image build and publish workflow                       |
| Published images                    | SBOM with `anchore/sbom-action` (syft), `actions/attest-sbom`, `actions/attest-build-provenance`, vulnerability scan with `anchore/scan-action`                                                                | Not in use: adopted for the publish workflow (R16)                                       |

### Consequences

- Neutral, because one clone and one pipeline; the price is building
  PostgreSQL and Keycloak from source on every run, so the build needs a
  cache.
- Bad, because there are two caches to keep: Bazel's for Anima's own code,
  and the image layer cache for the forks.
- Neutral, because submodules must be updated deliberately; that update is
  the act of adopting a new upstream version.
- Neutral, because the nightly package of `pg_oidc_validator` must not be
  used; the validator is built from the pinned source (GAP-005, closed).
- Bad, because `pgdsat` implements the CIS Benchmark of an earlier major version of PostgreSQL, not
  18 (GAP-004).
- Good, because known gaps of adopted components are not scattered in the
  text: they are entries of `gaps.toml`, each to be resolved, often by
  contributing upstream.
- Bad, because Renovate and CLA Assistant are GitHub Apps installed on the
  organization; they are not configured by this repository alone.

### Confirmation

Built and verified in `tests/repository/`: R10 (`test_R10_every_requirement_verified`, the traceability between the model and the tests), R11 (`test_R11_every_dependency_pinned`, exact versions, digests and commits, no Docker), R17 (`test_R17_component_licenses_allowed`), R18 (`test_R18_every_file_licensed`), R25 (`test_R25_every_gap_registered`) and R38 (`test_R38_derived_files_generated`). Pending, not written: R47 (reproducible builds) and R52 (engine parts validated without starting). Not built: the container files, the image layer cache, the Bazel cache and the publish workflow; the table of adopted tools says for each entry whether it is in use.

## Pros and Cons of the Options

### `rules_oci` and `rules_foreign_cc` to build everything with Bazel

- Bad, because they would replace the upstream container file and build systems this ADR adopts.

### `gitleaks-action`

- Bad, because it needs a licence key for organizations; the binary does the same.

### `hadolint-action`

- Bad, because the binary through `mise` keeps local and CI identical.

### `trivy-action`

- Bad, because one scanner is enough, and `scan-action` reads the syft SBOM.

### `step-security/harden-runner`

- Bad, because it was not adopted for 0.0.1; the original record states no reason.

### `kubeconform`, `kube-linter` and the `manifest:check` task (dropped)

- Bad, because they were installed and the task defined, but never part of `check`.
- Bad, because the engine is no longer declared as a Kubernetes manifest ([ADR-0011](0011-engine-image-and-runtime.md)), so neither is needed; `kube-linter-action` goes with them.
