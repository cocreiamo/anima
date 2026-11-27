"""Fitness functions: automated, objective checks of properties of the
architecture (`anima-specifying-requirements`). R53 to R56.

Each check is a function of its inputs; its companion test
(`<name>_detects_violation`) feeds it a deliberately wrong input.
"""

import re
from pathlib import Path
from urllib.parse import urlparse

from repo_facts import components, tool_images
from sysml_model import (
    NEGATIVE_SUFFIX,
    ROOT,
    defined_function_names,
    fitness_functions,
    port_part_names,
    requirement_docs,
    threshold_types,
    thresholds,
)

# ---- R53: no product in a requirement ---------------------------------------


def product_terms(components, part_names):
    """The names of the products, derived from the registers: each component's
    name, the segments of its upstream address, its image path and its
    submodule path, and the names of the parts of the model that fill a port.
    Nothing is listed by hand."""
    terms = set(part_names)
    for c in components:
        terms.add(c["name"])
        for key in ("upstream", "image"):
            if c.get(key):
                address = urlparse(c[key] if "//" in c[key] else "//" + c[key])
                terms.update(s for s in address.path.split("/") if s)
        if c.get("submodule"):
            terms.add(c["submodule"].rsplit("/", 1)[-1])
    return sorted(terms)


def term_pattern(term):
    """A term as a case-insensitive word, with `-`, `_` or a space optional
    between its parts: `pg_oidc_validator` finds `pgOidcValidator` too."""
    parts = [re.escape(p) for p in re.split(r"[-_ ]+", term) if p]
    return re.compile(
        r"(?<![A-Za-z0-9])" + r"[-_ ]?".join(parts) + r"(?![A-Za-z0-9])", re.IGNORECASE
    )


def products_named(docs, terms):
    """The terms found in each requirement text: {requirement: [terms]}."""
    patterns = {term: term_pattern(term) for term in terms}
    found = {}
    for requirement, text in docs.items():
        hits = sorted(t for t, pattern in patterns.items() if pattern.search(text))
        if hits:
            found[requirement] = hits
    return found


def registered_components():
    return components() + tool_images()


def test_R53_no_product_in_a_requirement(model):
    terms = product_terms(registered_components(), port_part_names(model))
    docs = requirement_docs(model)
    assert docs, "no requirement found in the model"
    assert terms, "no product name derived"
    named = products_named(docs, terms)
    assert not named, f"requirements that name a product: {named}"


def test_R53_no_product_in_a_requirement_detects_violation():
    registered = [
        {
            "name": "alpha-tool",
            "upstream": "https://example.test/vendor/alpha-tool",
            "submodule": "third_party/alpha",
        }
    ]
    terms = product_terms(registered, {"alphaToolAdapter"})
    docs = {"R1": "The engine shall start.", "R2": "Use Alpha-Tool to sign."}
    assert products_named(docs, terms) == {"R2": ["alpha", "alpha-tool"]}
    assert products_named({"R3": "Call the alphaToolAdapter."}, terms) == {
        "R3": ["alphaToolAdapter"]
    }
    assert products_named({"R4": "Ask the vendor."}, terms) == {"R4": ["vendor"]}
    assert products_named({"R5": "An alphabet of tools."}, terms) == {}
    assert products_named({"R6": "Build the alpha."}, terms) == {"R6": ["alpha"]}


# ---- R54: directories named by capability -------------------------------------


def directories_named_after(directories, terms):
    """The directories whose name is the name of a product."""
    patterns = [term_pattern(term) for term in terms]
    return sorted(
        str(d) for d in directories if any(p.fullmatch(d.name) for p in patterns)
    )


def capability_directories():
    """Every directory under engine/ and config/, at any depth."""
    found = []
    for top in ("engine", "config"):
        found += [
            p.relative_to(ROOT)
            for p in sorted((ROOT / top).rglob("*"))
            if p.is_dir() and "__pycache__" not in p.parts
        ]
    return found


