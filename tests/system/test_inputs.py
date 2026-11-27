"""The tag of an inner image depends on every input of its container file (PM-005).

An access-rules file in the database image was once stale because the tag was
made of the source commits and the container file only. No container is started
and nothing is built: the tag is computed by `mise-tasks/engine/tag` on a
temporary copy of the inputs, for every inner image.
"""

import hashlib
import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import ROOT

CONTAINERFILES = [
    "engine/database/Containerfile",
    "engine/access/Containerfile",
    "engine/secrets/Containerfile",
    "engine/mail/Containerfile",
]
COMMITS = "a1\nb2\nc3\nd4\n"


def copied_files(containerfile: str) -> list[str]:
    """The repository files the container file copies (COPY without --from)."""
    files: list[str] = []
    for line in (ROOT / containerfile).read_text().splitlines():
        parts = line.split()
        if parts[:1] == ["COPY"] and not any(p.startswith("--from=") for p in parts):
            files += [p for p in parts[1:-1] if not p.startswith("--")]
    return files


def copy_inputs(containerfile: str, destination: Path) -> None:
    for name in [containerfile, *copied_files(containerfile)]:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)


def tag_of(containerfile: str, directory: Path, commits: str = COMMITS) -> str:
    return subprocess.run(
        [str(ROOT / "mise-tasks/engine/tag"), containerfile, str(directory)],
        input=commits,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def naive_tag(containerfile: str, directory: Path, commits: str = COMMITS) -> str:
    """What the tag was before: the commits and the container file only."""
    data = commits.encode() + (directory / containerfile).read_bytes()
    return hashlib.sha256(data).hexdigest()[:12]


def inputs_that_leave_the_tag(tag, containerfile: str, directory: Path) -> list[str]:
    """The inputs whose change leaves the tag as it was (none, when it is right)."""
    unchanged = []
    for name in [containerfile, *copied_files(containerfile)]:
        before = tag(containerfile, directory)
        path = directory / name
        original = path.read_bytes()
        path.write_bytes(original + b"\n# changed\n")
        after = tag(containerfile, directory)
        path.write_bytes(original)
        if before == after:
            unchanged.append(name)
    if tag(containerfile, directory) == tag(containerfile, directory, COMMITS + "e5\n"):
        unchanged.append("source commits")
    return unchanged


@pytest.mark.parametrize("containerfile", CONTAINERFILES)
def test_R99_image_tag_depends_on_every_input(containerfile, tmp_path):
    """Changing the container file, a file it copies or a source commit changes the tag."""
    copy_inputs(containerfile, tmp_path)
    assert tag_of(containerfile, tmp_path) == tag_of(containerfile, tmp_path)
    assert inputs_that_leave_the_tag(tag_of, containerfile, tmp_path) == []


def test_R99_image_tag_depends_on_every_input_detects_violation(tmp_path):
    """The check fails on a tag made of the commits and the container file only:
    it names the files of the database image that the old tag ignored."""
    containerfile = "engine/database/Containerfile"
    copy_inputs(containerfile, tmp_path)
    missed = inputs_that_leave_the_tag(naive_tag, containerfile, tmp_path)
    assert missed == copied_files(containerfile)
    assert "engine/database/prepare.sql" in missed


def test_generated_rules_are_inputs_of_the_database_tag(tmp_path):
    """The generated access rules are passed as extra inputs of the tag: a change
    to them changes it."""
    containerfile = "engine/database/Containerfile"
    copy_inputs(containerfile, tmp_path)
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "pg_hba.conf").write_text("local all postgres peer\n")

    def tag() -> str:
        return subprocess.run(
            [str(ROOT / "mise-tasks/engine/tag"), containerfile, str(tmp_path)],
            input=COMMITS,
            env={"PATH": "/usr/bin:/bin", "ANIMA_TAG_EXTRA": "rules/pg_hba.conf"},
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    before = tag()
    (rules / "pg_hba.conf").write_text("local all all reject\n")
    assert tag() != before
