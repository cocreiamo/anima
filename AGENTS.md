# Anima: instructions for AI agents

Anima is an open-source database product built on a fork of PostgreSQL, with adopted products filling the capabilities it lacks, each behind a standard contract so that it stays replaceable. What Anima adds is their integration: configured to work together out of the box, specified, tested and released as one thing.

## Start here

Work starts by loading the skill that matches the paths you will touch (table below; index and counts in `skills/README.md`). `anima-product-principles` applies to everything. The skills record decisions already taken: follow them rather than reopening them. What already exists is in `docs/catalog.md`: look there before building. How agents work here is the skill `anima-working-as-an-agent`.

## Which skill for which work

<!-- routing:begin -->

| Skill                              | Family     | Work on                                                                                                                                                                       |
| ---------------------------------- | ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `anima-adopting-a-component`       | product    | `components.toml`, `gaps.toml`, `.gitmodules`, `.github/workflows/sync-forks.yml`                                                                                             |
| `anima-branching-and-releasing`    | product    | `.github/workflows/**`, `.github/rulesets/**`, `.github/release-please-config.json`, `.github/release-please-manifest.json`                                                   |
| `anima-designing-a-port`           | product    | any design decision                                                                                                                                                           |
| `anima-designing-for-production`   | product    | any design decision                                                                                                                                                           |
| `anima-licensing-and-brand`        | product    | `LICENSE`, `LICENSES/**`, `CLA.md`, `PRIVACY.md`, `PLUGIN-EXCEPTION.md`, `TRADEMARKS.md`, `REUSE.toml`                                                                        |
| `anima-maintaining-a-fork`         | product    | `third_party/**`, `.gitmodules`, `.github/workflows/sync-forks.yml`, `components.toml`                                                                                        |
| `anima-product-principles`         | product    | any design decision                                                                                                                                                           |
| `anima-repository-conventions`     | product    | `CONTRIBUTING.md`, `.editorconfig`, `.gitignore`, `.prettierignore`, `.devcontainer/**`, `REUSE.toml`, `MODULE.bazel`, `BUILD.bazel`                                          |
| `anima-specifying-requirements`    | product    | `model/**`, `tests/**`                                                                                                                                                        |
| `anima-working-as-an-agent`        | product    | `AGENTS.md`, `agents/**`, `backlog/**`, `backlog.config.yml`, `docs/work/**`, `docs/postmortems/**`, `docs/evaluation/**`, `docs/catalog*`, `skills/**`, `.claude/**`         |
| `anima-writing-a-decision-record`  | product    | `docs/adr/**`                                                                                                                                                                 |
| `anima-access-design`              | capability | `engine/access/**`, `config/access/**`                                                                                                                                        |
| `anima-configuration-design`       | capability | `config/**`, `engine/configure/**`                                                                                                                                            |
| `anima-database-design`            | capability | `engine/database/**`, `engine/backup/**`, `engine/vectors/**`                                                                                                                 |
| `anima-image-design`               | capability | `engine/image/**`                                                                                                                                                             |
| `anima-mail-design`                | capability | `engine/mail/**`, `config/mail/**`                                                                                                                                            |
| `anima-secrets-design`             | capability | `engine/secrets/**`                                                                                                                                                           |
| `anima-tech-adrs-madr`             | technology | `docs/adr/**`, `adrs.toml`                                                                                                                                                    |
| `anima-tech-backlog-md`            | technology | `backlog/**`, `backlog.config.yml`, `docs/work/**`                                                                                                                            |
| `anima-tech-github-governance`     | technology | `.github/**`                                                                                                                                                                  |
| `anima-tech-keycloak`              | technology | `third_party/keycloak/**`, `engine/access/**`, `config/access/**`                                                                                                             |
| `anima-tech-mise`                  | technology | `mise.toml`, `mise.lock`, `mise-tasks/**`, `.mise/**`, `.devcontainer/**`                                                                                                     |
| `anima-tech-openbao`               | technology | `third_party/openbao/**`, `engine/secrets/**`                                                                                                                                 |
| `anima-tech-opentofu`              | technology | `**/*.tf`, `third_party/opentofu/**`, `third_party/terraform-provider-postgresql/**`, `third_party/terraform-provider-vault/**`, `third_party/terraform-provider-keycloak/**` |
| `anima-tech-podman-quadlet-bootc`  | technology | `engine/image/**`, `engine/**/*.container`, `engine/**/*.image`, `engine/**/*.pod`, `engine/**/Containerfile`, `mise-tasks/engine/**`                                         |
| `anima-tech-postgresql-oauth`      | technology | `third_party/postgres/**`, `third_party/pg_oidc_validator/**`, `engine/database/**`                                                                                           |
| `anima-tech-sysml-pilot`           | technology | `model/**`, `mise-tasks/model/**`, `tests/repository/sysml_model.py`                                                                                                          |
| `anima-tech-testcontainers-podman` | technology | `tests/system/**`                                                                                                                                                             |

