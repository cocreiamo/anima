"""The tag of an inner image depends on every input of its container file (PM-005).

An access-rules file in the database image was once stale because the tag was
made of the source commits and the container file only. No container is started
and nothing is built: the tag is computed by `mise-tasks/engine/tag` on a
temporary copy of the inputs, for every inner image.
"""

import hashlib
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
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
    """The inputs whose change leaves the tag as it was (none, when it is right).
    Each input is changed in a copy of its own, and the copies are tagged together:
    the tag is a process that mostly waits for the machine, so it runs in parallel."""
    before = tag(containerfile, directory)
    names = [containerfile, *copied_files(containerfile)]

    def unchanged(indexed: tuple[int, str]) -> bool:
        index, name = indexed
        copy = directory.parent / f"{directory.name}-changed-{index}"
        shutil.copytree(directory, copy)
        with (copy / name).open("ab") as changed:
            changed.write(b"\n# changed\n")
        return tag(containerfile, copy) == before

    with ThreadPoolExecutor() as pool:
        flags = list(pool.map(unchanged, enumerate(names)))
        more = pool.submit(tag, containerfile, directory, COMMITS + "e5\n").result()
    found = [name for name, same in zip(names, flags, strict=True) if same]
    if before == more:
        found.append("source commits")
    return found


@pytest.mark.parametrize("containerfile", CONTAINERFILES)
def test_R99_image_tag_depends_on_every_input(containerfile, tmp_path):
    """Changing the container file, a file it copies or a source commit changes the tag."""
    copy_inputs(containerfile, tmp_path)
    assert tag_of(containerfile, tmp_path) == tag_of(containerfile, tmp_path)  # stable
    assert inputs_that_leave_the_tag(tag_of, containerfile, tmp_path) == []
    if containerfile == SECRETS:
        assert lock_file_faults(tmp_path / "locks") == []


def test_R99_image_tag_depends_on_every_input_detects_violation(tmp_path):
    """The check fails on a tag made of the commits and the container file only:
    it names the files of the database image that the old tag ignored."""
    containerfile = "engine/database/Containerfile"
    copy_inputs(containerfile, tmp_path)
    missed = inputs_that_leave_the_tag(naive_tag, containerfile, tmp_path)
    assert missed == copied_files(containerfile)
    assert "engine/database/prepare.sql" in missed
    # A tag that is not given the lock files leaves both of them out.
    secrets_inputs(tmp_path / "locks")
    assert locks_that_leave_the_tag(tmp_path / "locks", "") == LOCK_FILES.split()


LOCK_FILES = "third_party/openbao/go.mod third_party/openbao/go.sum"
SECRETS = "engine/secrets/Containerfile"


def secrets_tag(directory: Path, extra: str, commits: str = COMMITS) -> str:
    return subprocess.run(
        [str(ROOT / "mise-tasks/engine/tag"), SECRETS, str(directory)],
        input=commits,
        env={"PATH": "/usr/bin:/bin", "ANIMA_TAG_EXTRA": extra},
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def secrets_inputs(directory: Path) -> None:
    (directory / "engine/secrets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / SECRETS, directory / SECRETS)
    for lock in LOCK_FILES.split():
        (directory / lock).parent.mkdir(parents=True, exist_ok=True)
        (directory / lock).write_text(f"{lock}\n")


def locks_that_leave_the_tag(directory: Path, extra: str) -> list[str]:
    before = secrets_tag(directory, extra)
    left = []
    for lock in LOCK_FILES.split():
        original = (directory / lock).read_text()
        (directory / lock).write_text(original + "changed\n")
        if secrets_tag(directory, extra) == before:
            left.append(lock)
        (directory / lock).write_text(original)
    return left


def lock_file_faults(tmp_path: Path) -> list[str]:
    """What is wrong with how the secret store's tags take the fork's lock files: the
    build task gives go.mod and go.sum as extra inputs to the dependencies image and to
    the image built on it, and a change to either changes the tag."""
    build = (ROOT / "mise-tasks/engine/build").read_text()
    faults = []
    if f'extra="{LOCK_FILES}"' not in build:
        faults.append("the build task does not name the lock files")
    if build.count('ANIMA_TAG_EXTRA="$extra"') != 2:
        faults.append("the dependencies image and the image do not both take them")
    secrets_inputs(tmp_path)
    return faults + locks_that_leave_the_tag(tmp_path, LOCK_FILES)


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
