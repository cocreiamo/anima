"""The commands that the workflows call, run for real: the path filter, the key of
the inner images, the plan of the mirror and the sync of a fork. R172, R173, R175,
R177.

Run through `mise run ci:test`. `gh` is the one tool without a stand-in here: the
tests of `ci:changes` and `ci:sync-fork` put a stub first on the PATH. The stub of
`ci:changes` answers with a response recorded from the platform's compare API on
2026-11-28 (`fixtures/compare-recorded.json`: the fields the command reads, the
commits left out), so the decision and the reading of the answer are run for real
and only the one call is not; the stub of `ci:sync-fork` shows that the arguments
reach the tool and that its failure is the command's. What these tests therefore do
not show is that the platform accepts the call.
"""

import json
import os
import re
import subprocess
import tomllib

from ci_support import (
    FIXTURES,
    ROOT,
    recorder_command,
    register_entry,
    stub_command,
    task,
)

RECORDED = json.loads((FIXTURES / "compare-recorded.json").read_text())
NULL = "0" * 40
# The pattern of the workflow itself, so that the test reads what runs.
WORKFLOW = (ROOT / ".github" / "workflows" / "system-tests.yml").read_text()
RELEVANT = re.search(r"^\s+RELEVANT:\s*'([^']*)'", WORKFLOW, re.MULTILINE).group(1)


def gh_stub(tmp_path, pages, status=0, stderr=""):
    """A `gh` that prints the given pages (one JSON document each, as --paginate
    does) and records its arguments."""
    answers = tmp_path / "answers"
    answers.mkdir(parents=True, exist_ok=True)
    for number, page in enumerate(pages):
        (answers / f"{number}.json").write_text(json.dumps(page))
    log = tmp_path / "gh.log"
    env = stub_command(
        tmp_path / "bin",
        "gh",
        f'echo "$@" >> "{log}"\n'
        f'echo "{stderr}" >&2\n'
        f'cat "{answers}"/*.json\n'
        f"exit {status}\n",
    )
    return env, log


def changes(tmp_path, env, base="a" * 40, relevant=RELEVANT):
    result = task(
        "changes",
        env={
            **env,
            "BASE": base,
            "HEAD": "b" * 40,
            "GITHUB_REPOSITORY": "org/repo",
            "RELEVANT": relevant,
            "EVENT": "pull_request",
        },
    )
    return result, result.stdout


def with_files(*names):
    return {"files": [{"filename": n, "status": "modified"} for n in names]}


# ---- R172: the change filter decides from the comparison, and a failure is not "no change" ----


def test_R172_change_filter_decides_from_the_comparison(tmp_path):
    """Proves, with the recorded response of the compare API, that a change of the
    engine counts, that one of the documents does not, that a renamed file counts
    by its old name, that the answer is read across pages, and that without a base
    the change counts."""
    # The recorded change touches the model, skills, the catalog and tests of the
    # repository, none of them the engine's.
    env, log = gh_stub(tmp_path, [RECORDED])
    result, written = changes(tmp_path, env)
    assert result.returncode == 0, result.stderr
    assert written == "relevant=false\n"
    assert "repos/org/repo/compare/" + "a" * 40 + "..." + "b" * 40 in log.read_text()
    assert "--paginate" in log.read_text()

    # The same response, with a file of the engine added.
    touched = {**RECORDED, "files": RECORDED["files"] + with_files("engine/x")["files"]}
    env, _ = gh_stub(tmp_path / "t", [touched])
    result, written = changes(tmp_path / "t", env)
    assert written == "relevant=true\n"
    assert "engine/x" in result.stderr

    # A file moved out of the engine counts by its old name (the response shape of
    # a renamed file is the documented one; the history has none to record).
    moved = {
        "files": [
            {
                "filename": "docs/x.md",
                "previous_filename": "config/x.md",
                "status": "renamed",
            }
        ]
    }
    env, _ = gh_stub(tmp_path / "m", [moved])
    assert changes(tmp_path / "m", env)[1] == "relevant=true\n"

    # Two pages: the engine's file is on the second.
    env, _ = gh_stub(tmp_path / "p", [RECORDED, with_files("third_party/postgres")])
    assert changes(tmp_path / "p", env)[1] == "relevant=true\n"

    # Without a base, or with the null commit, there is nothing to compare: relevant,
    # and the platform is not asked.
    for base in ("", NULL):
        env, log = gh_stub(tmp_path / f"n{len(base)}", [{"files": []}], status=1)
        result, written = changes(tmp_path / f"n{len(base)}", env, base=base)
        assert result.returncode == 0 and written == "relevant=true\n"
        assert not log.exists()