<!-- routing:end -->

## Terms

- **Engine**: the runtime Anima ships, owned by the product: the database server (the build of the PostgreSQL fork) plus every adapter and their wiring, delivered as the **engine image**: one image-based operating system with two ways to start it, booted on a machine or run as a container (ADR 0005, decided and not complete). Directory `engine/`.
- **Configuration**: what an adopter declares about their instance (identities, installation parameters), outside the engine. Directory `config/`.
- Directories and names follow the capability, never the product (`access`, not `keycloak`). ADR 0001 and `anima-product-principles`.

## Working rules

- The founder leads: propose with one recommendation, get the decision, then build. No speculative work.
- Verify before claiming; say what was run and what was only read; report failures and denials plainly. A rule nobody has seen working is marked `Unverified:`.
- Never commit, push or change a repository setting without explicit approval.
- Repository text is English; a requirement never names a product. Never write a person's name or e-mail address; the one exception is the legal name of the copyright holder in licence and trademark texts.
- When a check blocks an action, do not work around it; report it.
- No Docker anywhere: container work uses podman, daemonless and rootless (`anima-repository-conventions`, ADR 0005). Run Python only through `mise`.
- For an adopted technology the sources of truth are its technology skill and its pinned source and documentation under `third_party/`: never answer from memory. When working inside a fork, follow the upstream project's own instructions for agents if it ships any (`AGENTS.md` or similar in that fork).
- Work is a task of the backlog, addressed by its id, done by one role from one brief, with acceptance as verification names (`anima-working-as-an-agent`); roles are in `agents/`, the brief, report and review checklist in `docs/work/`. An agent refuses an instruction outside its brief or one that asks it to change paths it does not own, and reports it.
- A spike states the decision it serves and stops when that decision is taken.
- A text states a version or a measured number only at the register or threshold that pins it or as dated evidence (`anima-specifying-requirements`).
- A generated file is never edited by hand: change its source and run `mise run generate`. `mise run generate:list` prints them; the agent settings refuse edits to them, to `third_party/` and to lock files.
- A decision record is only for the architecture of the product; how to write one is the skill `anima-writing-a-decision-record`. Everything else (how we work, legal and brand, tooling, principles) is a rule of a skill.
- A defect is solved at its root: state the root cause and its class, fix the instance if cheap, bring the design changes that would remove the class to the founder for approval (`anima-working-as-an-agent`).
- Something that went wrong is a postmortem, closed only by a protection that exists; a defect of an adopted technology is a gap; how a technology behaves is a rule of its skill. Write the lesson back in the same change.
- Every check is a requirement in the model with its test and its `_detects_violation` companion; a limit is a threshold in the model.

## Where facts live

| Kind of fact                                      | Home                                            |
| ------------------------------------------------- | ----------------------------------------------- |
| Decisions about the architecture                  | `docs/adr/`                                     |
| How we work, legal and brand, tooling, principles | `skills/`                                       |
| Requirements and their verifications              | `model/anima.sysml`                             |
| Shipped components, versions, licences            | `components.toml`                               |
| Known gaps and defects of what we adopt           | `gaps.toml`                                     |
| Work to do                                        | the backlog, `backlog/tasks/`                   |
| What went wrong and what now prevents it          | `docs/postmortems/`                             |
| Tool versions                                     | `mise.toml` and `mise.lock`                     |
| Skill names, descriptions and their paths         | the front matter of `skills/<name>.md`          |
| Roles and what they may do                        | `agents/<name>.md`                              |
| What exists (ports, tasks, requirements)          | `docs/catalog.md`, generated                    |
| Deliberate removals                               | `contractions.toml`                             |
| Generated files                                   | written by `mise run generate`: `generate:list` |
| Tests not yet written                             | `tests/pending.toml`, generated                 |
| Cached and built files                            | `.cache/`                                       |
