"""The agent layer: how agents are told what to read and what they may do.

Everything here is derived from neutral files, so that the vendor-specific
files are generated output (R38):

- skills/anima-*.md: the skills, one schema for every family (R72);
- agents/<role>.md: the roles; `.claude/agents/<role>.md` is generated (R77);
- the routing table of AGENTS.md and `.claude/rules/<skill>.md`, from the
  `paths` of the skills (R76);
- `.claude/settings.json`: refusals and one advisory hook (R86);
- docs/catalog.md: what exists, so that nobody reinvents it (R87).

The front matter of these files is a small, flat subset of YAML read by
`parse_yaml`: scalars, lists of scalars and lists of mappings, so that the
generators run with nothing but the standard library.
"""

import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = "mise run generate"

# ---- A reader for the YAML subset of our front matter ------------------------


def split_front_matter(text):
    """(front matter, body) of a document; the front matter is None if absent."""
    match = re.match(r"---\n(.*?)\n---\n?(.*)\Z", text, re.DOTALL)
    return (match[1], match[2]) if match else (None, text)


def _scalar(value):
    value = value.strip()
    if value in ("", "~", "null"):
        return ""
    if value == "[]":
        return []
    if value.startswith('"'):
        return json.loads(value)
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("''", "'")
    if value.startswith("[") and value.endswith("]"):
        return [_scalar(v) for v in value[1:-1].split(",")]
    return value


