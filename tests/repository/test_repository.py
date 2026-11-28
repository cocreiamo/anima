"""Verifications that need only the repository, not a running system.

Each test is named after the verification it implements in model/anima.sysml.
The logic of a check is a function of its inputs, so that its companion test
(`<name>_detects_violation`, R56) can feed it a deliberately wrong input.
"""

import json
import re
import subprocess

from repo_facts import (
    components,
    load_toml,
    repository_files,
    submodule_commits,
    tool_images,
)
from sysml_model import ROOT

COMMIT = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"sha256:[0-9a-f]{64}")
EXACT_VERSION = re.compile(r"\d+\.\d+\.\d+")
# Submodules that hold the organization's shared repository, not a component.
ORGANIZATION = {"shared"}

# Registry of the sample references in the companion tests. The samples are put
# together from parts, so that this file holds no image reference of its own for
# the scan below to find.
SAMPLE_HOST = "registry.example"
SAMPLE_DIGEST = "sha256:" + "0" * 64


def read_texts(paths):
    """Texts of the files, by path relative to the root; binary files and the
    bytecode caches are left out."""
    texts = {}
    for path in paths:
        if "__pycache__" in path.parts or not path.is_file():
            continue
        try:
            texts[str(path.relative_to(ROOT))] = path.read_text()
        except UnicodeDecodeError:
            continue
    return texts


def files_under(*names):
    """Every file under the given directories or files of the root, outside
    third_party/."""
    found = []
    for name in names:
        path = ROOT / name
        found += [path] if path.is_file() else sorted(path.rglob("*"))
    return found


# ---- R11: every dependency pinned ------------------------------------------


def pinning_faults(
    components, tool_images, submodule_pins, tools, workflows, devcontainer
):
    """What is not pinned: components and tool images by commit or digest, tools
    by exact version, workflow actions by commit, the development container by
    digest."""
    faults = []
    declared = set()
    for c in components + tool_images:
        name = c.get("name")
        if not c.get("version") or c["version"] == "latest":
            faults.append(f"{name}: no exact version")
        if "submodule" in c:
            if not COMMIT.fullmatch(c.get("commit", "")):
                faults.append(f"{name}: not pinned by a full commit")
            elif submodule_pins.get(c["submodule"]) != c["commit"]:
                faults.append(f"{name}: components.toml and the submodule disagree")
            declared.add(c["submodule"])
        elif "commit" in c and "image" not in c:
            # A fork that is not yet a submodule: pinned by its release commit.
            if not COMMIT.fullmatch(c["commit"]):
                faults.append(f"{name}: not pinned by a full commit")
        elif not DIGEST.fullmatch(c.get("digest", "")):
            faults.append(f"{name}: image not pinned by digest")
    # The submodules of the organization (its shared repository) are not
    # components: they must be pinned by a full commit, which the index makes so.
    fork_pins = {p: c for p, c in submodule_pins.items() if p not in ORGANIZATION}
    faults += [
        f"{path}: not pinned by a full commit"
        for path, commit in submodule_pins.items()
        if path in ORGANIZATION and not COMMIT.fullmatch(commit)
    ]
    if declared != set(fork_pins):
        faults.append("every submodule must be a declared component")
    faults += [
        f"{path} is not under third_party/"
        for path in fork_pins
        if not path.startswith("third_party/")
    ]

    for tool, version in tools.items():
        if not EXACT_VERSION.search(str(version)):
            faults.append(f"tool {tool} = {version}: not an exact version")

    for name, text in workflows.items():
        for ref in re.findall(r"uses:\s*\S+@(\S+)", text):
            if not COMMIT.fullmatch(ref):
                faults.append(f"{name}: action pinned by {ref}, not by a commit")

    if not DIGEST.search(devcontainer.get("image", "")):
        faults.append("development container image has no digest")
    for feature, options in devcontainer.get("features", {}).items():
        if not DIGEST.search(feature):
            faults.append(f"development container feature {feature} has no digest")
        if not EXACT_VERSION.search(options.get("version", "")):
            faults.append(f"development container feature {feature}: no exact version")
    return faults


# The word that names the tool, as a command: at the start of a word and followed
# by a space (or the compose form), so that `docker/metadata-action`,
# `docker-library/postgres` and `docker:pinDigests` are not commands.
# `--format docker` names an image format that podman writes; it is not a command.
DOCKER_COMMAND = re.compile(
    r"(?<![\w./:-])(?<!--format )" + "dock" + r"er(?:-compose)?(?=[ \t])"
)


