# Contributing to Anima

Thank you for considering a contribution. This page lists the rules; each one
is checked automatically on your pull request.

## Before you start

- Read the [Code of Conduct](CODE_OF_CONDUCT.md).
- Contributions are accepted only under the
  [Contributor License Agreement](CLA.md). CLA Assistant asks you to sign it
  on your first pull request.
- Report security problems privately, as described in
  [SECURITY.md](SECURITY.md), not in an issue or a pull request.

## Setting up

Clone the repository, then either open it in the development container or
install [mise](https://mise.jdx.dev) yourself:

```sh
git submodule update --init --depth 1
mise trust && mise install
mise run hooks:install
mise run check
```

`mise run check` runs everything CI runs, and `mise run format` formats your
changes. The git hooks run the fast checks before each commit, check the
commit message, and run every check before a push.

Container work uses podman, which needs no daemon and no root. Docker is not
used in this repository, and a check forbids a `docker` command in the tasks,
the workflows and the tests. The development container is to be replaced by
one in the same family as the engine (Fedora with its own container runtime); until then it is
the one in `.devcontainer/`.

## Making a change

- Every change reaches `main` through a pull request.
- The pull request title follows
  [Conventional Commits](https://www.conventionalcommits.org), for example
  `feat: accept tokens from a second issuer`. Releases and the changelog are
  generated from these titles.
- Every commit is signed.
- A change in behaviour starts in the requirements model
  (`model/anima.sysml`): each requirement has a verification, and each
  verification is an automated test with the same name.
- A decision that shapes the architecture is recorded as an ADR in
  `docs/adr/`, in the MADR 4.0.0 format, created with `adrs new "Title"` and
  checked by `mise run adr:check` ([`anima-repository-conventions`](docs/adr/0013-decision-records-in-madr-managed-with-adrs.md)).
  The decision makers are written as a role (`founder`), and a reference to
  another ADR is a Markdown link, not a bare number.
- Every dependency is pinned to an exact version and listed in
  `components.toml` if it ships with Anima.
- A known gap or defect of an adopted component is an entry in `gaps.toml`,
  the single register. A workaround in the repository names its entry in a
  comment, for example `# GAP-002`.

## Layout

- `model/`: the requirements model.
- `docs/adr/`: the architecture decision records.
- `engine/`: the runtime, everything Anima ships, owned by the product. One
  directory per capability, never named after a product: `database/` (the
  database server), `access/` (identity provider, token validation, fixed
  roles and access rules), `secrets/` (secret store and root of trust),
  `backup/`, `vectors/` and `image/` (the engine image: its container file
  and the Quadlet units).
- `config/`: an instance's configuration, owned by the adopter, with the same
  capability names: `access/` holds identities and the roles they hold. Here it
  is the example configuration, used by tests and local development; an
  adopter mounts their own.
- `skills/`: design criteria, as agent-neutral skill documents.
- `tests/`: `repository/` holds the verifications that need only the repository, `system/` those that start the engine image with Testcontainers.
- `third_party/`: the forked components, as git submodules.
- `mise-tasks/`: the tasks that are scripts.
- `.github/` and `.devcontainer/`: continuous integration, repository settings and the development container.
- `LICENSES/`: the licence texts REUSE needs.

The registers `components.toml` and `gaps.toml` sit at the root beside
`mise.toml`.

## Changes to PostgreSQL, Keycloak or another forked component

These live in their own repositories and keep their upstream licence. See
[`anima-maintaining-a-fork`](docs/adr/0007-fork-maintenance.md).
