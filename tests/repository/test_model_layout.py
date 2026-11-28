"""The layout of the model: one requirement per file (R190, R191, R192; PM-011, PM-019).

Two branches that each add a requirement to one long file add it at the same
place, git cannot merge two additions at one place, and the second pull request
left the merge queue seven times in one day. Each requirement is a file of its
own, with its verifications and its satisfy line, under `model/requirements/`,
so two additions are two files. The rest, the packages' common definitions (the
ports, the parts, the triggers), is the root file `model/anima.sysml`, which a
new requirement never changes. R150 merges two such additions with git.

Which file holds which requirement is not in the export of the model, so these
checks read the files: the names, and the declarations at the top of each file
with comments left out. What the declarations mean is still read from the export.
"""

import os
import re
import subprocess

from sysml_model import ROOT, thresholds

MODEL = ROOT / "model"
ROOT_FILE = "anima.sysml"
FILE_NAME = re.compile(r"^(?:R(\d+)-)?([a-z0-9]+(?:-[a-z0-9]+)*)\.sysml$")
COMMENT = re.compile(r"/\*.*?\*/|//[^\n]*", re.DOTALL)
TOKEN = re.compile(
    r"\bpackage\s+(?P<package>\w+)\s*\{"
    r"|\brequirement\s+(?:<'(?P<alias>R[\d.]+)'>\s*)?(?P<name>(?!def\b)\w+)"
    r"|\bverification\s+def\s+(?P<test>\w+)"
    r"|(?P<open>\{)|(?P<close>\})"
)


def kebab(name):
    """`everyGapRegistered` is `every-gap-registered`."""
    return re.sub(r"(?<=[a-z0-9])([A-Z])", r"-\1", name).lower()


def snake(name):
    """`everyGapRegistered` is `every_gap_registered`."""
    return kebab(name).replace("-", "_")


def pascal(name):
    """`everyGapRegistered` is `EveryGapRegistered`."""
    return name[0].upper() + name[1:]


def declarations(text):
    """(packages, requirements, tests) of a file: the root packages by name; the
    requirements as (alias or None, name, depth) where depth 1 is directly in a
    package; the names of the verification definitions."""
    packages, requirements, tests, depth = [], [], [], 0
    for token in TOKEN.finditer(COMMENT.sub(" ", text)):
        if token["package"]:
            if depth == 0:
                packages.append(token["package"])
            depth += 1
        elif token["name"]:
            requirements.append((token["alias"], token["name"], depth))
        elif token["test"]:
            tests.append(token["test"])
        elif token["open"]:
            depth += 1
        else:
            depth -= 1
    return packages, requirements, tests


def number_of(alias):
    return int(re.match(r"R(\d+)", alias)[1])


def layout_faults(files):
    """Faults of the layout of the model. `files` maps the path of each file,
    relative to model/, to its text. A requirement is identified by its name:
    its file is `<kebab-case name>.sysml`, its package the name with a capital,
    its verifications `test_<snake_case name>...`. One that had a number before
    keeps it as an alias: `R<n>-<kebab-case name>.sysml`, package `R<n>`,
    verifications `test_R<n>_...`."""
    faults, names, aliases = [], {}, {}
    for path, text in sorted(files.items()):
        packages, requirements, tests = declarations(text)
        parts = path.split("/")
        if path == ROOT_FILE:
            if requirements:
                faults.append(f"{path}: a requirement is in the root file")
            continue
        if not (len(parts) == 3 and parts[0] == "requirements"):
            faults.append(
                f"{path}: a model file outside the root and requirements/<group>/"
            )
            continue
        named = FILE_NAME.match(parts[2])
        if not named:
            faults.append(f"{path}: the name is not [R<n>-]<kebab-case name>.sysml")
            continue
        top = [r for r in requirements if r[2] == 1]
        if len(top) != 1:
            faults.append(f"{path}: {len(top)} requirements, not exactly one")
            continue
        alias, name, _depth = top[0]
        names.setdefault(name, []).append(path)
        if alias:
            aliases.setdefault(alias, []).append(path)
        if alias != (f"R{named[1]}" if named[1] else None):
            faults.append(f"{path}: holds alias {alias}, the file name says {named[1]}")
        if named[2] != kebab(name):
            faults.append(
                f"{path}: the name says {named[2]}, the requirement is {name}"
            )
        wanted = f"R{named[1]}" if alias else pascal(name)
        if packages != [wanted]:
            faults.append(f"{path}: the package is {packages}, not [{wanted}]")
        for sub, _sub_name, depth in requirements:
            if depth > 1 and sub and not sub.startswith(f"{alias}."):
                faults.append(f"{path}: {sub} is nested in {alias}")
        stem = f"test_{alias}_" if alias else f"test_{snake(name)}"
        for test in tests:
            if not test.startswith(stem):
                faults.append(f"{path}: the verification {test} is not of {name}")
    for kind, found in (("name", names), ("alias", aliases)):
        for key, paths in found.items():
            if len(paths) > 1:
                faults.append(f"{kind} {key} is in {len(paths)} files: {sorted(paths)}")
    return faults