def docker_invocations(files):
    """Lines that invoke Docker, in the given files (by path, with their text)."""
    return [
        f"{name}:{number}"
        for name, text in files.items()
        for number, line in enumerate(text.splitlines(), 1)
        if DOCKER_COMMAND.search(line)
    ]


# A container image can be named after a key (`image:`, `image =`, `"image":`,
# `Image=`, `FROM`), or anywhere as a reference that starts with a registry host.
KEYED_IMAGE = re.compile(
    r"""^[ \t]*(?:-[ \t]*)?(?:(?i:"?image"?)[ \t]*[:=][ \t]*|FROM[ \t]+(?:--\S+[ \t]+)?)"""
    r"""["']?(?P<ref>[^\s"'#,]+)""",
    re.MULTILINE,
)
QUALIFIED_IMAGE = re.compile(
    r"(?<![\w./:@{$-])"
    r"(?P<ref>(?:[a-z0-9-]+\.)+[a-z]{2,}(?::\d+)?/[a-z0-9._/-]+"
    r"(?::[A-Za-z0-9._-]+(?:@sha256:[0-9a-f]+)?|@sha256:[0-9a-f]+))"
)
# Written outside a key, a reference is recognized only when it has a tag or a
# digest: without one it cannot be told from a Go package path or a web address.
# A reference with neither, outside a key, is not seen by this scan.


def image_references(text):
    """Container image references in a text, as written."""
    stages = set(
        re.findall(r"^FROM\s.*\sAS\s+(\S+)", text, re.IGNORECASE | re.MULTILINE)
    )
    refs = {m["ref"] for m in KEYED_IMAGE.finditer(text)}
    refs |= {m["ref"] for m in QUALIFIED_IMAGE.finditer(text)}
    # `scratch`, a stage of a multi-stage build, a variable, a reference to
    # another Quadlet unit (`name.image`, `name.build`) and a local file
    # (`oci-archive:`, `oci:`, `dir:`) are not registry images.
    return sorted(
        r
        for r in refs
        if r.lower() != "scratch"
        and not r.startswith(("oci-archive:", "oci:", "dir:"))
        and r not in stages
        and not re.search(r"[${]", r)
        and not r.endswith((".image", ".build"))
    )


def image_reference_faults(files):
    """Image references that carry no digest: a tag alone, or no tag at all."""
    return [
        f"{name}: {ref}"
        for name, text in files.items()
        for ref in image_references(text)
        if not re.search(r"@sha256:[0-9a-f]{64}$", ref)
    ]


def registered_images(shipped, tools_and_tests):
    """components.toml as the text a scan reads: one line per image, with its
    digest appended, as an image reference is written everywhere else."""
    return "".join(
        f'image = "{c["image"]}@{c.get("digest", "")}"\n'
        if c.get("digest")
        else f'image = "{c["image"]}"\n'
        for c in shipped + tools_and_tests
        if "image" in c
    )


def image_scan_files():
    """Every file outside third_party/ that can reference an image: workflows
    and the other files of .github/, the development container, the tests, the
    tasks, the engine's units and the configuration; components.toml is read
    as the registered images."""
    paths = files_under(
        ".github",
        ".devcontainer",
        "tests",
        "mise-tasks",
        "mise.toml",
        "engine",
        "config",
    )
    files = read_texts(paths)
    files["components.toml"] = registered_images(components(), tool_images())
    return files


def test_R11_every_dependency_pinned():
    workflows = read_texts(sorted((ROOT / ".github" / "workflows").glob("*.yml")))
    devcontainer = json.loads(
        (ROOT / ".devcontainer" / "devcontainer.json").read_text()
    )
    faults = pinning_faults(
        components(),
        tool_images(),
        submodule_commits(),
        load_toml("mise.toml")["tools"],
        workflows,
        devcontainer,
    )
    scanned = image_scan_files()
    assert image_references(scanned["components.toml"]), "no image is registered"
    assert image_references(json.dumps(devcontainer)), "the scan finds no image"
    faults += image_reference_faults(scanned)

    # No Docker: no file that runs things invokes it (`anima-repository-conventions`, ADR 0005).
    runs = files_under("mise.toml", "mise-tasks", ".github/workflows", "tests")
    faults += [f"Docker invoked at {w}" for w in docker_invocations(read_texts(runs))]
    assert not faults, faults


def container_config(image_ref, features):
    """A development container file as pinning_faults() reads it. The key is put
    together so that no line of this file starts like an image setting."""
    return {"im" + "age": image_ref, "features": features}


