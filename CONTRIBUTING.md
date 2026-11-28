# Contributing to Anima

The rules every repository of the organization shares are in the
[contributing guide of the organization](https://github.com/cocreiamo/.github/blob/main/CONTRIBUTING.md):
the contributor license agreement (see the [privacy notice](PRIVACY.md) for the
data its signing records), Conventional Commits, signed commits, a pull
request for every change, and how to set up with mise. The code of conduct and
the security policy are in the same repository. This page lists what is
specific to Anima.

## Setting up

Besides the steps of the guide, fetch the forks first and install the hooks:

```sh
git submodule update --init --depth 1
mise run hooks:install
```

The development container in `.devcontainer/` is the other way to start. A
check forbids a `docker` command in the tasks, the workflows and the tests. The
development container is to be replaced by one in the same family as the engine
(Fedora with its own container runtime).

## Making a change

- A change in behaviour starts in the requirements model
  (`model/anima.sysml`): each requirement has a verification, and each
  verification is an automated test with the same name.
- A decision about the architecture of the product is recorded as an ADR in
  `docs/adr/`, made with `adrs new "Title"` and checked by
  `mise run adr:check`; how to write one is
  [`anima-writing-a-decision-record`](skills/anima-writing-a-decision-record.md).
  Anything else that is decided (how we work, licence and brand, tooling) is a
  rule of a skill, not a record.
- Work to do is a task of the backlog (`backlog/tasks/`), and something that
  went wrong is a postmortem (`docs/postmortems/`); how both work is
  [`anima-working-as-an-agent`](skills/anima-working-as-an-agent.md).
- Every dependency that ships with Anima is listed in `components.toml`.
- A known gap or defect of an adopted component is an entry in `gaps.toml`,
  the single register. A workaround in the repository names its entry in a
  comment, for example `# GAP-002`.

## Layout

- `model/`: the requirements model.
- `docs/adr/`: the architecture decision records. Elsewhere in `docs/`:
  `work/` (the templates of a brief, a report and a task, and the review
  checklist), `postmortems/`, `evaluation/` (the scenarios that evaluate the
  agent layer) and the generated `catalog.md`.
- `backlog/`: the tasks, one file each, made with the backlog tool.
- `agents/`: the roles of the agents that work here, as neutral files.
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
- `skills/`: design criteria, as agent-neutral skill documents (`AGENTS.md`
  says which one for which paths).
- `tests/`: `repository/` holds the verifications that need only the repository, `system/` those that start the engine image with Testcontainers.
- `third_party/`: the forked components, as git submodules.
- `shared/`: the repository `cocreiamo/.github` as a submodule. The workflows
  call its reusable workflows by the commit that carries them.
- `mise-tasks/`: the tasks that are scripts.
- `.github/` and `.devcontainer/`: continuous integration, repository settings and the development container.
- `LICENSES/`: the licence texts REUSE needs.

The registers `components.toml` and `gaps.toml` sit at the root beside
`mise.toml`.

## Changes to PostgreSQL, Keycloak or another forked component

These live in their own repositories and keep their upstream licence. See
[`anima-maintaining-a-fork`](skills/anima-maintaining-a-fork.md).