def test_R172_change_filter_decides_from_the_comparison_detects_violation(tmp_path):
    """Wrong answers of the platform fail the command and write nothing: "cannot
    tell" is never "nothing changed"."""
    # The call fails.
    env, _ = gh_stub(tmp_path / "f", [], status=1, stderr="HTTP 404")
    result, written = changes(tmp_path / "f", env)
    assert result.returncode != 0 and written == ""

    # The call succeeds with something that is not a comparison.
    env, _ = gh_stub(tmp_path / "g", [{"message": "Not Found"}])
    result, written = changes(tmp_path / "g", env)
    assert result.returncode != 0 and written == ""

    # The pattern is mandatory.
    env, _ = gh_stub(tmp_path / "h", [RECORDED])
    result, written = changes(tmp_path / "h", env, relevant="")
    assert result.returncode != 0 and written == ""

    # The decision answers the pattern it is given: the same recorded change is
    # relevant to a pattern that names the model.
    env, _ = gh_stub(tmp_path / "i", [RECORDED])
    assert changes(tmp_path / "i", env, relevant="^model/")[1] == "relevant=true\n"


# ---- R173: the key of the inner images follows what they are made of ------------------------


def git(*arguments, cwd):
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", *arguments],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.invalid",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.invalid",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_SYSTEM": "/dev/null",
        },
    )


def repository_with_submodule(tmp_path):
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    git("init", "-q", "-b", "main", cwd=upstream)
    (upstream / "f").write_text("1")
    git("add", ".", cwd=upstream)
    git("commit", "-q", "-m", "one", cwd=upstream)
    repo = tmp_path / "repo"
    for directory in ("engine/a", "mise-tasks/engine", "mise-tasks/ci", "config"):
        (repo / directory).mkdir(parents=True)
    (repo / "engine/a/Containerfile").write_text("FROM scratch\n")
    (repo / "mise-tasks/engine/build").write_text("build\n")
    (repo / "mise-tasks/ci/other").write_text("other\n")
    (repo / "config/c.yaml").write_text("c: 1\n")
    (repo / "README.md").write_text("readme\n")
    git("init", "-q", "-b", "main", cwd=repo)
    git("submodule", "add", "-q", str(upstream), "third_party/x", cwd=repo)
    git("add", ".", cwd=repo)
    git("commit", "-q", "-m", "base", cwd=repo)
    return repo, upstream


def key(repo, **env):
    result = task("cache-key", str(repo), env=env)
    assert result.returncode == 0, result.stderr
    assert re.fullmatch(r"value=[0-9a-f]{16}\n", result.stdout), result.stdout
    return result.stdout.strip().removeprefix("value=")


def test_R173_cache_key_follows_what_the_inner_images_are_made_of(tmp_path):
    """Proves, on a throwaway repository with a submodule, that the key is the same
    for the same inputs, changes with a file of the engine, of its tasks or of the
    configuration and with the commit a submodule is pinned to, and does not change
    with a file that the images are not made of."""
    repo, upstream = repository_with_submodule(tmp_path)
    first = key(repo)
    assert re.fullmatch(r"[0-9a-f]{16}", first)
    assert key(repo) == first

    for unrelated in ("README.md", "mise-tasks/ci/other"):
        (repo / unrelated).write_text("changed\n")
        assert key(repo) == first, unrelated

    seen = {first}
    for related in (
        "engine/a/Containerfile",
        "mise-tasks/engine/build",
        "config/c.yaml",
    ):
        (repo / related).write_text("changed\n")
        changed = key(repo)
        assert changed not in seen, related
        seen.add(changed)

    # The commit that the submodule is pinned to.
    (upstream / "f").write_text("2")
    git("commit", "-q", "-am", "two", cwd=upstream)
    git("-C", "third_party/x", "pull", "-q", "origin", "main", cwd=repo)
    assert key(repo) not in seen


