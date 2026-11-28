"""Independent additions do not conflict in generated files or in the model
(R150, PM-011, PM-016, PM-019).

A generated file that is committed is rewritten by every branch that changes its
source. GitHub's merge and its merge queue run no custom merge driver, so two
branches that each add one entry to the same list conflict whenever the entries
land in the same place of the file. The lists grow by id (the next free one), so
rendered by id they land at the same place, the end: the catalog's tables, the
fitness functions, the pending tests and the skills index's total did exactly
that, and each conflict cost a merge, a regeneration, a full check and a new
round of CI.

The test renders the volatile parts of the generated files for a base and for
two independent additions to it, then merges the three the way git does
(`git merge-file`) and asserts that no file conflicts.

The model is the same case (PM-011): two branches that each add a requirement
add it at the same place of one file, git cannot merge two additions at one
place, and the second pull request left the merge queue seven times in one day.
Each requirement is a file of its own, so the test commits the model of the
repository, adds one requirement on each of two branches the way the layout
says (a new file), and merges the branches with git.
"""

import os
import re
import shutil
import subprocess

import agent_layer as al
import generators
import sysml_model

MODEL = sysml_model.ROOT / "model"


def git(repo, *args, check=True):
    """A git command in a repository of the test, with no configuration of the
    user: no signing, no hooks, no template."""
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@example.org",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            "-C",
            str(repo),
            *args,
        ],
        check=check,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
        },
    )


def requirement_text(short, name, indent):
    pad = " " * indent
    return (
        f"{pad}requirement <'R{short}'> {name} {{\n"
        f"{pad}    doc /* The {name} shall hold. */\n"
        f"{pad}    subject tools : Toolchain;\n"
        f"{pad}}}\n"
    )


def add_requirement_to_model(repo, short, name):
    """Add a requirement the way the layout of the model says. With a directory
    of requirements it is a new file there; with one file it is inserted at the
    end of the first group, where the next id goes."""
    directory = repo / "model" / "requirements"
    if directory.is_dir():
        path = directory / "day0" / f"R{short}-{name}.sysml"
        path.parent.mkdir(exist_ok=True)
        path.write_text(
            f"package R{short} {{\n    private import Anima::*;\n\n"
            + requirement_text(short, name, 4)
            + "}\n"
        )
    else:
        path = repo / "model" / "anima.sysml"
        marker = "    }\n\n    // ---- Day 1"
        text = path.read_text()
        assert marker in text, "the end of the first group is not where it was"
        path.write_text(
            text.replace(marker, requirement_text(short, name, 8) + marker, 1)
        )


def merged_model_conflicts(tmp_path, source, first, second):
    """Whether two branches, each adding one requirement to a copy of the model
    in `source`, merge with a conflict. Real git, in a repository of its own."""
    repo = tmp_path / "repository"
    shutil.copytree(source, repo / "model")
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")
    for branch, (short, name) in (("first", first), ("second", second)):
        git(repo, "switch", "-q", "-c", branch, "main")
        add_requirement_to_model(repo, short, name)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", name)
    git(repo, "switch", "-q", "first")
    merged = git(repo, "merge", "--no-edit", "second", check=False)
    return merged.returncode != 0


def conflicts(base, ours, theirs, tmp_path):
    """Number of conflicts of the three-way merge of three texts, by git."""
    files = []
    for name, text in (("ours", ours), ("base", base), ("theirs", theirs)):
        path = tmp_path / name
        path.write_text(text)
        files.append(str(path))
    done = subprocess.run(
        ["git", "merge-file", "-p", *files],
        check=False,
        capture_output=True,
        text=True,
    )
    assert done.returncode >= 0, done.stderr
    return done.returncode


class State:
    """What the volatile generated files are rendered from."""

    def __init__(self, rows, entries, verifications, tests, skills):
        self.rows = list(rows)
        self.entries = list(entries)
        self.verifications = set(verifications)
        self.tests = set(tests)
        self.skills = list(skills)

    def copy(self):
        return State(
            self.rows, self.entries, self.verifications, self.tests, self.skills
        )

    def add_requirement(self, short, name, test_written=True, fitness=True):
        """A requirement with its verification, and its test if written."""
        test = f"test_{short}_" + name.replace(" ", "_")
        added = self.copy()
        added.rows.append([short, name, "written" if test_written else "pending"])
        added.verifications.add(test)
        if test_written:
            added.tests.add(test)
        if fitness:
            state = "written" if test_written else "pending"
            added.entries.append((short, name, "at every commit", test, state))
        return added

    def add_skill(self, name, unverified):
        added = self.copy()
        added.skills.append(
            al.Skill(
                name=name,
                description="Use when sampling.",
                family="product",
                paths=[f"{name}/**"],
                body="",
                unverified=unverified,
            )
        )
        return added


def by_id(rows):
    return sorted(rows, key=lambda r: [int(n) for n in re.findall(r"\d+", r[0])])


def render(state, by_name=True, with_total=False):
    """The parts of the generated files that grow, by file name."""
    rows = (
        sorted(state.rows, key=al.requirement_row_order)
        if by_name
        else by_id(state.rows)
    )
    entries = state.entries
    pending = generators.render_pending(state.verifications, state.tests)
    if by_name:
        fitness = generators.render_fitness(entries)
    else:
        fitness = "\n".join(
            f"- {s}, {w}, {t}: `{n}` ({x})."
            for s, w, t, n, x in sorted(entries, key=lambda e: int(e[0][1:]))
        )
        names = sorted(
            state.verifications - state.tests,
            key=lambda n: int(n.split("_")[1][1:]),
        )
        pending = "pending = [\n" + "".join(f'  "{n}",\n' for n in names) + "]\n"
    skills = sorted(state.skills, key=lambda s: s.name)
    index = al.skills_index(skills, [])
    if with_total:
        total = sum(s.unverified for s in skills)
        index = index.replace(
            "Globs of", f"Unverified rules in all skills: {total}.\n\nGlobs of"
        )
    return {
        "docs/catalog.md (requirements)": al.requirements_table(rows),
        "docs/catalog.md (fitness functions)": fitness,
        "tests/pending.toml": pending,
        "skills/README.md": index,
        "AGENTS.md (routing)": al.routing_table(skills),
    }