def _pinned_inputs():
    """A set of inputs for pinning_faults() that has no fault."""
    commit = "a" * 40
    source = {"name": "src", "version": "1.2.3", "submodule": "third_party/src"}
    source["commit"] = commit
    registered = {"name": "img", "version": "1.2.3", "digest": SAMPLE_DIGEST}
    registered["im" + "age"] = "x"
    feature = f"feature@{SAMPLE_DIGEST}"
    return {
        "components": [source, registered],
        "tool_images": [],
        "submodule_pins": {"third_party/src": commit},
        "tools": {"tool": "1.2.3"},
        "workflows": {"w.yml": f"uses: actions/checkout@{commit}"},
        "devcontainer": container_config(
            f"base:1@{SAMPLE_DIGEST}", {feature: {"version": "1.2.3"}}
        ),
    }


def test_R11_every_dependency_pinned_detects_violation():
    assert pinning_faults(**_pinned_inputs()) == []

    def faults(**change):
        return pinning_faults(**{**_pinned_inputs(), **change})

    good = _pinned_inputs()
    registered = good["components"][1]
    unpinned = {**registered, "digest": "sha256:short"}
    assert faults(components=[good["components"][0], unpinned])
    assert faults(components=[{**registered, "version": "latest"}])
    assert faults(tool_images=[unpinned])
    assert faults(submodule_pins={"third_party/src": "b" * 40})
    other = {**good["submodule_pins"], "third_party/other": "c" * 40}
    assert faults(submodule_pins=other)
    release = {"name": "fork", "version": "1.0.0", "commit": "d" * 40}
    assert faults(components=[release], submodule_pins={}) == []
    assert faults(components=[{**release, "commit": "abc"}], submodule_pins={})
    assert faults(components=[{"name": "bare", "version": "1.0.0"}], submodule_pins={})
    assert faults(tools={"tool": "latest"})
    assert faults(workflows={"w.yml": "uses: actions/checkout@v4"})
    # The reusable workflows of the organization are pinned like any action.
    shared = "uses: cocreiamo/.github/.github/workflows/check.yml@"
    assert faults(workflows={"w.yml": shared + "main"})
    assert faults(workflows={"w.yml": shared + "0b4136b"})
    assert faults(workflows={"w.yml": shared + "a" * 40 + " # shared"}) == []
    # The shared repository is a submodule that is not a component.
    organization = {**good["submodule_pins"], "shared": "d" * 40}
    assert faults(submodule_pins=organization) == []
    assert faults(submodule_pins={**organization, "shared": "short"})
    assert faults(devcontainer=container_config("base:1", {}))
    assert faults(devcontainer=container_config("base:1", {"f": {"version": "1.2.3"}}))

    command = "dock" + "er run x"
    assert docker_invocations({"t.toml": f"run = '{command}'\n"}) == ["t.toml:1"]
    assert docker_invocations({"t.toml": "uses: docker/metadata-action\n"}) == []
    image_format = "podman build --format " + "dock" + "er --tag x .\n"
    assert docker_invocations({"build": image_format}) == []

    host = SAMPLE_HOST
    tagged = f"image: {host}/team/tool:1.0\n"
    untagged = f"image: {host}/team/tool\n"
    short = "image: postgres:18\n"
    digested = f"image: {host}/team/tool:1.0@{SAMPLE_DIGEST}\n"
    assert image_reference_faults({"w.yml": tagged})
    assert image_reference_faults({"w.yml": untagged})
    assert image_reference_faults({"w.yml": short})
    assert image_reference_faults({"c.txt": f"pull {host}/team/tool:1.0 now\n"})
    assert image_reference_faults({"Containerfile": "FROM " + "base:1\n"})
    assert image_reference_faults({"u.container": "Image=" + f"{host}/a/b:1\n"})
    assert image_reference_faults({"d.json": '{"image": "' + f"{host}/a/b:1" + '"}'})
    unpinned_entry = {"im" + "age": f"{host}/a/b"}
    assert image_reference_faults(
        {"components.toml": registered_images([unpinned_entry], [])}
    )
    assert image_reference_faults({"w.yml": digested}) == []
    assert image_reference_faults({"Containerfile": "FROM scratch\n"}) == []
    assert image_reference_faults({"a.container": "Image=db.image\n"}) == []
    assert (
        image_reference_faults({"c": "-X example.test/org/repo/v2/pkg.Version\n"}) == []
    )
    local = "Image=oci-archive:/usr/lib/x.tar\n"
    assert image_reference_faults({"a.image": local}) == []