def test_R54_directories_named_by_capability(model):
    terms = product_terms(registered_components(), port_part_names(model))
    directories = capability_directories()
    assert directories, "no directory under engine/ or config/"
    wrong = directories_named_after(directories, terms)
    assert not wrong, f"directories named after a product: {wrong}"


def test_R54_directories_named_by_capability_detects_violation():
    terms = product_terms([{"name": "alpha-tool"}], set())
    paths = [Path("engine/access"), Path("engine/access/alpha-tool")]
    assert directories_named_after(paths, terms) == ["engine/access/alpha-tool"]
    assert directories_named_after(paths[:1], terms) == []
    assert directories_named_after([Path("config/AlphaTool")], terms)


# ---- R55: the checks stay fast ------------------------------------------------


def limit_faults(limits, doc, name="maxCheckTime"):
    """The limit is held in the model, as an attribute of the requirement: it
    must be there, in seconds (GAP-035: the pilot does not check a unit), and the
    requirement's text must not state a number of its own."""
    if name not in limits:
        return [f"the requirement has no attribute {name}"]
    faults = []
    value, unit = limits[name]
    if unit != "s":
        faults.append(f"{name} is in {unit}, not in seconds")
    if not isinstance(value, int | float) or value <= 0:
        faults.append(f"{name} is not a positive number")
    if re.search(r"\d", doc):
        faults.append("the text of the requirement states a number of its own")
    return faults


def over_budget(elapsed, budget):
    return elapsed > budget


def test_R55_checks_stay_fast(model, seconds_in_session):
    """Measures the wall-clock time from the loading of this directory's
    conftest, at the start of collection, to the start of this test, which runs
    last. It covers collection, the export of the
    model (cold or warm) and every other test. It does not cover the other tasks
    of `mise run check` (model:check, lint, licences, secrets, workflows, ADRs,
    build), the start of `uv` and `mise`, the teardown, or a cold cache of the
    tools: the limit of the requirement is on the whole of the checks, this test
    bounds the part that is pytest."""
    limits = thresholds(model)["R55"]
    assert not limit_faults(limits, requirement_docs(model)["R55"])
    budget = limits["maxCheckTime"][0]
    elapsed = seconds_in_session()
    assert not over_budget(elapsed, budget), (
        f"the pytest session took {elapsed:.1f} s before this test; "
        f"the limit is {budget} s"
    )


def test_R55_checks_stay_fast_detects_violation():
    assert over_budget(61.0, 60)
    assert not over_budget(2.0, 60)
    assert limit_faults({"maxCheckTime": (60, "s")}, "within the bound") == []
    assert limit_faults({}, "within the bound")
    assert limit_faults({"maxCheckTime": (60, "B")}, "within the bound")
    assert limit_faults({"maxCheckTime": (0, "s")}, "within the bound")
    assert limit_faults({"maxCheckTime": (60, "s")}, "within 60 seconds")


# ---- Fitness-function markers (the pilot reports neither fault) ---------------

TRIGGERS = {"commit", "promotion", "runtime"}


def marker_faults(markers, requirements):
    """GAP-036: the pilot reports no marker without a trigger, so this does.
    A marker without a trigger, or with one that is not a Trigger value, and a
    marker on something that is not a requirement of the model."""
    faults = [
        f"{r}: the marker has no valid trigger ({t})"
        for r, t in sorted(markers.items())
        if t not in TRIGGERS
    ]
    faults += [
        f"{r}: marked but not a requirement"
        for r in sorted(markers.keys() - requirements)
    ]
    return faults


def threshold_faults(all_limits, docs, types=None):
    """A threshold has a unit unless it is a plain integer, and the text of its
    requirement states no number."""
    types = types or {}
    faults = []
    for requirement, limits in sorted(all_limits.items()):
        for name, (_value, unit) in sorted(limits.items()):
            plain = types.get(requirement, {}).get(name) == "Integer"
            if unit is None and not plain:
                faults.append(f"{requirement}.{name} has no unit")
        if re.search(r"\d", docs.get(requirement, "")):
            faults.append(f"{requirement}: the text states a number")
    return faults