def render_padded_routing(state):
    """The routing as it was rendered until PM-016: a table padded to its widest cell."""
    rows = [
        [f"`{s.name}`", s.family, ", ".join(f"`{p}`" for p in s.paths)]
        for s in sorted(state.skills, key=lambda s: (al.FAMILY_ORDER[s.family], s.name))
    ]
    widths = [max(len(r[i]) for r in rows) for i in range(3)]
    return "\n".join(
        "| " + " | ".join(c.ljust(w) for c, w in zip(r, widths)) + " |" for r in rows
    )


def base_state(model):
    tests = sysml_model.names_of_tests()
    return State(
        al.requirement_rows(model, tests),
        generators.fitness_entries(model, tests),
        sysml_model.verifications(model),
        tests,
        al.skills(),
    )


def merge_faults(base, ours, theirs, tmp_path, **options):
    """Files of the three states that conflict when merged."""
    base_files, our_files, their_files = (
        render(s, **options) for s in (base, ours, theirs)
    )
    return [
        name
        for name in base_files
        if conflicts(base_files[name], our_files[name], their_files[name], tmp_path)
    ]


def test_R150_independent_additions_do_not_conflict_in_generated_files(model, tmp_path):
    base = base_state(model)
    # One branch adds a requirement whose test is written and a skill with an
    # unverified rule; the other adds a requirement whose test is not written
    # yet and another skill, with its own unverified rules.
    ours = base.add_requirement("R9001", "images carry provenance").add_skill(
        "anima-tracing-a-change", 1
    )
    theirs = base.add_requirement(
        "R9002", "update bot groups patches", test_written=False
    ).add_skill("anima-cleaning-a-cache", 2)
    assert merge_faults(base, ours, theirs, tmp_path) == []
    # A skill whose cells are wider than every other one (PM-016).
    wide = "anima-z" + "describing-a-very-long-named-capability-" * 3
    ours = base.add_skill(wide, 0)
    theirs = base.add_skill("anima-cleaning-a-cache", 0)
    assert merge_faults(base, ours, theirs, tmp_path) == []
    # Two requirements whose tests are not written yet.
    ours = base.add_requirement("R9003", "backup restores twice", test_written=False)
    theirs = base.add_requirement("R9004", "tests report coverage", test_written=False)
    assert merge_faults(base, ours, theirs, tmp_path) == []
    # Two requirements added to the model itself, on two branches of git.
    assert not merged_model_conflicts(
        tmp_path,
        MODEL,
        (9001, "imagesCarryProvenance"),
        (9002, "updateBotGroupsPatches"),
    )


def test_R150_independent_additions_do_not_conflict_in_generated_files_detects_violation(
    model, tmp_path
):
    """The check fails for the old renderings (by id, with a total), and for two
    additions that do land in the same place."""
    base = base_state(model)
    ours = base.add_requirement("R9001", "images carry provenance").add_skill(
        "anima-tracing-a-change", 1
    )
    theirs = base.add_requirement(
        "R9002", "update bot groups patches", test_written=False
    ).add_skill("anima-cleaning-a-cache", 2)
    old = merge_faults(base, ours, theirs, tmp_path, by_name=False, with_total=True)
    assert "docs/catalog.md (requirements)" in old
    assert "docs/catalog.md (fitness functions)" in old
    assert "skills/README.md" in old
    # The routing as a table padded to its widest cell: a wider cell rewrites
    # every row, so it conflicts with any other addition (PM-016).
    wide = "anima-z" + "describing-a-very-long-named-capability-" * 3
    one, other = base.add_skill(wide, 0), base.add_skill("anima-cleaning-a-cache", 0)
    padded = render_padded_routing
    assert conflicts(padded(base), padded(one), padded(other), tmp_path)
    ours = base.add_requirement("R9003", "backup restores twice", test_written=False)
    theirs = base.add_requirement("R9004", "tests report coverage", test_written=False)
    assert "tests/pending.toml" in merge_faults(
        base, ours, theirs, tmp_path, by_name=False
    )
    # Same place: two names that sort between the same two neighbours.
    ours = base.add_requirement("R9005", "update bot groups digests")
    theirs = base.add_requirement("R9006", "update bot groups patches")
    assert merge_faults(base, ours, theirs, tmp_path)
    # A merge of identical texts, and of one change, is clean.
    assert conflicts("a\nb\n", "a\nb\n", "a\nb\n", tmp_path) == 0
    assert conflicts("a\nb\n", "a\nx\nb\n", "a\nb\n", tmp_path) == 0
    # The model as one file: two requirements added at the same place conflict.
    one_file = tmp_path / "one_file"
    (one_file).mkdir()
    (one_file / "anima.sysml").write_text(
        "package Anima {\n    part def Toolchain;\n    package Day0 {\n"
        + requirement_text(1, "first", 8)
        + "    }\n\n    // ---- Day 1\n}\n"
    )
    assert merged_model_conflicts(
        tmp_path / "single",
        one_file,
        (9001, "imagesCarryProvenance"),
        (9002, "updateBotGroupsPatches"),
    )