# ---- R17: component licences allowed ---------------------------------------


def disallowed_licenses(components, allowed):
    return [
        f"{c['name']}: {c.get('license')}"
        for c in components
        if c.get("license") not in allowed
    ]


def test_R17_component_licenses_allowed():
    allowed = set(load_toml("components.toml")["policy"]["allowed_licenses"])
    assert not disallowed_licenses(components(), allowed)


def test_R17_component_licenses_allowed_detects_violation():
    allowed = {"MIT"}
    assert disallowed_licenses([{"name": "a", "license": "MIT"}], allowed) == []
    assert disallowed_licenses([{"name": "a", "license": "GPL-3.0-only"}], allowed)
    assert disallowed_licenses([{"name": "a"}], allowed)


# ---- R25: every gap registered ----------------------------------------------

GAP_FIELDS = {
    "id",
    "component",
    "version",
    "summary",
    "impact",
    "workaround",
    "upstream",
    "resolved_when",
    "status",
}


def gap_register_faults(gaps, mentions):
    """Faults of the register of gaps. `mentions` maps each file of the
    repository to the gap ids written in it."""
    faults = []
    ids = [g.get("id") for g in gaps]
    if ids != [f"GAP-{n:03d}" for n in range(1, len(ids) + 1)]:
        faults.append("ids are not unique and sequential")
    for g in gaps:
        if set(g) != GAP_FIELDS:
            faults.append(f"{g.get('id')}: fields differ from the register's")
        elif not all(g[f] for f in GAP_FIELDS):
            faults.append(f"{g['id']}: an empty field")
        if g.get("status") not in {"open", "closed"}:
            faults.append(f"{g.get('id')}: status is not open or closed")

    # Every GAP-nnn written in a file is a registered entry.
    for name, found in mentions.items():
        faults += [
            f"{name} names {i}, not registered" for i in sorted(found - set(ids))
        ]

    # A workaround that is a repository path names its entry.
    for g in gaps:
        workaround = g.get("workaround", "none")
        if workaround == "none" or " " in workaround:
            continue
        if workaround not in mentions:
            faults.append(
                f"{g.get('id')}: {workaround} is not a file of the repository"
            )
        elif g.get("id") not in mentions[workaround]:
            faults.append(f"{workaround} does not name {g.get('id')}")
    return faults


def gap_mentions():
    pattern = re.compile(r"GAP-\d{3}")
    mentions = {}
    for name, path in repository_files():
        try:
            mentions[name] = set(pattern.findall(path.read_text()))
        except UnicodeDecodeError:
            continue
    return mentions


def test_R25_every_gap_registered():
    assert not gap_register_faults(load_toml("gaps.toml")["gap"], gap_mentions())


def test_R25_every_gap_registered_detects_violation():
    gap = {f: "x" for f in GAP_FIELDS}
    gap |= {"id": "GAP-001", "status": "open", "workaround": "none"}
    mentions = {"a.py": {"GAP-001"}}
    assert gap_register_faults([gap], mentions) == []
    assert gap_register_faults([gap, {**gap, "id": "GAP-001"}], mentions)
    assert gap_register_faults([{**gap, "id": "GAP-002"}], mentions)
    assert gap_register_faults(
        [{k: v for k, v in gap.items() if k != "impact"}], mentions
    )
    assert gap_register_faults([{**gap, "summary": ""}], mentions)
    assert gap_register_faults([{**gap, "status": "maybe"}], mentions)
    assert gap_register_faults([gap], {"a.py": {"GAP-009"}})
    assert gap_register_faults([{**gap, "workaround": "missing.py"}], mentions)
    assert gap_register_faults([{**gap, "workaround": "b.py"}], {"b.py": set()})
    assert gap_register_faults([{**gap, "workaround": "a.py"}], mentions) == []


# ---- R18: every file licensed ----------------------------------------------


def reuse_lint(root):
    return subprocess.run(
        ["reuse", "--root", str(root), "lint"],
        check=False,
        capture_output=True,
        text=True,
    )


def test_R18_every_file_licensed():
    result = reuse_lint(ROOT)
    assert result.returncode == 0, result.stdout + result.stderr


def test_R18_every_file_licensed_detects_violation(tmp_path):
    """The smallest honest negative: a directory with one file that carries no
    copyright and licence information."""
    (tmp_path / "unlicensed.txt").write_text("no copyright, no licence\n")
    assert reuse_lint(tmp_path).returncode != 0


# ---- R140: the contributor agreement links its privacy notice --------------


