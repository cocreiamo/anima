"""The mirror of the base images. R160 to R163, R165 (GAP-060, TASK-43).

The workflow that copies every image of the register into the organization's
mirror, and the two commands it calls (`mise-tasks/ci/mirror-plan`, `mirror-copy`),
are read as text here; that the commands do what the text says is run for real
against a registry in `tests/ci/` (R172, R173, R165), and that the hosted registry
accepts the copy is shown only by the first run (`anima-branching-and-releasing`).
Each check is a function of its inputs and has a `_detects_violation` companion
that feeds it a deliberately wrong one. That the builds pull from the mirror is
R164, whose test is written when they do.
"""

import re

from repo_facts import load_toml
from sysml_model import ROOT

WORKFLOW = ROOT / ".github" / "workflows" / "mirror-base-images.yml"
COPY = ROOT / "mise-tasks" / "ci" / "mirror-copy"
PLAN = ROOT / "mise-tasks" / "ci" / "mirror-plan"
# The namespace of the organization's mirror: one package per upstream image,
# named after the register's entry.
NAMESPACE = "ghcr.io/cocreiamo/anima-mirror/"
COMMIT = re.compile(r"[0-9a-f]{40}")
# A registry of the sample references below, put together from parts so that this
# file holds no image reference of its own for the scan of R11 to find.
HOST = "registry" + ".example"
# An image reference with its digest, as a container file or a unit writes it.
PINNED_REFERENCE = re.compile(
    r"(?P<image>(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?/[a-z0-9._/-]+)"
    r"(?::[A-Za-z0-9._-]+)?@(?P<digest>sha256:[0-9a-f]{64})"
)


# ---- reading a workflow without a YAML library --------------------------------------------------


def jobs(text):
    """{job id: text of the job}, for a workflow written with two-space indentation."""
    found, current, in_jobs = {}, None, False
    for line in text.splitlines():
        if re.fullmatch(r"jobs:\s*", line):
            in_jobs = True
        elif in_jobs and re.match(r"\S", line):
            in_jobs = False
        elif in_jobs and (m := re.fullmatch(r"  ([\w-]+):\s*", line)):
            current = m.group(1)
            found[current] = ""
            continue
        if in_jobs and current:
            found[current] += line + "\n"
    return found


def job_permissions(job):
    m = re.search(r"^    permissions:\s*(\{\})?\n((?:      .*\n)*)", job, re.MULTILINE)
    if not m:
        return None
    return dict(re.findall(r"^\s+([\w-]+):\s*(\w+)", m.group(2), re.MULTILINE))


def triggers(text):
    m = re.search(r"^on:\n((?:  .*\n|\n)+)", text, re.MULTILINE)
    return set(re.findall(r"^  ([\w_]+):", m.group(1), re.MULTILINE)) if m else set()


def copy_commands(text):
    """The arguments of every `skopeo copy` the workflow runs."""
    return re.findall(r"^\s*sk copy (.*)$", text, re.MULTILINE)


def images_of(register):
    """The entries of the register that name an image: shipped components and the
    images that only tools and builds use."""
    return [
        c
        for c in register.get("component", []) + register.get("tool_image", [])
        if "image" in c
    ]


# ---- R160: no base image is left out of the mirror ---------------------------------------------


def register_faults(register):
    """Each image of the register has its own package in the mirror, and the copy
    tool is itself one of them, so that the workflow can take it from the register."""
    faults, seen = [], set()
    entries = images_of(register)
    for c in entries:
        name, mirror = c["name"], c.get("mirror")
        if mirror != NAMESPACE + name:
            faults.append(f"{name}: mirror is {mirror}, not {NAMESPACE}{name}")
        elif mirror in seen:
            faults.append(f"{name}: {mirror} is used twice")
        seen.add(mirror)
    if "skopeo" not in {c["name"] for c in entries}:
        faults.append("the copy tool is not in the register")
    return faults


def pulled_faults(register, files):
    """Each image that a container file or a unit under engine/ pulls and that the
    register does not hold, either under its upstream name or under its mirror's:
    the mirror would leave it out."""
    known = set()
    for c in images_of(register):
        known |= {(c["image"], c["digest"]), (c.get("mirror"), c["digest"])}
    faults = []
    for name, text in files.items():
        for m in PINNED_REFERENCE.finditer(text):
            if (m["image"], m["digest"]) not in known:
                faults.append(
                    f"{name}: {m['image']}@{m['digest']} is not in the register"
                )
    return faults


