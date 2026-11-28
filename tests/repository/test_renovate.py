"""The Renovate configuration must find what it is meant to update (a pattern
that matches nothing updates nothing, silently) and must not offer an update
from the wrong place: the images of components.toml (R70), the configurator's
version constraint, which follows the releases of the configurator and not those
of another tool (R120), the task runner's version, pinned in several places
(R121), and the build contexts of the container files, which are not images
(R122).
"""

import json
import re

from repo_facts import components, tool_images
from sysml_model import ROOT


def renovate_config():
    return json.loads((ROOT / ".github" / "renovate.json").read_text())


def python_pattern(pattern):
    """A Renovate pattern as a Python one (Renovate writes named groups
    `(?<name>...)`)."""
    return re.compile(re.sub(r"\(\?<([A-Za-z])", r"(?P<\1", pattern))


def manager_pattern():
    """The first match string of the first custom manager of
    .github/renovate.json, as a Python pattern."""
    return python_pattern(renovate_config()["customManagers"][0]["matchStrings"][0])


def unmatched_images(pattern, text, expected):
    """Images that are in `expected` and that the pattern does not find, and
    those found with something else than their digest."""
    found = {m["depName"] for m in pattern.finditer(text)}
    return sorted(set(expected) - found)


def registered_image_names():
    return [c["image"] for c in components() + tool_images() if "image" in c]


def test_R70_update_bot_finds_every_image():
    expected = registered_image_names()
    assert expected, "no image in components.toml"
    text = (ROOT / "components.toml").read_text()
    assert not unmatched_images(manager_pattern(), text, expected)


def entry(image_line):
    return (
        '[[component]]\nname = "x"\nversion = "1.0.0"\nlicense = "MIT"\n'
        f"{image_line}\ndigest = " + '"sha256:' + "0" * 64 + '"\n'
    )


def test_R70_update_bot_finds_every_image_detects_violation():
    pattern = manager_pattern()
    name = "registry" + ".example/a/b"  # put together: no reference in this file
    spaced = "im" + f'age = "{name}"'
    unspaced = "im" + f'age ="{name}"'
    assert unmatched_images(pattern, entry(spaced), [name]) == []
    assert unmatched_images(pattern, entry(unspaced), [name])
    assert unmatched_images(pattern, "", [name])


# ---- the managers that read other files than components.toml -----------------


def file_matches(manager, path):
    """Whether a custom manager reads the file `path` (patterns of the form
    `/regular expression/`, the only form this repository writes)."""
    patterns = manager["managerFilePatterns"]
    assert all(p.startswith("/") and p.endswith("/") for p in patterns), patterns
    return any(re.search(p[1:-1], path) for p in patterns)


def manager_for(config, dep_name):
    return [
        m
        for m in config.get("customManagers", [])
        if m.get("depNameTemplate") == dep_name
    ]


def pins_found(manager, path, text):
    """The current values that a custom manager finds in a file, none if the
    manager does not read that file."""
    if not file_matches(manager, path):
        return []
    return [
        m["currentValue"]
        for s in manager["matchStrings"]
        for m in python_pattern(s).finditer(text)
    ]


def releases_of(manager):
    return manager["datasourceTemplate"] == "github-releases"


def configurator_problems(config, files, version):
    """What keeps the configurator's constraint from following the releases of
    the configurator with its exact pin: `files` maps the paths of the
    declarations to their text."""
    managers = manager_for(config, "opentofu/opentofu")
    if not managers or not all(releases_of(m) for m in managers):
        return ["no manager follows the releases of the configurator"]
    problems = []
    for path, text in files.items():
        declared = re.findall(r'required_version\s*=\s*"([^"]*)"', text)
        found = [v for m in managers for v in pins_found(m, path, text)]
        if sorted(f"= {v}" for v in found) != sorted(declared):
            problems.append(f"{path}: the constraint {declared} is not found exactly")
        if any(v != version for v in found):
            problems.append(f"{path}: not the version of the register, {version}")
    off = [
        r
        for r in config.get("packageRules", [])
        if r.get("enabled") is False
        and r.get("matchManagers") == ["terraform"]
        and r.get("matchDepTypes") == ["required_version"]
    ]
    if not off:
        problems.append("the manager of the other tool still reads the constraint")
    return problems


def declaration_files():
    return {
        str(p.relative_to(ROOT)): p.read_text()
        for p in sorted((ROOT / "engine" / "configure").rglob("*.tf"))
    }


def configurator_register_version():
    (entry,) = [c for c in components() if c["name"] == "opentofu"]
    return entry["version"]


def test_R120_update_bot_follows_the_configurators_releases():
    files = declaration_files()
    assert any("required_version" in t for t in files.values()), "no constraint"
    assert not configurator_problems(
        renovate_config(), files, configurator_register_version()
    )