def privacy_link_faults(root):
    notice = root / "PRIVACY.md"
    if not notice.is_file() or not notice.read_text().strip():
        return ["PRIVACY.md is missing or empty"]
    return [
        f"{name} does not link PRIVACY.md"
        for name in ("CLA.md", "CONTRIBUTING.md")
        if not (root / name).is_file() or "PRIVACY.md" not in (root / name).read_text()
    ]


def test_R140_contributor_agreement_links_privacy_notice():
    assert not privacy_link_faults(ROOT)


def test_R140_contributor_agreement_links_privacy_notice_detects_violation(tmp_path):
    (tmp_path / "CLA.md").write_text("terms\n")
    (tmp_path / "CONTRIBUTING.md").write_text("[notice](PRIVACY.md)\n")
    assert privacy_link_faults(tmp_path) == ["PRIVACY.md is missing or empty"]
    (tmp_path / "PRIVACY.md").write_text("notice\n")
    assert privacy_link_faults(tmp_path) == ["CLA.md does not link PRIVACY.md"]
    (tmp_path / "CLA.md").write_text("see PRIVACY.md\n")
    assert privacy_link_faults(tmp_path) == []


# ---- R45: contractions register ---------------------------------------------

CONTRACTION_FIELDS = {"what", "reason", "deprecated_in", "removed_in"}


def contraction_faults(entries):
    faults = []
    for entry in entries:
        if set(entry) != CONTRACTION_FIELDS:
            faults.append(f"{entry}: fields differ from the register's")
            continue
        if not all(isinstance(entry[f], str) and entry[f] for f in CONTRACTION_FIELDS):
            faults.append(f"{entry}: an empty field")
            continue
        for version in ("deprecated_in", "removed_in"):
            if not EXACT_VERSION.fullmatch(entry[version]):
                faults.append(f"{entry}: {version} is not a version")
        # Only something a released version already deprecated can be removed.
        if entry["deprecated_in"] == entry["removed_in"]:
            faults.append(f"{entry}: removed in the version that deprecates it")
    whats = [entry.get("what") for entry in entries]
    if len(whats) != len(set(whats)):
        faults.append("a contraction is declared once")
    return faults


def test_R45_contractions_register_well_formed():
    assert not contraction_faults(load_toml("contractions.toml")["contraction"])


# ---- publicUrlDeclaredOnce: the public URL is declared once ---------------------------------------

PUBLIC_URL_FILE = "engine/access/public-url.env"
PUBLIC_URL_SURFACE = ("engine/", "config/", "mise-tasks/", "tests/system/")


def declared_public_url(text):
    """The public URL a declaration file states, or None."""
    for line in text.splitlines():
        if line.startswith("ANIMA_IDENTITY_PROVIDER_URL="):
            return line.split("=", 1)[1].strip()
    return None


def public_url_repeats(texts, declaration=PUBLIC_URL_FILE):
    """The files, other than the declaration, whose text holds the declared URL."""
    url = declared_public_url(texts[declaration])
    if not url:
        return [f"{declaration}: declares no public URL"]
    return [
        name
        for name, text in sorted(texts.items())
        if name != declaration and url in text
    ]


def test_public_url_declared_once():
    paths = [
        path
        for name, path in repository_files()
        if name.startswith(PUBLIC_URL_SURFACE) or name == PUBLIC_URL_FILE
    ]
    repeats = public_url_repeats(read_texts(paths))
    assert not repeats, repeats


def test_public_url_declared_once_detects_violation():
    declaration = "ANIMA_IDENTITY_PROVIDER_URL=https://idp.example:8443\n"
    texts = {PUBLIC_URL_FILE: declaration, "a": "no url here", "b": "x"}
    assert public_url_repeats(texts) == []
    repeated = {**texts, "c": "see https://idp.example:8443/realms"}
    assert public_url_repeats(repeated) == ["c"]
    assert public_url_repeats({PUBLIC_URL_FILE: "# nothing\n"})


def test_R45_contractions_register_well_formed_detects_violation():
    entry = {
        "what": "a",
        "reason": "r",
        "deprecated_in": "1.0.0",
        "removed_in": "2.0.0",
    }
    assert contraction_faults([entry]) == []
    assert contraction_faults([{k: v for k, v in entry.items() if k != "reason"}])
    assert contraction_faults([{**entry, "reason": ""}])
    assert contraction_faults([{**entry, "removed_in": "soon"}])
    assert contraction_faults([{**entry, "removed_in": "1.0.0"}])
    assert contraction_faults([entry, entry])
