"""The decision records: only architecture records exist (R93) and no text names
a record that does not exist (R94).

Each check is a function of its inputs; its companion test
(`<name>_detects_violation`) feeds it a deliberately wrong input.

R93 checks the front matter key `category: architecture` and that nothing else
sits in `docs/adr/`. It does not judge by title or body whether a record is
really about architecture: no such check was designed, so that remains a
matter of the skill `anima-writing-a-decision-record` and of review.
"""

import json
import os
import re
import subprocess
import tomllib

from repo_facts import repository_files
from sysml_model import ROOT

ADR_DIR = ROOT / "docs" / "adr"
RECORD_NAME = re.compile(r"(\d{4})-[a-z0-9-]+\.md")
# "ADR 0004", "ADR-0004", "ADR 0004, 0005", "ADRs 0004 and 0005", and the same
# with a line break between the word and the number. A number that is the start
# of a date ("ADR 2026-11-27") is not a reference.
REFERENCE = re.compile(
    r"\bADRs?(?:\s+|-)?(\d{4}(?!-?\d)(?:(?:,\s*|\s+and\s+|\s+to\s+)\d{4}(?!-?\d))*)"
)
# Binary or generated files that hold no prose.
SKIPPED_SUFFIXES = (".png", ".jpg", ".gz", ".pyc", ".lock", ".sum")


def front_matter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    fields = {}
    for line in (match[1] if match else "").splitlines():
        key, _, value = line.partition(":")
        if _:
            fields[key.strip()] = value.strip()
    return fields


# ---- R93: only architecture records exist ----------------------------------------


def record_faults(files):
    """`files` is {file name: text} of `docs/adr/`. Every record has the category
    architecture and its number equals the one in its file name; nothing but the
    generated index is anything else."""
    faults = []
    for name, text in sorted(files.items()):
        if name == "README.md":
            continue
        match = RECORD_NAME.fullmatch(name)
        if not match:
            faults.append(f"{name}: not a record (NNNN-slug.md)")
            continue
        fields = front_matter(text)
        if fields.get("category") != "architecture":
            faults.append(
                f"{name}: category is {fields.get('category')!r}, not architecture"
            )
        if fields.get("number") != str(int(match[1])):
            faults.append(
                f"{name}: number {fields.get('number')!r} differs from the file name"
            )
    return faults


def test_R93_only_architecture_records_exist():
    files = {p.name: p.read_text() for p in ADR_DIR.glob("*") if p.is_file()}
    assert any(RECORD_NAME.fullmatch(n) for n in files), "no record found"
    faults = record_faults(files)
    assert not faults, faults


def test_R93_only_architecture_records_exist_detects_violation():
    good = "---\nnumber: 7\ncategory: architecture\n---\n# T\n"
    assert record_faults({"0007-a.md": good, "README.md": "index"}) == []
    assert record_faults({"0007-a.md": good.replace("architecture", "process")})
    assert record_faults({"0007-a.md": good.replace("category: architecture\n", "")})
    assert record_faults({"0008-a.md": good})
    assert record_faults({"notes.md": good})


# ---- R94: no text names a record that does not exist -----------------------------


def existing_numbers(names):
    return {m[1] for n in names if (m := RECORD_NAME.fullmatch(n))}


def reference_faults(texts, existing):
    """`texts` is {path: text}. Each four-digit number written after ADR must be
    the number of a record that exists."""
    faults = []
    for path, text in sorted(texts.items()):
        for match in REFERENCE.finditer(text):
            for number in re.findall(r"\d{4}", match[1]):
                if number not in existing:
                    faults.append(f"{path}: names ADR {number}, which does not exist")
    return faults


def repository_texts():
    texts = {}
    for name, path in repository_files():
        if name.endswith(SKIPPED_SUFFIXES):
            continue
        try:
            texts[name] = path.read_text()
        except UnicodeDecodeError:
            continue
    return texts


def test_R94_no_reference_to_a_record_that_does_not_exist():
    existing = existing_numbers(p.name for p in ADR_DIR.glob("*.md"))
    assert existing, "no record found"
    texts = repository_texts()
    assert texts
    faults = reference_faults(texts, existing)
    assert not faults, faults


def test_R94_no_reference_to_a_record_that_does_not_exist_detects_violation():
    existing = {"0001", "0002"}
    assert reference_faults({"a.md": "see ADR 0002"}, existing) == []
    assert reference_faults({"a.md": "see ADR-0001 and ADR 0002"}, existing) == []
    missing = "see ADR " + "0009"
    assert reference_faults({"a.md": missing}, existing)
    assert reference_faults({"a.md": "ADR 0001, 0003"}, existing)
    assert reference_faults({"a.md": "ADRs 0001 and 0004"}, existing)
    # A line break between the word and the number does not hide a reference.
    assert reference_faults({"a.md": "(`After=`, ADR\n 0011)"}, existing)
    assert reference_faults({"a.md": "(ADR\n 0002, 0011)"}, existing)
    assert reference_faults({"a.md": "(ADR\n 0002)"}, existing) == []
    # A date after the word is not a reference.
    assert reference_faults({"a.md": "the ADR\n2026-11-27"}, existing) == []


# ---- R145: the records are made from the organization's template -------------------

TEMPLATE = "shared/templates/adr-madr.md"


def template_faults(config, root):
    """The configuration of the record tool names the template of the shared
    repository, and the file is there (the shared submodule is checked out)."""
    custom = config.get("templates", {}).get("custom")
    if custom != TEMPLATE:
        return [f"[templates].custom is {custom!r}, not {TEMPLATE!r}"]
    if not (root / custom).is_file():
        return [f"{custom} does not exist: is the shared submodule checked out?"]
    return []


def new_record(config_text, directory):
    """Create a record in a repository of its own under `directory` with the
    given configuration: the result of `adrs new` and the records listed."""
    (directory / "docs" / "adr").mkdir(parents=True)
    config = directory / "adrs.toml"
    config.write_text(config_text)
    # The configuration is named explicitly: a user-level one never counts.
    env = {**os.environ, "ADRS_CONFIG": str(config)}
    made = subprocess.run(
        ["adrs", "new", "A title"],
        cwd=directory,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    listed = subprocess.run(
        ["adrs", "export", "json"],
        cwd=directory,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    records = json.loads(listed.stdout)["adrs"] if listed.returncode == 0 else []
    return made, records


def test_R145_records_made_from_the_shared_template(tmp_path):
    config = tomllib.loads((ROOT / "adrs.toml").read_text())
    assert not template_faults(config, ROOT)
    # The same configuration, with the template named by its full path (the
    # path of a template is read from the directory of the configuration),
    # makes a record that the tool lists.
    text = (ROOT / "adrs.toml").read_text().replace(TEMPLATE, str(ROOT / TEMPLATE))
    made, records = new_record(text, tmp_path)
    assert made.returncode == 0, made.stderr
    assert [(r["number"], r["title"]) for r in records] == [(1, "A title")]


def test_R145_records_made_from_the_shared_template_detects_violation(tmp_path):
    assert template_faults({}, ROOT)
    assert template_faults({"templates": {"custom": "other.md"}}, ROOT)
    assert template_faults({"templates": {"custom": TEMPLATE}}, tmp_path)
    missing = (
        '[templates]\nformat = "madr"\nvariant = "full"\n'
        f'custom = "{tmp_path}/missing.md"\n'
    )
    made, records = new_record(missing, tmp_path / "repository")
    assert made.returncode != 0
    assert records == []
