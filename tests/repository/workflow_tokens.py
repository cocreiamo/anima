"""What a workflow may write with: the installation token of an organization App.

Used by the tests of the requirements whose workflows write to the platform: the
promotion (R24), the sync of the forks (R177) and the preparation of the release
(R155). A workflow cannot be run here, so this reads its text; that GitHub gives
the token as written is shown only by the first run (`anima-branching-and-releasing`).

The rule: the step that writes gets the token of the App named for its capability,
made by the pinned token action in the same job, with exactly the permissions the
write needs; the workflow's own token is never what writes, and no other job of the
workflow makes a token.
"""

import re

import yaml

TOKEN_ACTION = "actions/create-github-app-token@"
PINNED = re.compile(r"^actions/create-github-app-token@[0-9a-f]{40}$")
OWN_TOKEN = re.compile(r"github\.token|GITHUB_TOKEN")


def app_token_faults(text, job_id, app, consumer, grants, jobs_allowed=None):
    """What lets a write in `job_id` use another credential than the token of App
    `app` (the prefix of its organization variable and secret, for example
    `PROMOTE`), or lets that token be broader than `grants`.

    `consumer(step)` says which steps write; each of them must be given the token
    in `env: GH_TOKEN` (a command) or `with: token` (an action)."""
    faults = []
    workflow = yaml.safe_load(text)
    all_jobs = workflow.get("jobs", {})
    allowed = set(jobs_allowed or [job_id])
    for name, other in all_jobs.items():
        made = [
            s for s in other.get("steps", []) if TOKEN_ACTION in str(s.get("uses", ""))
        ]
        if made and name not in allowed:
            faults.append(f"{name} makes an App token and is not meant to")
    job = all_jobs.get(job_id)
    if job is None:
        return [f"no job {job_id}"]
    steps = job.get("steps", [])
    makers = [
        (i, s) for i, s in enumerate(steps) if TOKEN_ACTION in str(s.get("uses", ""))
    ]
    if len(makers) != 1:
        return faults + [f"{job_id} makes {len(makers)} App tokens, not one"]
    index, maker = makers[0]
    if not PINNED.match(str(maker["uses"]).split(" ")[0]):
        faults.append("the token action is not pinned by a full commit")
    reference = f"${{{{ steps.{maker.get('id', '')}.outputs.token }}}}"
    if not maker.get("id"):
        faults.append("the token step has no id")
    given = maker.get("with", {})
    if given.get("app-id") != f"${{{{ vars.{app}_APP_ID }}}}":
        faults.append(f"the App id is not the variable {app}_APP_ID")
    if given.get("private-key") != f"${{{{ secrets.{app}_APP_PRIVATE_KEY }}}}":
        faults.append(f"the private key is not the secret {app}_APP_PRIVATE_KEY")
    asked = {
        k.removeprefix("permission-"): v
        for k, v in given.items()
        if k.startswith("permission-")
    }
    if asked != grants:
        faults.append(f"the token asks for {asked}, not {grants}")
    if "GH_TOKEN" in job.get("env", {}):
        faults.append("the job gives every step a token in its environment")
    if "write" in (job.get("permissions") or {}).values():
        faults.append("the workflow's own token can write in this job")
    writers = [(i, s) for i, s in enumerate(steps) if consumer(s)]
    if not writers:
        faults.append("no step writes")
    for i, step in writers:
        carried = {**step.get("env", {}), **step.get("with", {})}
        if i < index:
            faults.append("a step writes before the token is made")
        if reference not in (carried.get("GH_TOKEN"), carried.get("token")):
            faults.append("a step that writes is not given the App token")
        if OWN_TOKEN.search(yaml.safe_dump(step)):
            faults.append("a step that writes names the workflow's own token")
    return faults