def parse_yaml(block):
    """A mapping of keys to scalars, lists of scalars or lists of mappings."""
    lines = [
        line
        for line in block.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    found = {}
    i = 0
    while i < len(lines):
        match = re.fullmatch(r"([A-Za-z_][\w-]*):(?:\s+(.*))?", lines[i].rstrip())
        if not match:
            raise ValueError(f"cannot read front matter line: {lines[i]!r}")
        key, value = match[1], match[2] or ""
        i += 1
        if re.fullmatch(r"[>|][+-]?", value):
            # A folded or literal block scalar, which the backlog tool writes for
            # a long title: the more indented lines that follow.
            block_lines = []
            while i < len(lines) and lines[i].startswith((" ", "\t")):
                block_lines.append(lines[i].strip())
                i += 1
            found[key] = (" " if value[0] == ">" else "\n").join(block_lines)
            continue
        if value:
            found[key] = _scalar(value)
            continue
        items = []
        while i < len(lines) and lines[i].startswith((" ", "\t")):
            stripped = lines[i].strip()
            if stripped.startswith("- ") or stripped == "-":
                rest = stripped[1:].strip()
                pair = re.fullmatch(r"([A-Za-z_][\w-]*):(?:\s+(.*))?", rest)
                if pair:
                    items.append({pair[1]: _scalar(pair[2] or "")})
                else:
                    items.append(_scalar(rest))
            else:
                pair = re.fullmatch(r"([A-Za-z_][\w-]*):(?:\s+(.*))?", stripped)
                if not pair or not items or not isinstance(items[-1], dict):
                    raise ValueError(f"cannot read front matter line: {lines[i]!r}")
                items[-1][pair[1]] = _scalar(pair[2] or "")
            i += 1
        found[key] = items
    return found


def read_document(path):
    """(front matter mapping, body) of a Markdown file with front matter."""
    block, body = split_front_matter(Path(path).read_text())
    if block is None:
        raise ValueError(f"{path}: no front matter")
    return parse_yaml(block), body


# ---- Skills (R72, R73) ---------------------------------------------------------

SECTIONS = [
    "Use this when",
    "Rules",
    "Questions to answer before proposing",
    "Where the result goes",
]
SKILL_KEYS = {"name", "description", "family", "paths"}
FAMILIES = ("product", "capability", "technology")
UNVERIFIED = re.compile(r"^\d+\.\s+Unverified:", re.MULTILINE)


def family_of(name):
    """The family a skill file name stands for."""
    if name.startswith("anima-tech-"):
        return "technology"
    if re.fullmatch(r"anima-[a-z]+-design", name):
        return "capability"
    return "product"


def capability_of(name):
    """`access` for `anima-access-design`."""
    return name.removeprefix("anima-").removesuffix("-design")


def sections_of(body):
    return re.findall(r"^## (.+?)\s*$", body, re.MULTILINE)


def rules_section(body):
    match = re.search(r"^## Rules\s*$(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
    return match[1] if match else ""


def unverified_count(body):
    """Rules that start with the marker `Unverified:`."""
    return len(UNVERIFIED.findall(rules_section(body)))


def skill_schema_faults(stem, text):
    """What keeps a skill from having the one shape of every skill."""
    block, body = split_front_matter(text)
    if block is None:
        return ["no front matter"]
    try:
        fields = parse_yaml(block)
    except ValueError as error:
        return [str(error)]
    faults = []
    if set(fields) != SKILL_KEYS:
        faults.append(
            f"front matter keys are {sorted(fields)}, not {sorted(SKILL_KEYS)}"
        )
    if fields.get("name") != stem:
        faults.append("name differs from the file name")
    description = fields.get("description")
    if not isinstance(description, str) or not description.startswith("Use when"):
        faults.append("description does not say when to use the skill")
    if fields.get("family") not in FAMILIES:
        faults.append(f"family {fields.get('family')!r} is not one of {FAMILIES}")
    elif fields["family"] != family_of(stem):
        faults.append(f"family {fields['family']} does not match the file name")
    paths = fields.get("paths")
    if not isinstance(paths, list) or not all(isinstance(p, str) and p for p in paths):
        faults.append("paths is not a list of globs")
    if sections_of(body) != SECTIONS:
        faults.append(f"sections are {sections_of(body)}, not {SECTIONS}")
    if not re.search(r"^1\. ", rules_section(body), re.MULTILINE):
        faults.append("Rules has no numbered rule")
    return faults


@dataclass
class Skill:
    name: str
    description: str
    family: str
    paths: list
    body: str
    unverified: int


def read_skill(path):
    fields, body = read_document(path)
    return Skill(
        name=fields["name"],
        description=fields["description"],
        family=fields["family"],
        paths=list(fields["paths"]),
        body=body,
        unverified=unverified_count(body),
    )


def skills(root=ROOT):
    return [read_skill(p) for p in sorted((root / "skills").glob("anima-*.md"))]


def front_matter(path):
    """`name` and `description` of a skill, as the pointers need them."""
    skill = read_skill(path)
    return {"name": skill.name, "description": skill.description}


# ---- Path globs (R74, R75, R76) ------------------------------------------------


def glob_regex(pattern):
    """A glob as a regular expression: `**` crosses directories, `*` and `?`
    stay inside one, and `dir/**` also matches `dir` itself."""
    out = ""
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pattern.startswith("/**", i) and i + 3 == len(pattern):
            out += "(?:/.*)?"
            i += 3
        elif pattern.startswith("**", i):
            out += ".*"
            i += 2
        elif pattern[i] == "*":
            out += "[^/]*"
            i += 1
        elif pattern[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pattern[i])
            i += 1
    return re.compile(out)


def glob_matches(pattern, path):
    return bool(glob_regex(pattern).fullmatch(path))


def not_yet_present(root=ROOT):
    """The globs that match nothing yet, in their one place."""
    data = tomllib.loads((root / "skills" / "not-yet-present.toml").read_text())
    return list(data["paths"])


# ---- Routing: the table of AGENTS.md and the path rules (R76) -------------------

ROUTING_BEGIN = "<!-- routing:begin -->"
ROUTING_END = "<!-- routing:end -->"
FAMILY_ORDER = {"product": 0, "capability": 1, "technology": 2}


def pad_table(header, rows):
    """A Markdown table padded the way Prettier pads it."""
    widths = [max(len(r[i]) for r in [header, *rows]) for i in range(len(header))]

    def line(cells):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    rule = "| " + " | ".join("-" * w for w in widths) + " |"
    return "\n".join([line(header), rule, *[line(r) for r in rows]])


def routing_table(all_skills):
    rows = []
    for skill in sorted(all_skills, key=lambda s: (FAMILY_ORDER[s.family], s.name)):
        work = ", ".join(f"`{p}`" for p in skill.paths) or "any design decision"
        rows.append([f"`{skill.name}`", skill.family, work])
    return pad_table(["Skill", "Family", "Work on"], rows)


def agents_md(text, all_skills):
    """AGENTS.md with the routing table between its markers regenerated."""
    begin = text.index(ROUTING_BEGIN) + len(ROUTING_BEGIN)
    end = text.index(ROUTING_END)
    return text[:begin] + "\n\n" + routing_table(all_skills) + "\n\n" + text[end:]


def rule_file(skill):
    """The path rule that tells the agent which skill to load for these paths."""
    paths = "".join(f"  - {json.dumps(p)}\n" for p in skill.paths)
    return (
        "---\n"
        f"# Generated by `{TASK}` from skills/{skill.name}.md. Do not edit.\n"
        f"paths:\n{paths}"
        "---\n\n"
        f"Before changing anything under these paths, load the skill "
        f"`{skill.name}` (`skills/{skill.name}.md`).\n"
    )


def skill_pointer(skill):
    name = skill.name
    return (
        "---\n"
        f"# Generated by `{TASK}` from skills/{name}.md. Do not edit.\n"
        f"name: {name}\n"
        f"description: {json.dumps(skill.description, ensure_ascii=False)}\n"
        "---\n\n"
        f"@../../../skills/{name}.md\n"
        f"If the line above was not expanded, read `skills/{name}.md` in the "
        "repository root and follow it.\n"
    )


def skills_index(all_skills, not_yet):
    """skills/README.md: every skill with its family and its `Unverified:` count."""
    out = [
        f"<!-- Generated by `{TASK}` from the skill files. Do not edit. -->\n",
        "# Skills\n",
        (
            "Design criteria of Anima as skill documents for any AI coding agent. "
            "Load the one that matches the work before you start; `AGENTS.md` has "
            "the table that says which one for which paths.\n"
        ),
        (
            "Three families, one schema: `## Use this when`, `## Rules`, "
            "`## Questions to answer before proposing`, `## Where the result goes`, "
            "with the front matter `name`, `description`, `family` and `paths`. A "
            "product skill is named for a kind of work. A capability skill is named "
            "`anima-<capability>-design` and covers the directories of one capability under `engine/` or "
            "`config/`. A technology skill is named `anima-tech-<technology>`, "
            "records how that technology actually behaves, and is retired when the "
            "technology is replaced. A rule that nobody has seen working starts with "
            "`Unverified:`; the count per skill shows how much is still to be "
            "shown.\n"
        ),
    ]
    for family in FAMILIES:
        members = [s for s in all_skills if s.family == family]
        out.append(f"## {family.capitalize()} skills\n")
        out.append(
            "\n".join(
                f"- [`{s.name}`]({s.name}.md) ({s.unverified} unverified): "
                f"{s.description}"
                for s in members
            )
            + "\n"
        )
    out.append(
        "Globs of `paths` that match nothing yet, listed in "
        "`not-yet-present.toml` and in no other place: "
        + (", ".join(f"`{p}`" for p in not_yet) or "none")
        + ".\n"
    )
    out.append(
        "The content lives here, in plain Markdown with no vendor syntax. For "
        "Claude Code, `.claude/skills/<name>/SKILL.md` is a thin pointer and "
        "`.claude/rules/<name>.md` names the skill to load for its paths; both "
        "are generated. Another agent vendor wires its own pointers the same "
        "way: create its native skill or rules entry, put the trigger "
        "description in it, and make it import or tell the agent to read "
        "`skills/<name>.md`, never copy the content.\n"
    )
    return "\n".join(out)


# ---- Roles (R77, R78) ------------------------------------------------------------

ROLE_KEYS = {"name", "description", "tier", "model_tier", "may", "may_not"}
TIERS = ("coordinator", "implementer", "reviewer", "spike", "explorer")
MODEL_TIERS = ("top", "standard")
# The vendor mapping of the neutral statement `model_tier`: top is the vendor's
# most capable model, standard its mid model.
MODELS = {"top": "opus", "standard": "sonnet"}
# What `may` allows, as tools of the vendor.
TOOLS = {
    "read": ["Read"],
    "search": ["Grep", "Glob"],
    "edit": ["Edit", "Write"],
    "run": ["Bash"],
    "fetch": ["WebFetch", "WebSearch"],
    "delegate": ["Agent"],
}
# Decided: the model tier of each tier of role, and the tiers that only read.
TIER_MODEL_TIER = {
    "coordinator": "top",
    "implementer": "standard",
    "reviewer": "top",
    "spike": "top",
    "explorer": "standard",
}
READ_ONLY_TIERS = ("reviewer", "spike", "explorer")
ROLE_SECTIONS = [
    "What it is for",
    "What it reads first",
    "What it produces",
    "What it must never do",
]


def role_faults(stem, text):
    block, body = split_front_matter(text)
    if block is None:
        return ["no front matter"]
    try:
        fields = parse_yaml(block)
    except ValueError as error:
        return [str(error)]
    faults = []
    if set(fields) != ROLE_KEYS:
        faults.append(
            f"front matter keys are {sorted(fields)}, not {sorted(ROLE_KEYS)}"
        )
    if fields.get("name") != stem:
        faults.append("name differs from the file name")
    if fields.get("tier") not in TIERS:
        faults.append(f"tier {fields.get('tier')!r} is not one of {TIERS}")
    if fields.get("model_tier") not in MODEL_TIERS:
        faults.append(
            f"model_tier {fields.get('model_tier')!r} is not one of {MODEL_TIERS}"
        )
    may = fields.get("may")
    if not isinstance(may, list) or not may or not set(may) <= set(TOOLS):
        faults.append(f"may is not a list drawn from {sorted(TOOLS)}")
    if (
        fields.get("tier") in TIER_MODEL_TIER
        and fields.get("model_tier") != TIER_MODEL_TIER[fields["tier"]]
    ):
        faults.append(
            f"a {fields['tier']} runs on the {TIER_MODEL_TIER[fields['tier']]} model tier"
        )
    if fields.get("tier") in READ_ONLY_TIERS and "edit" in (may or []):
        faults.append(f"a {fields['tier']} may not edit")
    if not isinstance(fields.get("may_not"), list) or not fields.get("may_not"):
        faults.append("may_not is not a non-empty list")
    if not fields.get("description"):
        faults.append("no description")
    if sections_of(body) != ROLE_SECTIONS:
        faults.append(f"sections are {sections_of(body)}, not {ROLE_SECTIONS}")
    return faults


@dataclass
class Role:
    name: str
    description: str
    tier: str
    model_tier: str
    may: list
    may_not: list
    body: str


def read_role(path):
    fields, body = read_document(path)
    return Role(
        name=fields["name"],
        description=fields["description"],
        tier=fields["tier"],
        model_tier=fields["model_tier"],
        may=list(fields["may"]),
        may_not=list(fields["may_not"]),
        body=body,
    )


def roles(root=ROOT):
    return [read_role(p) for p in sorted((root / "agents").glob("*.md"))]


def tools_for(may):
    return [tool for permission in may for tool in TOOLS[permission]]


def vendor_role(role):
    """`.claude/agents/<name>.md`: the subagent file the vendor reads."""
    return (
        "---\n"
        f"# Generated by `{TASK}` from agents/{role.name}.md. Do not edit.\n"
        f"name: {role.name}\n"
        f"description: {json.dumps(role.description, ensure_ascii=False)}\n"
        f"model: {MODELS[role.model_tier]}\n"
        f"tools: {', '.join(tools_for(role.may))}\n"
        "---\n" + role.body
    )


# ---- Settings and the advisory hook (R86, R92) -------------------------------------

LOCK_FILES = ["mise.lock", "uv.lock", "MODULE.bazel.lock", ".mise/locks/**"]
# A bare interpreter runs outside the task runner, where the bytecode prefix and
# the pinned version are not set (PM-004, R107). `mise exec -- python` and
# `mise run` start with another word and are not matched.
BARE_INTERPRETERS = ["Bash(python:*)", "Bash(python3:*)"]
HOOK = ".claude/hooks/new-file-reminder.sh"


def settings_json(refused):
    """`.claude/settings.json`: refusals only (no permission is granted) and
    one advisory hook. `refused` is the list of generated files."""
    deny = [f"Edit(/{path})" for path in refused]
    deny += ["Edit(/third_party/**)"]
    deny += [f"Edit(/{path})" for path in LOCK_FILES]
    deny += BARE_INTERPRETERS
    settings = {
        "$schema": "https://json.schemastore.org/claude-code-settings.json",
        "permissions": {"deny": deny},
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "${CLAUDE_PROJECT_DIR}/" + HOOK,
                            "args": [],
                        }
                    ],
                }
            ]
        },
    }
    return json.dumps(settings, indent=2) + "\n"