def list_faults(workflow, plan, copy, register):
    """The plan takes its list from the register, the workflow runs it for each
    entry, and none of the three holds a list of its own."""
    faults = []
    if "components.toml" not in plan:
        faults.append("the plan does not read the register")
    for section in ('register.get("component"', 'register.get("tool_image"'):
        if section not in plan:
            faults.append(f"the plan does not read {section}")
    if (
        '("mirror", "mirror")' not in plan
        or "fromJSON(needs.plan.outputs.images)" not in workflow
    ):
        faults.append("the copies are not driven by the register's mirror names")
    for c in images_of(register):
        for own in (c["image"], c["digest"], c["mirror"]):
            for where, text in (("workflow", workflow), ("plan", plan), ("copy", copy)):
                if own in text:
                    faults.append(f"{c['name']}: {own} is written in the {where}")
    return faults


def engine_files():
    """Container files and units under engine/ that name an image."""
    found = {}
    for path in sorted((ROOT / "engine").rglob("*")):
        if path.is_file() and (
            path.name.startswith("Containerfile")
            or path.suffix in {".container", ".image", ".build", ".pod"}
        ):
            found[str(path.relative_to(ROOT))] = path.read_text()
    return found


def test_R160_mirror_covers_every_base_image():
    """Proves that every image of the register has its package in the mirror, that
    every image the engine's container files pull is in the register, and that the
    workflow and its commands copy what the register lists, with no list of their
    own."""
    register = load_toml("components.toml")
    files = engine_files()
    assert files, "no container file found under engine/"
    assert images_of(register), "the register holds no image"
    assert register_faults(register) == []
    assert pulled_faults(register, files) == []
    assert (
        list_faults(WORKFLOW.read_text(), PLAN.read_text(), COPY.read_text(), register)
        == []
    )


def test_R160_mirror_covers_every_base_image_detects_violation():
    register = load_toml("components.toml")
    workflow, plan, copy = WORKFLOW.read_text(), PLAN.read_text(), COPY.read_text()
    first = images_of(register)[0]

    without = {"component": [], "tool_image": []}
    for key in ("component", "tool_image"):
        for c in register.get(key, []):
            without[key].append(
                {k: v for k, v in c.items() if k != "mirror"} if c is first else c
            )
    assert register_faults(without)
    wrong = {"component": [{**first, "mirror": "ghcr.io/elsewhere/x"}]}
    assert register_faults(wrong)
    twice = {
        "tool_image": [{**c, "mirror": NAMESPACE + "x"} for c in images_of(register)]
    }
    assert register_faults(twice)
    no_tool = {"component": [c for c in images_of(register) if c["name"] != "skopeo"]}
    assert register_faults(no_tool)

    extra = {"engine/x/Containerfile": f"FROM {HOST}/team/tool:1@sha256:{'0' * 64}\n"}
    assert pulled_faults(register, extra)
    held = f"FROM {first['image']}:1@{first['digest']}\n"
    assert not pulled_faults(register, {"engine/x/Containerfile": held})
    through_mirror = f"FROM {first['mirror']}@{first['digest']}\n"
    assert not pulled_faults(register, {"engine/x/Containerfile": through_mirror})

    assert list_faults(workflow, plan, copy, register) == []
    assert list_faults(workflow + f"# {first['image']}\n", plan, copy, register)
    assert list_faults(workflow, plan + f"# {first['mirror']}\n", copy, register)
    assert list_faults(workflow, plan, copy + f"# {first['digest']}\n", register)
    assert list_faults(workflow, plan.replace("tool_image", "other"), copy, register)
    assert list_faults(
        workflow, plan.replace("components.toml", "list.toml"), copy, register
    )
    assert list_faults(
        workflow.replace("fromJSON(needs.plan.outputs.images)", "x"),
        plan,
        copy,
        register,
    )
    assert list_faults(
        workflow, plan.replace('("mirror", "mirror")', ""), copy, register
    )


# ---- R161: the copy keeps the digest, and a copy that does not fails --------------------------


