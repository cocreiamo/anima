"""Every step of a workflow calls a command that has a test. R168.

A workflow is run by the platform, so shell written inside it first runs in
production: three times in one day (2026-11-28) it failed there for a reason that
a test on a developer's machine would have shown (PM-010, PM-013, and the first
publishing run). The rule that follows: a workflow step is a call to a command of
the repository, and that command has a test that runs it for real
(`anima-branching-and-releasing`).

The definition of the one thing a `run:` may hold, which is the rule:

  A `run:` value is one or more lines, each of them exactly one invocation
  `mise run <task>`, followed by arguments that are each a literal word or one
  `"$NAME"` of the step's environment. No other command, no `|`, `&`, `;`, `>`,
  `<`, `$(`, backtick, `\\`, `#`, `if`, `for`, `case`, `{`, no `${{ }}` (an
  expression reaches a command through `env:`), no parsing and no choice: whatever
  decides is in the command.

The tasks are in `mise-tasks/<area>/<name>` (task `<area>:<name>`) or `mise.toml`.
A command has a test when a test of `tests/` names it, which is how the tests of
`tests/ci/` run a command (`task("<name>")` runs `ci:<name>`), or when it is in the
short table below with its reason: a command that is itself a verification, or
that the verification cannot run without.
"""

import re
import tomllib

import yaml
from sysml_model import ROOT

WORKFLOWS = ROOT / ".github" / "workflows"
THIS_FILE = "test_workflow_steps.py"

# One invocation of a task of the repository, with literal or environment arguments.
CALL = re.compile(
    r'mise run (?P<task>[a-z][a-z0-9:_-]*)(?: (?:"\$[A-Z][A-Z0-9_]*"|[A-Za-z0-9_./=@:+-]+))*'
)

# Commands that have no test that names them, each with the reason. A command
# that a workflow no longer calls is removed from here (the check says so).
VERIFIED_THROUGH = {
    "ci:test": "is the integration tests of the commands that the workflows call",
    "engine:test": "is the system tests",
    "engine:image": "builds the image that the system tests start and fail without",
    "engine:build": "builds the inner images that the system tests start",
    "promote:verify": "runs every check and the system tests: it is the verification",
}

# A workflow that still holds shell, with the reason. Dated 2026-11-28; the change
# that converts it removes the entry (the check fails on an entry that it no
# longer needs). The founder approved the rule on the day; the conversion of the
# promotion is under way in another change.
UNCONVERTED = {
    "promote.yml": (
        "2026-11-28: the promotion's shell (the commit to promote, the archive of "
        "the image, the publish, the move of the branch, the release) is being "
        "moved into `mise-tasks/promote/` by another change, which removes this entry"
    ),
}


def run_steps(workflow):
    """[(job id, step name, text of its `run:`)] of a parsed workflow."""
    found = []
    for job_id, job in (workflow.get("jobs") or {}).items():
        for index, step in enumerate(job.get("steps") or []):
            if "run" in step:
                found.append((job_id, step.get("name") or f"#{index + 1}", step["run"]))
    return found


def step_faults(workflow):
    """The steps of one workflow that are not one call of a command, and the
    commands that it calls: (faults, commands)."""
    faults, commands = [], []
    for job_id, name, script in run_steps(workflow):
        lines = [line.strip() for line in str(script).splitlines() if line.strip()]
        if not lines:
            faults.append(f"{job_id} / {name}: an empty step")
        for line in lines:
            call = CALL.fullmatch(line)
            if call:
                commands.append(call["task"])
            else:
                faults.append(
                    f"{job_id} / {name}: `{line}` is not one call of a command"
                )
    return faults, commands


def defined_tasks():
    """The tasks of the repository: the files of mise-tasks/ and the tasks of mise.toml."""
    found = {
        str(p.relative_to(ROOT / "mise-tasks")).replace("/", ":")
        for p in (ROOT / "mise-tasks").rglob("*")
        if p.is_file()
    }
    found |= set(tomllib.loads((ROOT / "mise.toml").read_text()).get("tasks", {}))
    return found


def named_by_a_test(command, test_texts):
    """Whether a test runs the command: it names `<area>:<name>`, its path
    `mise-tasks/<area>/<name>`, or, for the commands of `ci`, `task("<name>"`."""
    path = "mise-tasks/" + command.replace(":", "/")
    needles = [command, path]
    if command.startswith("ci:"):
        needles.append(f'task("{command.removeprefix("ci:")}"')
    return any(n in text for text in test_texts for n in needles)