def test_R120_update_bot_follows_the_configurators_releases_detects_violation():
    version = "1.2.3"
    path = "engine/configure/x.tf"
    exact = {path: 'terraform {\n  required_version = "= 1.2.3"\n}\n'}
    manager = {
        "customType": "regex",
        "managerFilePatterns": ["/^engine\\/configure\\/.+\\.tf$/"],
        "matchStrings": ['required_version = "= (?<currentValue>[0-9.]+)"'],
        "depNameTemplate": "opentofu/opentofu",
        "datasourceTemplate": "github-releases",
    }
    rule = {
        "matchManagers": ["terraform"],
        "matchDepTypes": ["required_version"],
        "enabled": False,
    }
    good = {"customManagers": [manager], "packageRules": [rule]}
    assert configurator_problems(good, exact, version) == []
    # the other tool's manager still reads it
    assert configurator_problems({**good, "packageRules": []}, exact, version)
    # no manager for the configurator
    assert configurator_problems({"packageRules": [rule]}, exact, version)
    # the releases of another tool
    other = {**manager, "depNameTemplate": "hashicorp/terraform"}
    assert configurator_problems({**good, "customManagers": [other]}, exact, version)
    # a constraint that is not an exact pin, or a pin that is not the register's
    loose = {path: 'terraform {\n  required_version = ">= 1.2.3"\n}\n'}
    assert configurator_problems(good, loose, version)
    assert configurator_problems(good, exact, "1.2.4")
    # a file that the manager does not read
    assert configurator_problems(good, {"engine/other/x.tf": exact[path]}, version)


# ---- R121: the task runner's version, pinned in several places --------------

MISE_FILES = [".github/workflows/ci.yml", ".devcontainer/devcontainer.json"]
MISE_WORKFLOWS = [
    ".github/workflows/promote.yml",
    ".github/workflows/system-tests.yml",
]


def mise_problems(config, files):
    """What keeps the task runner's version from being updated in every file
    that pins it, with one value: `files` maps paths to text. The step of the
    other workflows is read by the built-in manager of the workflows."""
    managers = manager_for(config, "jdx/mise")
    if not managers or not all(releases_of(m) for m in managers):
        return ["no manager follows the releases of the task runner"]
    problems = []
    seen = set()
    for path, text in files.items():
        found = [v for m in managers for v in pins_found(m, path, text)]
        if len(found) != 1:
            problems.append(f"{path}: {len(found)} versions found, one expected")
        seen.update(found)
    if len(seen) > 1:
        problems.append(f"the files pin different versions: {sorted(seen)}")
    group = [
        r
        for r in config.get("packageRules", [])
        if "jdx/mise" in r.get("matchDepNames", []) and r.get("groupName")
    ]
    if not group:
        problems.append("the versions are not updated together")
    return problems


def test_R121_update_bot_follows_the_task_runner_everywhere():
    files = {p: (ROOT / p).read_text() for p in MISE_FILES}
    assert not mise_problems(renovate_config(), files)
    # the step of the other workflows pins the same version
    steps = "".join((ROOT / p).read_text() for p in MISE_WORKFLOWS)
    versions = set(re.findall(r"version: (20[0-9.]+)", steps))
    versions.update(
        pins_found(
            manager_for(renovate_config(), "jdx/mise")[0],
            MISE_FILES[0],
            files[MISE_FILES[0]],
        )
    )
    assert len(versions) == 1, versions


def test_R121_update_bot_follows_the_task_runner_everywhere_detects_violation():
    manager = {
        "managerFilePatterns": ["/^ci\\.yml$/", "/^dev\\.json$/"],
        "matchStrings": [
            "mise-version: (?<currentValue>[0-9.]+)",
            '"version": "(?<currentValue>[0-9.]+)"',
        ],
        "depNameTemplate": "jdx/mise",
        "datasourceTemplate": "github-releases",
    }
    rule = {"matchDepNames": ["jdx/mise"], "groupName": "mise"}
    config = {"customManagers": [manager], "packageRules": [rule]}
    files = {"ci.yml": "mise-version: 1.0.0\n", "dev.json": '{"version": "1.0.0"}'}
    assert mise_problems(config, files) == []
    assert mise_problems({**config, "packageRules": []}, files)
    assert mise_problems({"packageRules": [rule]}, files)
    assert mise_problems(config, {**files, "ci.yml": "mise-version: 1.0.1\n"})
    assert mise_problems(config, {**files, "ci.yml": "mise-version: '1.0.0'\n"})


# ---- R122: a build context is not an image ----------------------------------


