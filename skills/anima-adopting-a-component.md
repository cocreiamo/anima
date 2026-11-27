---
name: anima-adopting-a-component
description: "Use when adding, replacing or evaluating a tool, library, service, GitHub Action, image or test suite for Anima, or when tempted to write a script of our own: order of preference, evaluation facts, fork and pinning mechanics, gaps.toml."
family: product
paths:
  - components.toml
  - gaps.toml
  - .gitmodules
  - .github/workflows/sync-forks.yml
---

# Adopting a component

How Anima takes in a tool, library, service, action, image or test suite.

## Use this when

- Adding a tool, library, service, GitHub Action, image or test suite.
- Replacing an adopted component, or comparing alternatives.
- Tempted to write a script, a wrapper or a small tool of our own.

## Rules

1. **Order of preference.** First the official mechanism of something already
   adopted; then the official tool of the ecosystem; then an established
   third-party tool; ours only as a last resort. Example: PostgreSQL's own
   `oauth_hook_client` for token logins (GAP-007), `mise generate devcontainer`
   for the development container. Not: an init container to
   generate secrets (ADR 0003), a C test client of ours.
2. **A script of ours is minimal and registered.** It is a mise file task in
   `mise-tasks/`, never a `tools/` directory, and it has a `gaps.toml` entry
   saying what upstream change would remove it. Example: `mise-tasks/model/check`
   and `mise-tasks/model/export` work around GAP-001 and GAP-002.
3. **Collect the facts before recommending.**
   - Licence: its SPDX identifier must be in `policy.allowed_licenses` of
     `components.toml`. Adding an identifier is the founder's decision. An
     excluded licence ends the discussion (HashiCorp Vault, BUSL, `anima-licensing-and-brand`).
   - Maturity and governance: who maintains it, how many maintainers, how
     young. A young tool loses to the reference implementation (OpenSysML
     rejected for the OMG Pilot Implementation); governance risk is recorded
     (pgBackRest).
   - Does it need a paid key, a licence key or an account? (`gitleaks-action`
     needs a key for organizations; the `gitleaks` binary does not.)
   - Does it run headless, in the development container and in CI alike, with
     no Docker daemon and no root?
   - Does it need its own PostgreSQL? That would be a circular dependency with
     the database server (Infisical and Conjur rejected, ADR 0003).