def command_faults(commands, defined, test_texts, through, also_called=()):
    """The commands that a workflow calls and that do not exist, or have no test."""
    faults = []
    for command in sorted(set(commands)):
        if command not in defined:
            faults.append(f"{command} is not a task of the repository")
        elif command not in through and not named_by_a_test(command, test_texts):
            faults.append(f"{command} has no test that runs it")
    for command, reason in sorted(through.items()):
        if command not in commands and command not in also_called:
            faults.append(f"{command} is excused but no workflow calls it")
        if not reason:
            faults.append(f"{command} is excused without a reason")
    return faults


def workflow_faults(workflows, defined, test_texts, through, unconverted):
    """Every fault of the set of workflows: {file name: parsed workflow}."""
    faults, commands, excused_calls = [], [], []
    for name, workflow in sorted(workflows.items()):
        found, called = step_faults(workflow)
        if name in unconverted:
            if not unconverted[name]:
                faults.append(f"{name} is excused without a reason")
            if not found:
                faults.append(
                    f"{name} is converted: remove its entry of the exceptions"
                )
            excused_calls += called
            continue
        faults += [f"{name}: {f}" for f in found]
        commands += called
    # The commands of an unconverted workflow are not asked to have a test yet; they
    # still count as called, so that an excuse is not called stale for them.
    return faults + command_faults(
        commands, defined, test_texts, through, also_called=excused_calls
    )


def read_workflows():
    return {
        p.name: yaml.safe_load(p.read_text()) for p in sorted(WORKFLOWS.glob("*.yml"))
    }


def read_tests():
    return [
        p.read_text()
        for p in sorted((ROOT / "tests").rglob("*.py"))
        if p.name != THIS_FILE
    ]


def test_R168_workflow_steps_call_tested_commands():
    """Proves, from the text of every workflow, that each `run:` is one call of a
    command of the repository with literal or environment arguments, that each
    command exists, and that a test of `tests/` runs it, or it is a verification
    itself. The tests of the commands are R169 to R174 and R165 (`tests/ci/`).
    The shared workflows of the organization are not read here."""
    workflows = read_workflows()
    assert workflows, "no workflow found"
    assert (
        workflow_faults(
            workflows, defined_tasks(), read_tests(), VERIFIED_THROUGH, UNCONVERTED
        )
        == []
    )


def parse(text):
    return yaml.safe_load(text)


def test_R168_workflow_steps_call_tested_commands_detects_violation():
    def one(script):
        return {
            "w.yml": parse(
                "jobs:\n  j:\n    steps:\n      - name: s\n        run: |\n"
                + "".join(f"          {line}\n" for line in script.splitlines())
            )
        }

    defined = {"ci:a", "ci:b", "check"}
    tests = ['task("a")']
    through = {"check": "is the verification"}

    def faults(script, **override):
        arguments = {
            "defined": defined,
            "test_texts": tests,
            "through": through,
            "unconverted": {},
            **override,
        }
        return workflow_faults(one(script), **arguments)

    # The allowed glue: one call, or several, one per line; literal and environment arguments.
    assert faults("mise run ci:a") == ["check is excused but no workflow calls it"]
    assert faults('mise run ci:a "$FORK" --flag=1 path/x\nmise run check') == []
    # Everything else is logic.
    for script in (
        "echo hello",
        "mise run ci:a | tee x",
        "mise run ci:a && mise run check",
        "mise run ci:a; mise run check",
        "mise run ci:a > out",
        "mise run ci:a $(date)",
        "mise run ci:a `date`",
        "mise run ci:a ${{ github.sha }}",
        "mise run ci:a ${FORK}",
        "mise run ci:a # why",
        "mise run ci:a \\\n  x",
        "if true; then mise run ci:a; fi",
        "set -euo pipefail\nmise run ci:a",
        "podman load --input x",
        "gh api repos/x",
        "mise exec python -- python x",
        "mise run",
        "",
    ):
        assert faults(script), script
    # A command that does not exist, or that no test runs, or an excuse that is stale.
    assert faults("mise run ci:missing\nmise run check")
    assert faults("mise run ci:b\nmise run check")
    assert faults("mise run ci:a\nmise run check", test_texts=[])
    assert faults("mise run ci:a\nmise run check", through={"check": ""})
    assert faults("mise run ci:a", through={"check": "x", "ci:old": "x"})
    # Another form of naming that a test runs the command.
    assert faults("mise run ci:b\nmise run check", test_texts=["mise run ci:b"]) == []
    assert faults("mise run ci:b\nmise run check", test_texts=["mise-tasks/ci/b"]) == []
    # The exception of an unconverted workflow: needed, with a reason, and not stale.
    shell = one("echo shell")
    kept = {"w.yml": "why"}
    assert workflow_faults(shell, defined, tests, {}, kept) == []
    assert workflow_faults(shell, defined, tests, {}, {"w.yml": ""})
    assert workflow_faults(one("mise run ci:a"), defined, tests, {}, kept)
    assert workflow_faults(shell, defined, tests, {}, {})