def number_faults(files, frozen):
    """A requirement added now carries no number: any short name `R<n>` above the
    highest number that was frozen when the names became the identifiers."""
    faults = []
    for path, text in sorted(files.items()):
        for alias, name, _depth in declarations(text)[1]:
            if alias and number_of(alias) > frozen:
                faults.append(f"{path}: {name} has the number {alias}, above {frozen}")
    return faults


def model_files(directory=MODEL):
    return {
        str(path.relative_to(directory)): path.read_text()
        for path in sorted(directory.rglob("*.sysml"))
    }


def test_R190_each_requirement_in_a_file_of_its_own():
    files = model_files()
    assert ROOT_FILE in files
    assert len(files) > 100, "the requirements are not in files of their own"
    assert layout_faults(files) == []


GOOD = (
    "package R7 {\n    private import Anima::*;\n"
    "    requirement <'R7'> everyGapRegistered {\n"
    "        doc /* { not code } */\n"
    "        requirement <'R7.1'> nested { }\n"
    "    }\n"
    "    satisfy everyGapRegistered by toolchain;\n"
    "    verification def test_R7_every_gap_registered { }\n"
    "    verification def test_R7_1_nested { }\n"
    "}\n"
)
PATH = "requirements/day0/R7-every-gap-registered.sysml"


def test_R190_each_requirement_in_a_file_of_its_own_detects_violation():
    root = "package Anima { part def System; }\n"
    assert layout_faults({ROOT_FILE: root, PATH: GOOD}) == []
    two = GOOD.replace(
        "    satisfy", "    requirement <'R8'> second { }\n    satisfy", 1
    )
    assert layout_faults({ROOT_FILE: root, PATH: two})
    other = PATH.replace("R7-", "R8-")
    assert layout_faults({ROOT_FILE: root, other: GOOD})  # the name says R8
    renamed = PATH.replace("every-gap-registered", "something-else")
    assert layout_faults({ROOT_FILE: root, renamed: GOOD})
    assert layout_faults({ROOT_FILE: root + GOOD, PATH: GOOD})  # one in the root
    elsewhere = "requirements/R7-every-gap-registered.sysml"
    assert layout_faults({ROOT_FILE: root, elsewhere: GOOD})  # no group
    assert layout_faults({ROOT_FILE: root, "other.sysml": GOOD})
    twin = "requirements/day1/R7-every-gap-registered.sysml"
    assert any(  # two files claim one id
        "2 files" in f for f in layout_faults({ROOT_FILE: root, PATH: GOOD, twin: GOOD})
    )
    foreign = GOOD.replace("test_R7_every", "test_R8_every")
    assert layout_faults({ROOT_FILE: root, PATH: foreign})
    wrong_package = GOOD.replace("package R7", "package Day0")
    assert layout_faults({ROOT_FILE: root, PATH: wrong_package})
    foreign_sub = GOOD.replace("R7.1", "R9.1")
    assert layout_faults({ROOT_FILE: root, PATH: foreign_sub})
    # A requirement named in a comment is not one.
    commented = GOOD + "// requirement <'R9'> notOne { }\n"
    assert layout_faults({ROOT_FILE: root, PATH: commented}) == []
    # A requirement with no number: the name is the identifier.
    assert layout_faults({ROOT_FILE: root, NAMED_PATH: NAMED}) == []
    assert layout_faults({ROOT_FILE: root, NAMED_PATH.replace("every", "each"): NAMED})
    assert layout_faults({ROOT_FILE: root, NAMED_PATH: NAMED.replace("EveryGap", "x")})
    assert layout_faults(
        {ROOT_FILE: root, NAMED_PATH: NAMED.replace("test_every", "test_each")}
    )
    # A name already taken by a file with a number, and an alias given to a file
    # whose name has none.
    assert any(
        "2 files" in f
        for f in layout_faults(
            {
                ROOT_FILE: root,
                NAMED_PATH: NAMED,
                "requirements/day0/R7-every-gap-registered.sysml": GOOD,
            }
        )
    )
    assert layout_faults({ROOT_FILE: root, NAMED_PATH: GOOD})


NAMED = (
    "package EveryGapRegistered {\n    private import Anima::*;\n"
    "    requirement everyGapRegistered {\n        doc /* x */\n    }\n"
    "    satisfy everyGapRegistered by toolchain;\n"
    "    verification def test_every_gap_registered { }\n"
    "}\n"
)
NAMED_PATH = "requirements/day0/every-gap-registered.sysml"


def test_new_requirements_carry_no_number(model):
    files = model_files()
    frozen = thresholds(model)["newRequirementsCarryNoNumber"]["maxLegacyNumber"]
    assert frozen[1] is None
    assert number_faults(files, frozen[0]) == []


def test_new_requirements_carry_no_number_detects_violation():
    assert number_faults({"a": GOOD}, 7) == []
    assert number_faults({"a": GOOD}, 6)
    assert number_faults({"a": NAMED}, 0) == []
    nested = GOOD.replace("R7.1", "R70.1")
    assert number_faults({"a": nested}, 7)