def digest_faults(workflow):
    """What would let the mirror hold something under a digest it was not given.
    `workflow` is the text of the copy command."""
    faults = []
    copies = copy_commands(workflow)
    if not copies:
        return ["the workflow copies nothing"]
    for arguments in copies:
        for flag in ("--all", "--preserve-digests"):
            if flag not in arguments.split():
                faults.append(f"a copy lacks {flag}")
        if re.search(r"--(format|override|dest-compress|remove-signatures)", arguments):
            faults.append("a copy converts or rewrites the image")
    if not re.search(r"inspect --raw .*\| sha256sum", workflow):
        faults.append("the digest is not read as the hash of the raw manifest")
    after = workflow.split("sk copy", 1)[-1]
    if not re.search(r'\[ "\$held" = "\$hex" \] \|\| die', after):
        faults.append("the copy is not read back and compared with the expected digest")
    for source in re.findall(r'^\s*put "([^"]*)"', workflow, re.MULTILINE):
        if "@sha256:" not in source:
            faults.append(f"a copy is taken from {source}, not by digest")
    for wanted in ('put "$IMAGE@sha256:$current"', 'put "$IMAGE@sha256:$pinned"'):
        if wanted not in workflow:
            faults.append(
                f"{wanted} is missing: the current and the pinned digest are both copied"
            )
    if re.search(r"continue-on-error|set \+e|\|\| true", workflow):
        faults.append("a failure can be ignored")
    return faults


def test_R161_mirror_preserves_digests():
    """Proves the text of the copy command: every copy is whole and keeps the digest,
    is read back and compared, and both the pinned digest and the one the upstream
    tag names are copied, by digest. That it does is run in R173."""
    assert digest_faults(COPY.read_text()) == []


def test_R161_mirror_preserves_digests_detects_violation():
    good = COPY.read_text()
    assert digest_faults(good) == []
    assert digest_faults(good.replace("--preserve-digests ", ""))
    assert digest_faults(good.replace("copy --all ", "copy "))
    assert digest_faults(good.replace("--retry-times 3", "--format oci"))
    assert digest_faults(good.replace('[ "$held" = "$hex" ] || die', "true"))
    assert digest_faults(good.replace("inspect --raw", "inspect"))
    assert digest_faults(good.replace('put "$IMAGE@sha256:$pinned"', "#"))
    assert digest_faults(
        good.replace('put "$IMAGE@sha256:$current"', 'put "$IMAGE:$TAG"')
    )
    assert digest_faults(good.replace("--retry-times 3", "|| true"))
    assert digest_faults("name: nothing\n")


# ---- R162: nothing in the mirror is deleted, moved or overwritten -----------------------------

TAGS = {'"sha256-$current"', '"$TAG-$today"', '"sha256-$pinned"'}


def immutability_faults(workflow):
    """What would let a copy delete, move or overwrite something the mirror holds."""
    faults = []
    if re.search(
        r"\bdelete\b|\bDELETE\b|--force|\brmi\b|\bsync\b|gh api|skopeo-delete", workflow
    ):
        faults.append("the workflow can delete or force")
    if "latest" in workflow:
        faults.append("a moving name is mentioned")
    copies = copy_commands(workflow)
    body = workflow.split("put() {", 1)[-1].split("\n}\n", 1)[0]
    if len(copies) != 1 or "sk copy" not in body:
        faults.append("the mirror is written outside the one function that guards it")
    else:
        before = body.split("sk copy", 1)[0]
        if 'manifest_hex "$MIRROR:$tag"' not in before or before.count("return 0") < 2:
            faults.append("a tag that exists is not left alone before the copy")
        if "sha256-*) die" not in before:
            faults.append("a digest tag that names another digest is not a fault")
    named = set(re.findall(r'^\s*put "[^"]*" ("[^"]*")', workflow, re.MULTILINE))
    if named != TAGS:
        faults.append(f"the mirror is tagged with {sorted(named)}, not {sorted(TAGS)}")
    return faults


def test_R162_mirror_never_deletes_or_moves_a_tag():
    """Proves the text of the copy command: one function writes the mirror, and only
    after it has found the tag absent; no command deletes. That a tag that exists is
    left as it is is run in R173."""
    assert immutability_faults(COPY.read_text()) == []