def test_R68_limits_are_held_in_the_model(model):
    limits = thresholds(model)
    assert {"R9", "R55", "R81", "R85"} <= set(limits), "the limits are in the model"
    assert limits["R9"]["maxStartTime"] == (180, "s")
    assert not threshold_faults(limits, requirement_docs(model), threshold_types(model))


def test_R68_limits_are_held_in_the_model_detects_violation():
    ok = {"R1": {"max": (5, "s")}}
    assert threshold_faults(ok, {"R1": "within the bound"}) == []
    assert threshold_faults({"R1": {"max": (5, None)}}, {"R1": "x"})
    assert threshold_faults({"R1": {"max": (5, "s")}}, {"R1": "within 5 seconds"})
    count = {"R1": {"maxLines": (5, None)}}
    assert threshold_faults(count, {"R1": "x"}, {"R1": {"maxLines": "Integer"}}) == []
    assert threshold_faults(count, {"R1": "x"}, {"R1": {"maxLines": "Real"}})


def test_R69_fitness_markers_are_complete(model):
    markers = fitness_functions(model)
    assert markers, "no requirement is marked as a fitness function"
    assert not marker_faults(markers, set(requirement_docs(model)))


def test_R69_fitness_markers_are_complete_detects_violation():
    assert marker_faults({"R1": "commit"}, {"R1"}) == []
    assert marker_faults({"R1": None}, {"R1"})
    assert marker_faults({"R1": "sometimes"}, {"R1"})
    assert marker_faults({"R9": "commit"}, {"R1"})


# ---- R56: every check seen to fail ----------------------------------------------

# Verifications of a repository-level requirement that have no companion that
# shows them failing, each with the reason. Few, and in this one place.
EXCEPTIONS = {}


def checks_without_companion(names, exceptions):
    """Faults of the pairing of checks and companions: a check without its
    companion, a companion without its check, an exception that is not needed."""
    checks = {
        n for n in names if n.startswith("test_R") and not n.endswith(NEGATIVE_SUFFIX)
    }
    companions = {n for n in names if n.endswith(NEGATIVE_SUFFIX)}
    faults = [
        f"{n} has no {n + NEGATIVE_SUFFIX}"
        for n in sorted(checks)
        if n + NEGATIVE_SUFFIX not in companions and n not in exceptions
    ]
    faults += [
        f"{c} has no check named {c.removesuffix(NEGATIVE_SUFFIX)}"
        for c in sorted(companions)
        if c.startswith("test_R") and c.removesuffix(NEGATIVE_SUFFIX) not in checks
    ]
    faults += [
        f"exception {n} is not a check, or has a companion, or has no reason"
        for n, reason in sorted(exceptions.items())
        if n not in checks or n + NEGATIVE_SUFFIX in companions or not reason
    ]
    return faults


def test_R56_every_check_seen_to_fail():
    names = defined_function_names(ROOT / "tests" / "repository")
    faults = checks_without_companion(names, EXCEPTIONS)
    assert not faults, faults


def test_R56_every_check_seen_to_fail_detects_violation():
    check = "test_R9_x"
    companion = check + NEGATIVE_SUFFIX
    assert checks_without_companion({check, companion}, {}) == []
    assert checks_without_companion({check}, {})
    assert checks_without_companion({companion}, {})
    assert checks_without_companion({check}, {check: "why"}) == []
    assert checks_without_companion({check}, {check: ""})
    assert checks_without_companion({check, companion}, {check: "why"})
    assert checks_without_companion({check}, {"test_R8_y": "why"})
    assert checks_without_companion({"test_helper_x"}, {}) == []