# ---- The catalog (R87) ---------------------------------------------------------------


def humanize(camel):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", camel).lower()


def task_descriptions(root=ROOT):
    """{mise task: description}, from mise.toml and the file tasks."""
    tasks = {}
    config = tomllib.loads((root / "mise.toml").read_text()).get("tasks", {})
    for name, entry in config.items():
        tasks[name] = entry.get("description", "")
    for path in sorted((root / "mise-tasks").rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".py":
            continue
        parts = list(path.relative_to(root / "mise-tasks").parts)
        if parts[-1] == "_default":
            parts = parts[:-1]
        match = re.search(
            r'^#\s*MISE\s+description="([^"]*)"', path.read_text(), re.MULTILINE
        )
        tasks[":".join(parts)] = match[1] if match else ""
    return dict(sorted(tasks.items()))


def capability_keys(all_skills, root=ROOT):
    keys = {capability_of(s.name) for s in all_skills if s.family == "capability"}
    for top in ("engine", "config"):
        if (root / top).is_dir():
            keys |= {p.name for p in (root / top).iterdir() if p.is_dir()}
    return keys


def synonyms(root=ROOT):
    path = root / "docs" / "catalog-synonyms.toml"
    return tomllib.loads(path.read_text()) if path.exists() else {}


def catalog_keys(model, all_skills, all_roles, components, tasks, root=ROOT):
    """Every name an entry of the synonyms file may stand for."""
    import sysml_model as m

    keys = capability_keys(all_skills, root)
    port = m.named(model, "Port")
    keys |= {humanize(model[p]["declaredName"]) for p in m.specializations(model, port)}
    keys |= {c["name"] for c in components}
    keys |= {r.name for r in all_roles} | {s.name for s in all_skills} | set(tasks)
    return keys


def port_rows(model):
    import sysml_model as m

    stand_ins = m.specializations(model, m.named(model, "StandIn"))
    rows = []
    for port in sorted(m.specializations(model, m.named(model, "Port"))):
        defaults = m.usages_of(model, port)
        alternatives = []
        for definition in sorted(m.specializations(model, port)):
            kind = "stand-in" if definition in stand_ins else "alternative"
            alternatives += [f"{u} ({kind})" for u in m.usages_of(model, definition)]
        rows.append(
            [
                humanize(model[port]["declaredName"]),
                ", ".join(defaults) or "none",
                ", ".join(alternatives) or "none",
            ]
        )
    return sorted(rows)


def requirement_row_order(row):
    """Rows by name, then id. Not by id: a new requirement takes the next id, so
    two branches that each add one would insert at the same place, the end, and
    conflict. By name they insert where their names fall (R150)."""
    return row[1], [int(n) for n in re.findall(r"\d+", row[0])]


def requirements_table(rows):
    return "| Id | Name | Verification |\n| --- | --- | --- |\n" + "\n".join(
        f"| {a} | {b} | {c} |" for a, b, c in rows
    )


def requirement_rows(model, tests):
    import sysml_model as m

    found = m.verifications(model)
    rows = []
    for element in model.values():
        if not m.is_requirement(model, element):
            continue
        names = sorted(n for n, t in found.items() if element["@id"] in t)
        if not names:
            state = "see its parts"
        elif all(n in tests for n in names):
            state = "written"
        else:
            state = "pending"
        rows.append(
            [
                element["declaredShortName"],
                humanize(element["declaredName"]),
                state,
            ]
        )
    return sorted(rows, key=requirement_row_order)


def tool_names(root=ROOT):
    """The tools pinned in mise.toml, by name; versions live in mise.toml alone."""
    return sorted(tomllib.loads((root / "mise.toml").read_text()).get("tools", {}))


def workflow_rows(root=ROOT):
    """[file, name, triggers] for each workflow of .github/workflows/."""
    rows = []
    for path in sorted((root / ".github" / "workflows").glob("*.yml")):
        text = path.read_text()
        name = re.search(r"^name:\s*(.+?)\s*$", text, re.MULTILINE)
        block = re.search(
            r"^on:\s*(.*?)\n(?=\S)", text + "\nend", re.MULTILINE | re.DOTALL
        )
        triggers = []
        if block:
            inline = re.match(r"\[(.*)\]", block[1].split("\n")[0].strip())
            if inline:
                triggers = [t.strip() for t in inline[1].split(",")]
            else:
                triggers = re.findall(r"^  ([a-z_]+):", block[0], re.MULTILINE)
        rows.append(
            [
                f"`{path.name}`",
                name[1].strip("\"'") if name else "",
                ", ".join(triggers),
            ]
        )
    return rows


def catalog(
    model, tests, all_skills, all_roles, components, tasks, words, fitness="", root=ROOT
):
    """docs/catalog.md: what exists, so that an agent does not reinvent it."""
    out = [
        f"<!-- Generated by `{TASK}`. Do not edit. -->\n",
        "# Catalog of what exists\n",
        (
            "Look here before building something. Each section is derived from its "
            "source; the words that help to find an entry are in "
            "`docs/catalog-synonyms.toml`. Requirements and fitness functions are "
            "listed by name, not by id (R150).\n"
        ),
        "## Ports, their default adapter and their stand-in\n",
        "| Port | Default adapter | Alternatives |\n| --- | --- | --- |\n"
        + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in port_rows(model))
        + "\n",
        "## Requirements and their verification\n",
        requirements_table(requirement_rows(model, tests)) + "\n",
        "## Components\n",
        "| Component | Role |\n| --- | --- |\n"
        + "\n".join(f"| {c['name']} | {c['role']} |" for c in components)
        + "\n",
        "## Tasks (`mise run <task>`)\n",
        "| Task | What it does |\n| --- | --- |\n"
        + "\n".join(f"| `{n}` | {d} |" for n, d in tasks.items())
        + "\n",
        "## Tools (`mise.toml`)\n",
        ", ".join(f"`{t}`" for t in tool_names(root)) + "\n",
        "## Workflows (`.github/workflows/`)\n",
        "| Workflow file | Name | Triggers |\n| --- | --- | --- |\n"
        + "\n".join(f"| {a} | {b} | {c} |" for a, b, c in workflow_rows(root))
        + "\n",
        "## Fitness functions\n",
        (
            "Requirements marked as fitness functions in the model, when each runs "
            "and its test.\n"
        ),
        fitness + "\n",
        "## Skills\n",
        "\n".join(f"- `{s.name}` ({s.family})" for s in all_skills) + "\n",
        "## Roles\n",
        "\n".join(f"- `{r.name}` ({r.tier}): {r.description}" for r in all_roles)
        + "\n",
        "## Words that find an entry\n",
        "\n".join(f"- {k}: {', '.join(v)}" for k, v in sorted(words.items())) + "\n",
    ]
    return "\n".join(out)