def test_R162_mirror_never_deletes_or_moves_a_tag_detects_violation():
    good = COPY.read_text()
    assert immutability_faults(good) == []
    assert immutability_faults(good + "      - run: skopeo delete docker://x\n")
    assert immutability_faults(good + "      - run: gh api -X DELETE x\n")
    assert immutability_faults(good.replace("--retry-times 3", "--force"))
    assert immutability_faults(good.replace('"$TAG-$today"', "latest"))
    assert immutability_faults(good.replace("        return 0\n", "", 1))
    assert immutability_faults(
        good.replace('manifest_hex "$MIRROR:$tag"', 'manifest_hex "$IMAGE"', 1)
    )
    assert immutability_faults(good.replace("sha256-*) die", "sha256-*) echo"))
    assert immutability_faults(good + "    sk copy --all --preserve-digests a b\n")
    assert immutability_faults(good.replace('"$TAG-$today"', '"$TAG"'))


# ---- R163: the job that writes packages holds nothing else ------------------------------------

CHECKOUT = "actions/checkout@"
TASK_RUNNER = "jdx/mise-action@"


def run_text(step):
    return step.split("run:", 1)[1] if "run:" in step else ""


def job_actions(job):
    return re.findall(r"^\s*(?:- )?uses:\s*(\S+)", job, re.MULTILINE)


def privilege_faults(workflow, copy):
    """What would give the mirror's credentials to code that is not the copy. The
    job that holds them runs the one command that copies, which a test runs for
    real (R173); it is given the repository to read and the task runner without a
    single tool installed, and nothing else."""
    faults = []
    if triggers(workflow) != {"schedule", "workflow_dispatch"}:
        faults.append(f"triggers are {sorted(triggers(workflow))}")
    if not re.search(r"^permissions: \{\}$", workflow, re.MULTILINE):
        faults.append("the workflow grants permissions by default")
    found = jobs(workflow)
    writers = [n for n, b in found.items() if "packages" in (job_permissions(b) or {})]
    mirror = found.get("mirror", "")
    if writers != ["mirror"] or job_permissions(mirror) != {
        "contents": "read",
        "packages": "write",
    }:
        faults.append(
            f"packages: write is held by {writers}, and by more than that job, "
            "or it holds more than contents: read"
        )
    else:
        actions = job_actions(mirror)
        if [a.split("@")[0] + "@" for a in actions] != [CHECKOUT, TASK_RUNNER]:
            faults.append(
                f"the job that writes packages runs {actions}, not the checkout and "
                "the task runner"
            )
        if not re.search(r"^\s+install: false\s*$", mirror, re.MULTILINE) or not (
            re.search(
                r'^\s+MISE_TASK_RUN_AUTO_INSTALL: "false"\s*$', mirror, re.MULTILINE
            )
        ):
            faults.append("a tool of the repository can be installed in that job")
        runs = [
            run_text(s).strip()
            for s in re.split(r"^      - ", mirror, flags=re.MULTILINE)
        ]
        runs = [r for r in runs if r]
        if runs != ["mise run ci:mirror-copy"]:
            faults.append(f"the job that writes packages runs {runs}")
    plan = job_permissions(found.get("plan", ""))
    if plan != {"contents": "read"}:
        faults.append(f"the planning job holds {plan}")
    for ref in re.findall(r"uses:\s*\S+@(\S+)", workflow):
        if not COMMIT.fullmatch(ref):
            faults.append(f"an action is pinned by {ref}, not by a commit")
    if workflow.count("persist-credentials: false") != workflow.count(CHECKOUT):
        faults.append("a checkout keeps its credentials")
    if "--password-stdin" not in copy or re.search(
        r"--(password|creds|dest-creds|src-creds)\b(?!-)",
        copy.replace("--password-stdin", ""),
    ):
        faults.append("the token is not passed on standard input")
    if ":/auth.json:ro" not in copy:
        faults.append("the credentials file is not mounted read only")
    if (
        re.search(r"@sha256:[0-9a-f]{64}", workflow + copy)
        or "needs.plan.outputs.skopeo" not in workflow
        or '"$SKOPEO"' not in copy
    ):
        faults.append("the copy tool is not taken from the register by digest")
    for step in re.findall(r"run: (.*)", workflow):
        if "${{" in step:
            faults.append("an expression is written inside a script")
    return faults


def test_R163_mirror_has_least_privilege():
    """Proves the text of the workflow and of the copy command: only the mirror job
    writes packages, it runs two pinned actions (the checkout and the task runner,
    which installs no tool) and the one command that copies, the token is read from
    standard input, and the triggers cannot be a pull request. It does not prove
    that the registry or the organization grants no more."""
    assert privilege_faults(WORKFLOW.read_text(), COPY.read_text()) == []