def build_contexts(text):
    """Names that a container file copies from and that are neither one of its
    stages nor an image reference: contexts given at build time."""
    stages = set(
        re.findall(r"^FROM\s+\S+\s+AS\s+(\S+)", text, re.MULTILINE | re.IGNORECASE)
    )
    names = set(re.findall(r"^COPY\s+(?:--\S+\s+)*?--from=(\S+)", text, re.MULTILINE))
    return sorted(n for n in names if n not in stages and not re.search(r"[/:.]", n))


def unignored_contexts(config, texts):
    ignored = set()
    for rule in config.get("packageRules", []):
        if rule.get("enabled") is False and rule.get("matchManagers") == ["dockerfile"]:
            ignored.update(rule.get("matchPackageNames", []))
    return sorted({n for text in texts for n in build_contexts(text)} - ignored)


def test_R122_update_bot_ignores_build_contexts():
    texts = [p.read_text() for p in sorted((ROOT / "engine").rglob("Containerfile*"))]
    assert any(build_contexts(t) for t in texts), "no build context found"
    assert not unignored_contexts(renovate_config(), texts)


def test_R122_update_bot_ignores_build_contexts_detects_violation():
    host = "registry" + ".example/"  # put together: no reference in this file
    tag = ":1"
    text = (
        f"FROM {host}x{tag} AS one\n"
        "COPY --from=ctx / /src\n"
        "COPY --chmod=555 --from=other /f /f\n"
        "COPY --from=one /a /a\n"
        f"COPY --from={host}y{tag} /a /a\n"
    )
    assert build_contexts(text) == ["ctx", "other"]
    rule = {
        "matchManagers": ["dockerfile"],
        "matchPackageNames": ["ctx", "other"],
        "enabled": False,
    }
    assert unignored_contexts({"packageRules": [rule]}, [text]) == []
    assert unignored_contexts({}, [text]) == ["ctx", "other"]
    partial = {**rule, "matchPackageNames": ["ctx"]}
    assert unignored_contexts({"packageRules": [partial]}, [text]) == ["other"]
    enabled = {k: v for k, v in rule.items() if k != "enabled"}
    assert unignored_contexts({"packageRules": [enabled]}, [text])


# ---- R124: the JDK that builds the identity provider stays on its LTS line --


def line_problems(config, image, current, newer, older):
    """What keeps the update bot from proposing a version of `image` beyond the
    line of its current version: the rule's pattern must accept the current
    version and the `older` ones of the line, and refuse the `newer` ones."""
    rules = [
        r
        for r in config.get("packageRules", [])
        if image in r.get("matchPackageNames", []) and "allowedVersions" in r
    ]
    if len(rules) != 1:
        return [f"{len(rules)} rules cap {image}, one expected"]
    allowed = rules[0]["allowedVersions"]
    if not (allowed.startswith("/") and allowed.endswith("/")):
        return [f"not a regular expression: {allowed}"]
    pattern = re.compile(allowed[1:-1])
    problems = [f"refuses {v}" for v in [current, *older] if not pattern.search(v)]
    problems += [f"accepts {v}" for v in newer if pattern.search(v)]
    return problems


def test_R124_update_bot_keeps_the_jdk_on_its_lts_line():
    (entry,) = [t for t in tool_images() if t["name"] == "eclipse-temurin"]
    major = entry["version"].split("-")[0]
    assert major == "21", "the LTS line of the register changed: decide, then edit"
    assert not line_problems(
        renovate_config(),
        entry["image"],
        entry["version"],
        newer=["22-jdk", "25-jdk", "27-jdk", "27.0.1_9-jdk"],
        older=["21.0.9_10-jdk", "21-jdk-noble"],
    )


def test_R124_update_bot_keeps_the_jdk_on_its_lts_line_detects_violation():
    jdk = "registry" + ".example/jdk"  # put together: no reference in this file
    rule = {"matchPackageNames": [jdk], "allowedVersions": "/^21([.-]|$)/"}
    args = (jdk, "21-jdk", ["22-jdk", "210-jdk"], ["21.0.1_1-jdk"])
    assert line_problems({"packageRules": [rule]}, *args) == []
    # no rule, a rule for another image, a rule that allows the next line
    assert line_problems({}, *args)
    assert line_problems(
        {"packageRules": [{**rule, "matchPackageNames": ["x"]}]}, *args
    )
    assert line_problems({"packageRules": [{**rule, "allowedVersions": "/^2/"}]}, *args)
    # a rule that is not a pattern, or that refuses the current version
    assert line_problems({"packageRules": [{**rule, "allowedVersions": "<22"}]}, *args)
    assert line_problems(
        {"packageRules": [{**rule, "allowedVersions": "/^25/"}]}, *args
    )
