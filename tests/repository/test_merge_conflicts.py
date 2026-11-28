"""Independent additions do not conflict in generated files (R150, PM-011).

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
"""

import re
import subprocess

import agent_layer as al
import generators
import sysml_model


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
    # Two requirements whose tests are not written yet.
    ours = base.add_requirement("R9003", "backup restores twice", test_written=False)
    theirs = base.add_requirement("R9004", "tests report coverage", test_written=False)
    assert merge_faults(base, ours, theirs, tmp_path) == []


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