def test_R173_cache_key_follows_what_the_inner_images_are_made_of_detects_violation(
    tmp_path,
):
    """Inputs that are not there make the command fail instead of giving a key
    that hashes nothing."""
    (tmp_path / "bare").mkdir()
    assert task("cache-key", str(tmp_path / "bare")).returncode != 0
    repo, _ = repository_with_submodule(tmp_path)
    (repo / "engine/a/Containerfile").unlink()
    (repo / "engine/a").rmdir()
    (repo / "engine").rmdir()
    assert task("cache-key", str(repo)).returncode != 0


# ---- R175: the plan of the mirror is the register's ------------------------------------------


def plan(register=None):
    arguments = [str(register)] if register else []
    return task("mirror-plan", *arguments)


def test_R175_mirror_plan_comes_from_the_register(tmp_path):
    """Proves that the plan lists every image of the register with the fields the
    copy reads, and names the copy tool by its digest, from the register itself."""
    result = plan()
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert [line.split("=", 1)[0] for line in lines] == ["images", "skopeo"]
    matrix = json.loads(lines[0].split("=", 1)[1])
    register = tomllib.loads((ROOT / "components.toml").read_text())
    imaged = [
        c
        for c in register["component"] + register.get("tool_image", [])
        if "image" in c
    ]
    assert [i["name"] for i in matrix["include"]] == [c["name"] for c in imaged]
    for entry, planned in zip(imaged, matrix["include"], strict=True):
        assert planned == {
            field: entry[source]
            for field, source in (
                ("name", "name"),
                ("image", "image"),
                ("tag", "version"),
                ("digest", "digest"),
                ("mirror", "mirror"),
            )
        }
    skopeo = register_entry("skopeo")
    assert lines[1] == f"skopeo={skopeo['image']}@{skopeo['digest']}"


def test_R175_mirror_plan_comes_from_the_register_detects_violation(tmp_path):
    """A register without the copy tool, or without a file, is a failure, and a
    register with one image plans one."""
    register = tmp_path / "register.toml"
    register.write_text(
        '[[component]]\nname = "a"\nimage = "x/a"\nversion = "1"\n'
        'digest = "sha256:' + "0" * 64 + '"\nmirror = "m/a"\n'
    )
    result = plan(register)
    assert result.returncode != 0 and "skopeo" in result.stderr
    assert plan(tmp_path / "missing.toml").returncode != 0

    register.write_text(register.read_text() + register_text_of("skopeo"))
    result = plan(register)
    assert result.returncode == 0
    names = [
        i["name"] for i in json.loads(result.stdout.splitlines()[0][7:])["include"]
    ]
    assert names == ["a", "skopeo"]


def register_text_of(name):
    entry = register_entry(name)
    fields = ("name", "version", "image", "digest", "mirror")
    return "[[tool_image]]\n" + "".join(f'{k} = "{entry[k]}"\n' for k in fields)


# ---- R177: the sync of a fork passes its arguments and does not hide a failure -----------------


def test_R177_fork_sync_passes_its_arguments_to_the_platform_tool(tmp_path):
    """Proves, with a stub of `gh` (no stand-in exists for the platform), that the
    fork, the upstream and the branch reach the tool in the right places and that
    the command ends with the tool's own status."""
    log = tmp_path / "log"
    env = recorder_command(tmp_path / "bin", "gh", log)
    # What the step gave is the installation token of the fork-sync App.
    env["GH_TOKEN"] = "fork-sync-app-token"
    result = task("sync-fork", "org/fork", "up/stream", "release/1.2", env=env)
    assert result.returncode == 0, result.stderr
    assert log.read_text() == (
        "repo sync org/fork --source up/stream --branch release/1.2 "
        "credential=fork-sync-app-token\n"
    )


