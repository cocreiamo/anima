"""Texts that do not age (R57): a skill and a requirement name an adopted thing
by its role; the version is stated in the register that pins it, and as dated
evidence."""

import re

from repo_facts import components, load_toml, tool_images
from sysml_model import ROOT, requirement_docs

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
EVIDENCE = re.compile(r"\bobserved\b", re.IGNORECASE)


def tool_names(tools):
    """`pipx:reuse` is reuse, `github:owner/adrs` is adrs."""
    return {re.split(r"[:/]", key)[-1] for key in tools}


def pinned_versions(components, tools):
    """The versions that the registers pin and that a text must not repeat: the
    dotted versions of the components and of the tools (`18.7`, `6.6.0-26`,
    `3.13.18`). A version with no dot (a bare `45`) is left out: it cannot be told
    from any other number."""
    values = [c["version"] for c in components] + [str(v) for v in tools.values()]
    # A build suffix after `+` (`21.0.13+9.0.LTS`) is not part of the version.
    return sorted(
        {
            m
            for v in values
            for m in re.findall(r"\d+(?:\.\d+)+(?:-\d+)?", v.split("+")[0])
        }
    )


def names_for_versions(components, tools):
    """Names that may be followed by a version: the components' and the tools'."""
    return sorted({c["name"] for c in components} | tool_names(tools))


def blocks(text):
    """A text in blocks: paragraphs, and each item of a list on its own."""
    block = []
    for line in text.splitlines():
        starts_item = re.match(r"\s*(?:[-*]|\d+\.)\s", line)
        if not line.strip() or starts_item:
            if block:
                yield "\n".join(block)
            block = [] if not line.strip() else [line]
        else:
            block.append(line)
    if block:
        yield "\n".join(block)


def versions_stated(text, versions, names):
    """Versions in a text: a pinned version as a word of its own, or a component
    or tool name followed by a number (`PostgreSQL 18`, `podman 5`)."""
    found = []
    for version in versions:
        pattern = rf"(?<![\w.])v?{re.escape(version)}(?![\w]|\.\d)"
        found += [m.group(0) for m in re.finditer(pattern, text)]
    for name in names:
        pattern = rf"(?<![\w-]){re.escape(name)}[ -]v?\d+(?:\.\d+)*(?![\w])"
        found += [m.group(0) for m in re.finditer(pattern, text, re.IGNORECASE)]
    return found


def is_dated_evidence(block):
    """Dated evidence: a block that says it was observed and carries an ISO date,
    e.g. "All observed on 2026-11-27 with OpenBao 2.7.3"."""
    return bool(DATE.search(block) and EVIDENCE.search(block))


def aging_faults(texts, versions, names, evidence_allowed):
    """{name: [versions]} of the texts that state a version outside dated
    evidence. Requirement texts allow no evidence."""
    faults = {}
    for name, text in texts.items():
        found = []
        for block in blocks(text):
            if evidence_allowed and is_dated_evidence(block):
                continue
            found += versions_stated(block, versions, names)
        if found:
            faults[name] = found
    return faults


def registered():
    tools = load_toml("mise.toml")["tools"]
    shipped = components() + tool_images()
    return pinned_versions(shipped, tools), names_for_versions(shipped, tools)


def test_R57_texts_do_not_age(model):
    versions, names = registered()
    assert versions and names
    skills = {
        str(p.relative_to(ROOT)): p.read_text()
        for p in sorted((ROOT / "skills").glob("*.md"))
    }
    assert skills, "no skill found"
    wrong = aging_faults(skills, versions, names, evidence_allowed=True)
    wrong |= aging_faults(requirement_docs(model), versions, names, False)
    assert not wrong, f"texts that state a version: {wrong}"


def test_R57_texts_do_not_age_detects_violation():
    versions = pinned_versions(
        [{"version": "18.7"}, {"version": "45"}],
        {"tool": "1.2.3", "java": "temurin-21.0.13+9.0.LTS"},
    )
    assert versions == ["1.2.3", "18.7", "21.0.13"]
    names = names_for_versions([{"name": "postgresql"}], {"pipx:reuse": "6.3.0"})
    assert names == ["postgresql", "reuse"]

    def faults(text, evidence=True):
        return aging_faults({"t": text}, versions, names, evidence)

    assert faults("Runs on 18.7 only.")
    assert faults("Use PostgreSQL 18 here.")
    assert faults("reuse 6 is needed")
    assert faults("Pinned at 1.2.3.")
    assert faults("Write postgresql-17 rules.")
    assert faults("It is a plain text with no version.") == {}
    assert faults("Forty-five and 18.70 and R1.2 are other numbers.") == {}
    observed = "All observed on 2026-11-27 with PostgreSQL 18.7 here."
    assert faults(observed) == {}
    assert faults(observed, evidence=False)
    assert faults("Seen on 2026-11-27 with PostgreSQL 18.7.")  # not marked observed
    assert faults("Observed with PostgreSQL 18.7, no date.")  # no date
    # Evidence covers its own paragraph or list item only.
    assert faults(observed + "\n\n- but PostgreSQL 18.7 again.")
