"""Traceability between the requirements model and the tests.

The model is read through the JSON export of the SysML v2 Pilot Implementation,
never by parsing the text ourselves.
"""

import tomllib

import generators
from sysml_model import (
    ROOT,
    children,
    is_requirement,
    names_of_tests,
    verifications,
)


def traceability_faults(model, tests, pending, pending_text):
    """Faults between the model's verifications, the written tests (without
    their companions), the pending list and the generated pending file."""
    faults = []
    found = verifications(model)
    verified = set().union(*found.values()) if found else set()
    names = set(found)

    def is_verified(requirement):
        if requirement["@id"] in verified:
            return True
        nested = [c for c in children(model, requirement) if is_requirement(model, c)]
        return bool(nested) and all(is_verified(c) for c in nested)

    requirements = [e for e in model.values() if is_requirement(model, e)]
    if not requirements:
        faults.append("no requirement found in the model")
    unverified = sorted(
        r["declaredShortName"] for r in requirements if not is_verified(r)
    )
    if unverified:
        faults.append(f"requirements without a verification: {unverified}")

    # Every verification is a test of the same name, or is listed as pending.
    if names - tests - pending:
        faults.append(f"verifications with no test: {sorted(names - tests - pending)}")
    if tests - names:
        faults.append(
            f"tests that verify nothing in the model: {sorted(tests - names)}"
        )
    if pending & tests:
        faults.append(
            f"written tests still listed as pending: {sorted(pending & tests)}"
        )
    if pending - names:
        faults.append(f"pending entries not in the model: {sorted(pending - names)}")

    # The list is generated, so it is also exactly the computed one.
    if pending_text != generators.render_pending(names, tests):
        faults.append("tests/pending.toml is out of date: run `mise run generate`")
    return faults


def pending_file():
    text = (ROOT / "tests" / "pending.toml").read_text()
    return set(tomllib.loads(text)["pending"]), text


def test_R10_every_requirement_verified(model):
    pending, text = pending_file()
    faults = traceability_faults(model, names_of_tests(model), pending, text)
    assert not faults, faults


def test_R10_every_requirement_verified_detects_violation(model):
    tests = names_of_tests(model)
    pending, text = pending_file()
    assert traceability_faults(model, tests, pending, text) == []

    # A requirement whose verification is removed from the model.
    gone = {
        key: e
        for key, e in model.items()
        if e.get("declaredName") != "test_R2_valid_token_opens_session"
    }
    assert any(
        "without a verification" in f
        for f in traceability_faults(
            gone, tests, pending - {"test_R2_valid_token_opens_session"}, text
        )
    )

    # A verification with no test and not pending.
    written = "test_R10_every_requirement_verified"
    assert any(
        "no test" in f
        for f in traceability_faults(model, tests - {written}, pending, text)
    )
    # A test that verifies nothing in the model.
    assert any(
        "verify nothing" in f
        for f in traceability_faults(
            model, tests | {"test_R999_nothing"}, pending, text
        )
    )
    # A written test still listed as pending.
    assert any(
        "still listed as pending" in f
        for f in traceability_faults(model, tests, pending | {written}, text)
    )
    # A pending entry that is not in the model.
    assert any(
        "not in the model" in f
        for f in traceability_faults(model, tests, pending | {"test_R999_x"}, text)
    )
    # A stale generated file.
    assert any(
        "out of date" in f
        for f in traceability_faults(model, tests, pending, text + "# stale\n")
    )
    # A test that shows a check failing is not a verification in the model.
    assert "test_R10_every_requirement_verified" in tests
    assert "test_R10_every_requirement_verified_detects_violation" not in tests