def test_R163_mirror_has_least_privilege_detects_violation():
    good, copy = WORKFLOW.read_text(), COPY.read_text()
    assert privilege_faults(good, copy) == []
    assert privilege_faults(
        good.replace("  workflow_dispatch:", "  pull_request:\n  workflow_dispatch:"),
        copy,
    )
    assert privilege_faults(
        good.replace("permissions: {}", "permissions: read-all", 1), copy
    )
    assert privilege_faults(
        good.replace(
            "      contents: read\n", "      contents: read\n      packages: write\n", 1
        ),
        copy,
    )
    assert privilege_faults(
        good.replace(
            "      packages: write\n", "      packages: write\n      contents: write\n"
        ),
        copy,
    )
    assert privilege_faults(good.replace("      packages: write\n", ""), copy)
    # Another action, or another command, in the job that holds the token.
    assert privilege_faults(
        good.replace(
            "      - name: Copy",
            "      - uses: actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9 # v6.1.0\n"
            "      - name: Copy",
        ),
        copy,
    )
    assert privilege_faults(
        good.replace("run: mise run ci:mirror-copy", "run: echo $REGISTRY_TOKEN"), copy
    )
    assert privilege_faults(good.replace("          install: false\n", ""), copy)
    assert privilege_faults(
        good.replace('      MISE_TASK_RUN_AUTO_INSTALL: "false"\n', ""), copy
    )
    assert privilege_faults(
        good.replace("@3d3c42e5aac5ba805825da76410c181273ba90b1", "@v7"), copy
    )
    assert privilege_faults(
        good.replace("persist-credentials: false", "persist-credentials: true", 1), copy
    )
    assert privilege_faults(good, copy.replace("--password-stdin", "--password x"))
    assert privilege_faults(
        good.replace("run: mise run ci:mirror-copy", "run: x ${{ github.token }}"), copy
    )
    assert privilege_faults(good, copy.replace(":/auth.json:ro", ":/auth.json"))
    assert privilege_faults(
        good, copy.replace('"$SKOPEO"', "quay.io/skopeo/stable@sha256:" + "0" * 64, 1)
    )
    assert privilege_faults(good.replace("needs.plan.outputs.skopeo", "x"), copy)


# ---- R165: a signed image is mirrored with its signatures, and the choice is explicit ---------

# The signature attachments of an upstream image are read and written only where the
# configuration of the copy tool enables them: for the upstream scope, which the
# tool's policy may require signed, and for the mirror's.
SCOPES = ("$IMAGE", "$MIRROR")


def signature_faults(workflow):
    """What would make the copy of an image that its upstream signed fail, or drop
    its signatures without saying so."""
    faults = []
    if "--registries.d /rd" not in workflow or ":/rd:ro" not in workflow:
        faults.append("the copy tool has no registries configuration, read only")
    for scope in SCOPES:
        enabled = re.search(
            rf"^\s*{re.escape(scope)}:\n\s*use-sigstore-attachments: true$",
            workflow,
            re.MULTILINE,
        )
        if not enabled:
            faults.append(f"signature attachments are not enabled for {scope}")
    if "--remove-signatures" in workflow:
        faults.append("signatures are dropped")
    return faults


def test_R165_mirror_keeps_the_signatures_of_signed_images():
    """Proves the text of the copy command: the copy tool is given a configuration
    that enables signature attachments for the upstream scope and the mirror's, and
    the copy does not strip them. A signed image failed to copy without it on the
    first run, 2026-11-28; that the command keeps them is run in R165
    (`tests/ci/`)."""
    assert signature_faults(COPY.read_text()) == []


def test_R165_mirror_keeps_the_signatures_of_signed_images_detects_violation():
    good = COPY.read_text()
    assert signature_faults(good) == []
    assert signature_faults(good.replace("--registries.d /rd", ""))
    assert signature_faults(good.replace(":/rd:ro", ":/rd"))
    assert signature_faults(good.replace("$IMAGE:\n", "$OTHER:\n"))
    assert signature_faults(good.replace("$MIRROR:\n", "$OTHER:\n"))
    assert signature_faults(good.replace("use-sigstore-attachments: true", "x: 1"))
    assert signature_faults(good + "# sk copy --remove-signatures\n")
