"""The workflows that write do it with the token of an organization App. workflows-write-with-organization-apps.

The checks read the text of the workflows (a workflow cannot be run here); that the
Apps, their variables and secrets exist and that GitHub gives the token as written
is shown only by the first runs (`anima-branching-and-releasing`). Each check has a
`_detects_violation` companion that feeds it a deliberately wrong workflow.
"""

import re

import yaml
from sysml_model import ROOT
from workflow_tokens import app_token_faults

WORKFLOWS = ROOT / ".github" / "workflows"
PROMOTE = WORKFLOWS / "promote.yml"
SYNC_FORKS = WORKFLOWS / "sync-forks.yml"
PREPARE_RELEASE = WORKFLOWS / "prepare-release.yml"
APP_TOKEN = "${{ steps.app-token.outputs.token }}"
OWN_TOKEN = "${{ github.token }}"


def writes_promotion(step):
    run = str(step.get("run", ""))
    return "promote:green" in run or "promote:release" in run


def writes_fork(step):
    return "ci:sync-fork" in str(step.get("run", ""))


def writes_release_pull_request(step):
    return "release-please-action@" in str(step.get("uses", ""))


def app_token_workflow_faults(promote, sync, prepare, forks):
    """The three workflows against the rule: the promote App for main-green and the
    release, the fork-sync App for the forks (each token limited to its one fork),
    the bot App for the release pull request; and every fork in `forks` is synced."""
    found = app_token_faults(
        promote, "promote", "PROMOTE", writes_promotion, {"contents": "write"}
    )
    found += app_token_faults(
        sync,
        "sync",
        "FORK_SYNC",
        writes_fork,
        {"contents": "write", "workflows": "write"},
    )
    found += app_token_faults(
        prepare,
        "release-please",
        "BOT",
        writes_release_pull_request,
        {"contents": "write", "pull-requests": "write"},
    )
    matrix = yaml.safe_load(sync)["jobs"]["sync"]["strategy"]["matrix"]["include"]
    missing = set(forks) - {entry["fork"] for entry in matrix}
    if missing:
        found.append(f"forks not synced: {sorted(missing)}")
    for entry in matrix:
        if entry["repository"] != entry["fork"].split("/")[1]:
            found.append(f"{entry['fork']} is limited to {entry['repository']}")
    token = next(
        s
        for s in yaml.safe_load(sync)["jobs"]["sync"]["steps"]
        if "create-github-app-token" in str(s.get("uses"))
    )["with"]
    if (
        token.get("repositories") != "${{ matrix.repository }}"
        or token.get("owner") != "cocreiamo"
    ):
        found.append("the fork-sync token is not limited to the fork of the job")
    return found


def test_workflows_write_with_organization_app_tokens():
    """Proves, from the text of the three workflows, that each write is given the
    installation token of its App and no other credential, in the job that makes
    it. It does not prove that the Apps, the variables and the secrets exist or
    that GitHub accepts the token: the first runs do."""
    assert (
        app_token_workflow_faults(
            PROMOTE.read_text(),
            SYNC_FORKS.read_text(),
            PREPARE_RELEASE.read_text(),
            ["cocreiamo/anima-yarp", "cocreiamo/anima-postgres"],
        )
        == []
    )


def test_workflows_write_with_organization_app_tokens_detects_violation():
    promote, sync, prepare = (
        PROMOTE.read_text(),
        SYNC_FORKS.read_text(),
        PREPARE_RELEASE.read_text(),
    )
    forks = ["cocreiamo/anima-yarp"]

    def faults(promote=promote, sync=sync, prepare=prepare):
        return app_token_workflow_faults(promote, sync, prepare, forks)

    def once(text, old, new):
        assert text.count(old) >= 1, old
        return text.replace(old, new)

    assert faults() == []
    # main-green pushed, or the release created, with the workflow's own token.
    assert faults(promote=once(promote, APP_TOKEN, OWN_TOKEN))
    assert faults(
        promote=once(
            promote,
            "    permissions:\n      contents: read\n    env:\n      SHA:",
            "    permissions:\n      contents: write\n    env:\n      SHA:",
        )
    )
    assert faults(
        promote=once(
            promote,
            "    env:\n      SHA:",
            f"    env:\n      GH_TOKEN: {OWN_TOKEN}\n      SHA:",
        )
    )
    # A token that asks for more, from another App, or from an unpinned action.
    assert faults(
        promote=once(
            promote,
            "permission-contents: write",
            "permission-contents: write\n          permission-packages: write",
        )
    )
    assert faults(promote=once(promote, "vars.PROMOTE_APP_ID", "vars.OTHER_APP_ID"))
    assert faults(
        promote=once(
            promote,
            "create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510",
            "create-github-app-token@v3",
        )
    )
    # The App token made in a job that publishes.
    assert faults(
        promote=once(
            promote,
            "      - id: load\n",
            "      - id: app-token\n        uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510\n      - id: load\n",
        )
    )
    # The sync with a secret that was never set, with a token for every fork, or
    # without the fork of the reverse proxy.
    assert faults(sync=once(sync, APP_TOKEN, "${{ secrets.FORK_SYNC_TOKEN }}"))
    assert faults(
        sync=once(sync, "repositories: ${{ matrix.repository }}", "repositories: x")
    )
    assert faults(sync=once(sync, "cocreiamo/anima-yarp", "cocreiamo/anima-other"))
    # The release pull request opened with the workflow's own token.
    assert faults(prepare=once(prepare, APP_TOKEN, OWN_TOKEN))
    assert faults(
        prepare=once(
            prepare, "    permissions: {}", "    permissions:\n      contents: write"
        )
    )
    assert faults(prepare=re.sub(r"          token: .*\n", "", prepare))