# ---- R192: the check validates every file, root first, and names the faulty one ----------

CHECK = ROOT / "mise-tasks" / "model" / "check"
PREFIX = "package Anima { part def System; part def Toolchain; part toolchain : Toolchain; }\n"


def write_model(directory, requirements):
    """A small model: the root file and the given requirement files (name: text)."""
    (directory / "requirements" / "day0").mkdir(parents=True)
    (directory / "anima.sysml").write_text(PREFIX)
    for name, text in requirements.items():
        (directory / "requirements" / "day0" / name).write_text(text)


GOOD_FILE = (
    "package R1 {\n    private import Anima::*;\n"
    "    requirement <'R1'> alphaRule { subject tools : Toolchain; }\n"
    "    satisfy alphaRule by toolchain;\n}\n"
)
BAD_FILE = (
    "package R2 {\n    private import Anima::*;\n"
    "    requirement <'R2'> betaRule { subject tools : Toolchain; }\n"
    "    satisfy nothingOfThatName by toolchain;\n}\n"
)


def feed_check(script_text, directory, tmp_path, pilot_says=""):
    """Run the check with a stand-in for the JVM that keeps what it is given and
    prints `pilot_says`. Returns the packages fed, cell by cell, in order, and
    the finished process."""
    tmp_path.mkdir()
    script = tmp_path / "check"
    script.write_text(script_text)
    script.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fed = tmp_path / "fed"
    java = bin_dir / "java"
    java.write_text(
        f'#!/usr/bin/env bash\ncat > "{fed}"\nprintf "%s\\n" "$PILOT_SAYS"\n'
    )
    java.chmod(0o755)
    fetch = tmp_path / "root" / "mise-tasks" / "model" / "fetch"
    fetch.parent.mkdir(parents=True)
    fetch.write_text(f'#!/usr/bin/env bash\necho "{tmp_path}/pilot"\n')
    fetch.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "MISE_PROJECT_ROOT": str(tmp_path / "root"),
        "SYSML_PILOT_VERSION": "9.9.9",
        "PILOT_SAYS": pilot_says,
    }
    done = subprocess.run(
        [str(script), str(directory)],
        check=False,
        env=env,
        capture_output=True,
        text=True,
    )
    cells = re.split(r"(?m)^%$", fed.read_text())[1::2]
    packages = [re.search(r"package (\w+)", c)[1] for c in cells if "package" in c]
    return packages, done


# What the pilot prints for a reference that does not resolve in its third cell:
# the cells are numbered from 1 in the order they were fed (observed on 2026-11-28
# with the real pilot; the full check of the model shows it on every run).
UNRESOLVED = (
    "3> ERROR:Couldn't resolve reference to Feature 'nothingOfThatName'. "
    "(3.sysml line : 4 column : 13)"
)


def test_R192_check_validates_every_file_of_the_model(tmp_path):
    """Proves, with a stand-in for the JVM, that the check feeds the pilot the
    root file first and then every requirement file, each as a cell, and that
    an error in the third cell fails it and names the third file and no other.
    That the real pilot reports an error of any cell by its number is observed
    (see UNRESOLVED), and the check of the whole model runs it on every commit."""
    model = tmp_path / "model"
    write_model(model, {"R1-first.sysml": GOOD_FILE, "R2-second.sysml": BAD_FILE})
    packages, done = feed_check(CHECK.read_text(), model, tmp_path / "ok")
    assert packages == ["Anima", "R1", "R2"]
    assert done.returncode == 0, done.stderr
    packages, done = feed_check(CHECK.read_text(), model, tmp_path / "bad", UNRESOLVED)
    assert done.returncode != 0
    assert "R2-second.sysml" in done.stderr
    assert "R1-first.sysml" not in done.stderr
    assert "anima.sysml" not in done.stderr


def test_R192_check_validates_every_file_of_the_model_detects_violation(tmp_path):
    model = tmp_path / "model"
    write_model(model, {"R1-first.sysml": GOOD_FILE, "R2-second.sysml": BAD_FILE})
    text = CHECK.read_text()
    # A check that reads no requirement file.
    pattern = "-name '*.sysml' ! -path"
    assert pattern in text
    blind = text.replace(pattern, "-name 'none.sysml' ! -path")
    assert feed_check(blind, model, tmp_path / "blind")[0] == ["Anima"]
    # A check that does not load the root file first: the others cannot import it.
    root_line = '[ ! -f "$path/anima.sysml" ] || files+=("$path/anima.sysml")'
    assert root_line in text
    last = text.replace(root_line, ":")
    assert feed_check(last, model, tmp_path / "last")[0][0] != "Anima"
    # A check that does not say which file a numbered error is in.
    silent = text.replace(
        'echo "model:check: $((i + 1)).sysml is ${files[$i]}" >&2', ":"
    )
    assert silent != text
    done = feed_check(silent, model, tmp_path / "silent", UNRESOLVED)[1]
    assert done.returncode != 0
    assert "R2-second.sysml" not in done.stderr