def test_R177_fork_sync_passes_its_arguments_to_the_platform_tool_detects_violation(
    tmp_path,
):
    """A refusal of the tool (a branch that diverged) fails the command with the
    tool's message; a missing or empty argument fails before the tool is called."""
    log = tmp_path / "log"
    env = stub_command(
        tmp_path / "bin",
        "gh",
        f'echo called >> "{log}"\necho "branch has diverged" >&2\nexit 1\n',
    )
    env["GH_TOKEN"] = "fork-sync-app-token"
    result = task("sync-fork", "org/fork", "up/stream", "main", env=env)
    assert result.returncode != 0
    assert "branch has diverged" in result.stderr
    log.unlink()
    # No token: it fails before the tool is called, naming the variable.
    no_token = {**env, "GH_TOKEN": ""}
    result = task("sync-fork", "org/fork", "up/stream", "main", env=no_token)
    assert result.returncode != 0 and "GH_TOKEN" in result.stderr
    assert not log.exists()
    for arguments in ((), ("a", "b"), ("a", "", "c"), ("a", "b", "c", "d")):
        assert task("sync-fork", *arguments, env=env).returncode != 0
    assert not log.exists()


# ---- R195: the names of the Apps are checked by name, never by value --------------------------

APP_WORKFLOW = (
    "      app-id: ${{ vars.X_APP_ID }}\n      private-key: ${{ secrets.X_APP_PRIVATE_KEY }}\n"
    "      app-id: ${{ vars.Y_APP_ID }}\n      private-key: ${{ secrets.Y_APP_PRIVATE_KEY }}\n"
)


def app_names_env(tmp_path, variables, secrets, workflow=APP_WORKFLOW):
    """The workflows directory and a `gh` that answers the lists of names only, and
    fails when it is asked for anything that would carry a value."""
    workflows = tmp_path / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "w.yml").write_text(workflow)
    log = tmp_path / "log"
    env = stub_command(
        tmp_path / "bin",
        "gh",
        f'echo "$@" >> "{log}"\n'
        'case "$1 $2 $3 $4" in\n'
        f'  "variable list --org o") printf "%s\\n" {" ".join(variables)};;\n'
        f'  "secret list --org o") printf "%s\\n" {" ".join(secrets)};;\n'
        "  *) exit 1;;\n"
        "esac\n",
    )
    return {**env, "WORKFLOWS": str(workflows)}, log


def test_R195_app_names_are_checked_by_name_only(tmp_path):
    """Proves, with a stub of `gh` (the platform has no stand-in), that the command
    reads the names the workflows use, asks only for the field `name`, and succeeds
    when the organization holds them all."""
    env, log = app_names_env(
        tmp_path,
        ["X_APP_ID", "Y_APP_ID", "OTHER"],
        ["X_APP_PRIVATE_KEY", "Y_APP_PRIVATE_KEY"],
    )
    result = task("app-names", "o", env=env)
    assert result.returncode == 0, result.stderr
    asked = log.read_text().splitlines()
    assert len(asked) == 2 and all("--json name" in line for line in asked)
    assert "X_APP_PRIVATE_KEY" in result.stdout


def test_R195_app_names_are_checked_by_name_only_detects_violation(tmp_path):
    """A missing variable, a missing secret, a variable listed where the secret is
    wanted and a workflow that names no App each fail, naming what is missing."""
    env, _ = app_names_env(
        tmp_path / "a", ["X_APP_ID"], ["X_APP_PRIVATE_KEY", "Y_APP_PRIVATE_KEY"]
    )
    result = task("app-names", "o", env=env)
    assert result.returncode != 0 and "variable: Y_APP_ID" in result.stderr
    env, _ = app_names_env(
        tmp_path / "b", ["X_APP_ID", "Y_APP_ID"], ["X_APP_PRIVATE_KEY"]
    )
    result = task("app-names", "o", env=env)
    assert result.returncode != 0 and "secret: Y_APP_PRIVATE_KEY" in result.stderr
    env, _ = app_names_env(
        tmp_path / "c", ["X_APP_ID", "Y_APP_ID"], ["X_APP_ID", "Y_APP_ID"]
    )
    assert task("app-names", "o", env=env).returncode != 0
    env, _ = app_names_env(tmp_path / "d", ["X_APP_ID"], [], workflow="on: push\n")
    assert task("app-names", "o", env=env).returncode != 0