4. **Verify by running it.** Run the tool (a spike) before recommending it, and
   state in the proposal what was run and what was only read in documentation.
   Example: the OpenBao spike of ADR 0003 found that a failed
   self-initialization cannot be repaired (GAP-015). **A spike answers a
   question that can change a decision; otherwise the implementation is the
   verification.** A spike is throwaway code outside the repository, justified
   only while a decision is open and its answer could change it; once the
   decision is taken, verifying it means building it in the repository with
   its tests. What a spike found goes into the repository as evidence (an
   ADR's Confirmation section, an entry in `gaps.toml`); what worked in it is
   promoted, not rewritten (the validator's build recipe and the secret
   store's declarative configuration were). Not: a spike run in parallel with
   the implementation of the same thing, or kept going after its question is
   answered; the spike on how the engine's containers are run was closed the
   moment that decision was taken.
5. **A component built from source is a fork, pinned as a submodule,** with a `[[component]]` entry in `components.toml` (name, role, version, exact commit or image digest, SPDX licence, upstream, submodule path) and an entry in the fork-sync workflow; the mechanics and the branch rules are `anima-maintaining-a-fork`.
6. **Mechanics of adopting anything else.** Images by digest, never a tag alone, wherever they are referenced outside `third_party/`: the shipped components of `components.toml`, the images used only by tools and tests (the separate `[[tool_image]]` section, not shipped), the workflows, the tests, the mise tasks, the development container and the units under `engine/`; GitHub Actions by full commit SHA with minimal `permissions` (`zizmor` checks them); tools in `mise.toml` with an exact version, which `mise.lock` records with checksums. Renovate proposes the updates. Not: `latest`, a version range, a tool installed from the host, an image referenced by a tag alone (R11).
7. **Record every limit found.** A gap or defect of an adopted component is a `GAP-nnn` entry in `gaps.toml` (never one in a README or a comment), the workaround names the id in a comment (R25), and the gap has a task in the backlog. Closed entries are kept; ids are never reused.
8. **One tool per concern, and a tool follows the decision it serves.** Renovate proposes updates, so no Dependabot updates (Dependabot alerts are only a GitHub setting). Tools come from mise, so no wrapper action that downloads the same binary. One image scanner, not two. When a decision changes, the tool goes with it, with its task and its lock entries: the tools that checked a Kubernetes manifest were dropped when the engine stopped being declared as one (`anima-image-design`). Not: `hadolint-action` (the binary through mise keeps local and CI identical); `trivy-action` next to `anchore/scan-action` (one scanner is enough and it reads the SBOM); `gitleaks-action` (it needs a licence key for organizations, the binary does not); `step-security/harden-runner` (not adopted, no reason recorded); `kubeconform`, `kube-linter` and the `manifest:check` task (installed and never part of `check`); a tool kept "in case", or left installed and unused.
9. **Learn from what was rejected.** HashiCorp Vault: BUSL. SOPS: stores but does not issue or rotate. Podman secrets: storage only. Dynamic short-lived users for the identity provider: Keycloak cannot reload its database password (GAP-017). `rules_oci` and `rules_foreign_cc`: they would replace the container files and the upstream builds. OpenSysML: young; the OMG Pilot Implementation is the reference. `podman kube play` on the host's own podman: differs from machine to machine (GAP-018, GAP-019, closed); a Kubernetes manifest in general is replaced by native Quadlet units. Docker, in any role: not used.
10. **What is adopted, by concern, and in use today** (the tools of `mise.toml` and the workflows of `.github/workflows/` are listed in `docs/catalog.md`): REUSE (`reuse lint`, `fsfe/reuse-action`, `LICENSES/`, `REUSE.toml`); `SECURITY.md` with GitHub private vulnerability reporting (a GitHub setting); Contributor Covenant as `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `CODEOWNERS`; `gitleaks` and GitHub secret scanning with push protection (a setting); Dependabot alerts (a setting); `ruff`, `shellcheck`, `actionlint`, `buildifier`, Prettier, `taplo`, `typos` and `.editorconfig` for formatting and linting; hooks generated by `mise generate git-pre-commit`; `gaps.toml`; actions pinned by commit, `zizmor` and OpenSSF Scorecard; CodeQL on the workflows and the Python tests; Renovate (the configuration is in use, the app is installed on the organization); `actions/dependency-review-action` and Conventional Commits titles; the GitHub ruleset in `.github/rulesets/main.json`; `release-please` (`anima-branching-and-releasing`); the decision-record tool (`anima-tech-adrs-madr`); the backlog tool (`anima-tech-backlog-md`). Renovate and CLA Assistant are GitHub Apps installed on the organization, so the repository alone does not configure them.
11. Unverified: **the tools adopted for a named later step.** Nothing runs them yet: `pgdsat`, the CIS Benchmark of an earlier major version of the database server (GAP-004), which joins `promote:verify` once the engine image exists; `hadolint` for container files, which joins with the first container file that needs it; `bootc-image-builder` for disk images; `bazel-contrib/setup-bazel` for the first Bazel target; `redhat-actions/buildah-build`, `podman-login`, `push-to-registry` and `docker/metadata-action` for the first image build and publish workflow; the SBOM and attestation actions (`anchore/sbom-action`, `actions/attest-sbom`, `actions/attest-build-provenance`) and the vulnerability scan (`anchore/scan-action`) for the publish workflow (R16).

## Questions to answer before proposing

- Which official or established mechanism did you look for first, and what did
  you find?
- What did you run, and what did you only read?
- Which licence, and is it on the allowlist?
- What does it need to start: an account, a key, a database?
- Which gaps did you find, and what is each one's `resolved_when`?

## Where the result goes

The decision goes to an ADR (or an amendment to `anima-repository-conventions`'s adopted-tools
table). The component goes to `components.toml` (plus the submodule and
sync workflow if built from source); a tool to `mise.toml` and `mise.lock`;
every limit to `gaps.toml`.
