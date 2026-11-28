"""Reading the model (model/anima.sysml and model/requirements/**) through the
JSON export of the SysML v2 Pilot Implementation, never by parsing the text
ourselves. The one exception is the layout of the files (test_model_layout.py):
which file holds which requirement is not in the export.
"""

import ast
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def export_model(source="model"):
    """Elements of a SysML file or of a directory of them (default: the model,
    read as one), by id."""
    path = subprocess.run(
        [str(ROOT / "mise-tasks" / "model" / "export"), str(source)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    # The path is in the export cache, keyed by the hash of the model: never
    # remove it.
    exported = json.loads(Path(path).read_text())
    elements = (e.get("payload", e) for e in exported)
    return {e["@id"]: e for e in elements}


def relationships(model, element, kind):
    for ref in element.get("ownedRelationship", []):
        relationship = model.get(ref["@id"])
        if relationship is not None and relationship["@type"] == kind:
            yield relationship


def children(model, element, kind=None):
    for ref in element.get("ownedRelationship", []):
        relationship = model.get(ref["@id"])
        if relationship is None or (kind and relationship["@type"] != kind):
            continue
        for child in relationship.get("ownedRelatedElement", []):
            if child["@id"] in model:
                yield model[child["@id"]]


def referenced(model, element):
    """The feature a `verify x` or `verify x.y` refers to, if any."""
    for subsetting in relationships(model, element, "ReferenceSubsetting"):
        target = model.get(subsetting["referencedFeature"]["@id"])
        if target is None:
            return None
        chain = list(relationships(model, target, "FeatureChaining"))
        if chain:  # `x.y`: the last feature of the chain
            return model.get(chain[-1]["chainingFeature"]["@id"])
        return target
    return None


def is_requirement(model, element):
    """A requirement is identified by its name. A short name, `R<n>`, is the
    alias of one that had a number before the name became the identifier."""
    return (
        element["@type"] == "RequirementUsage"
        and element.get("declaredName")
        and referenced(model, element) is None
    )


def alias(element):
    """The legacy number of a requirement, `R55`, or None for one without."""
    return element.get("declaredShortName")


def verifications(model):
    """The verification definitions of the model, by name, with what they verify."""
    found = {}
    for element in model.values():
        if element["@type"] != "VerificationCaseDefinition":
            continue
        targets = set()
        for objective in children(model, element, "ObjectiveMembership"):
            for verify in children(
                model, objective, "RequirementVerificationMembership"
            ):
                target = referenced(model, verify)
                if target is not None:
                    targets.add(target["@id"])
        found[element["declaredName"]] = targets
    return found


# A check that verifies a requirement is named after it: `test_<snake_case name>`,
# or `test_R<n>_<what>` for a requirement that has a legacy number. Its
# companion, which shows that the check fails on a deliberately wrong input, has
# the same name with this suffix (R56). A companion verifies nothing in the
# model, so names_of_tests() leaves it out.
NEGATIVE_SUFFIX = "_detects_violation"


def defined_function_names(directory):
    """Names of every function defined in the test_*.py files of a directory."""
    names = set()
    for path in directory.rglob("test_*.py"):
        tree = ast.parse(path.read_text())
        names |= {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    return names


def names_of_tests(model):
    """Names of the written tests that implement a verification of the model:
    those named `test_R<n>_...` and those that carry the name of a verification,
    without their companions that show the check failing."""
    verified = set(verifications(model))
    return {
        name
        for name in defined_function_names(ROOT / "tests")
        if (name.startswith("test_R") or name in verified)
        and not name.endswith(NEGATIVE_SUFFIX)
    }


# ---- Requirement texts ------------------------------------------------------


def requirement_docs(model):
    """The `doc` text of every requirement, by name."""
    docs = {}
    for element in model.values():
        if is_requirement(model, element):
            docs[element["declaredName"]] = " ".join(
                child["body"].strip()
                for child in children(model, element)
                if child["@type"] == "Documentation"
            )
    return docs


# ---- Structure of the model: ports and the parts that fill them --------------


def named(model, name):
    found = [
        e
        for e in model.values()
        if e["@type"] == "PartDefinition" and e.get("declaredName") == name
    ]
    assert len(found) == 1, f"the model defines {name} once"
    return found[0]["@id"]


def specializations(model, general_id):
    """Ids of the definitions that directly specialize the given definition."""
    return {
        r["specific"]["@id"]
        for r in model.values()
        if r["@type"] == "Subclassification"
        and r["general"]["@id"] == general_id
        and r["specific"]["@id"] in model
    }


def usages_of(model, definition_id):
    """Names of the part usages typed by the given definition, wherever nested."""
    return [
        usage.get("declaredName")
        for usage in model.values()
        if usage["@type"] == "PartUsage"
        for typing in relationships(model, usage, "FeatureTyping")
        if typing["type"]["@id"] == definition_id
    ]


def port_part_names(model):
    """Names of the parts that fill a port: the adapters and the stand-ins."""
    names = set()
    for port in specializations(model, named(model, "Port")):
        for definition in {port} | specializations(model, port):
            names.update(usages_of(model, definition))
    return names


# ---- Thresholds: numbers held in the model --------------------------------------
# Promoted from a spike with the Pilot Implementation: a threshold is an attribute
# of a requirement bound to a literal with a unit, e.g.
# `attribute maxStartTime : ISQ::DurationValue = 180 [SI::s];`.

LITERALS = {"LiteralInteger", "LiteralRational"}


def _bound_value(model, feature):
    """The expression bound to a feature by `= ...`, if any."""
    return next(children(model, feature, "FeatureValue"), None)


def _quantity(model, expression):
    """(value, unit) of a literal `180` or `180 [s]`; None for anything else.

    `180 [s]` is an OperatorExpression with operator "[" whose two parameters
    are bound to the literal and to a reference whose Membership points at the
    unit, exported as a library stub with declaredShortName "s".
    """
    if expression is None:
        return None
    if expression["@type"] in LITERALS:
        return (expression["value"], None)
    if (
        expression["@type"] == "OperatorExpression"
        and expression.get("operator") == "["
    ):
        number, unit = (
            _bound_value(model, p)
            for p in children(model, expression, "ParameterMembership")
        )
        if number is None or number["@type"] not in LITERALS or unit is None:
            return None
        membership = next(relationships(model, unit, "Membership"), None)
        target = model.get(membership["memberElement"]["@id"]) if membership else None
        if target is None:
            return None
        return (
            number["value"],
            target.get("declaredShortName") or target.get("declaredName"),
        )
    return None


def thresholds(model):
    """{requirement name: {threshold name: (value, unit)}}: the attributes
    of a requirement that are bound to a literal, with or without a unit. The
    pilot does not check that the unit fits the attribute's quantity, so a test
    that reads a threshold also asserts its unit."""
    found = {}
    for requirement in model.values():
        if requirement["@type"] != "RequirementUsage" or not requirement.get(
            "declaredName"
        ):
            continue
        values = {}
        for attribute in children(model, requirement, "FeatureMembership"):
            if attribute["@type"] == "AttributeUsage":
                quantity = _quantity(model, _bound_value(model, attribute))
                if quantity is not None:
                    values[attribute.get("declaredName")] = quantity
        if values:
            found[requirement["declaredName"]] = values
    return found


def threshold_types(model):
    """{requirement name: {attribute name: declared type name}} for the
    attributes of a requirement that are bound to a literal: `Integer` for a
    plain count, a quantity type for a duration."""
    found = {}
    for requirement in model.values():
        if requirement["@type"] != "RequirementUsage" or not requirement.get(
            "declaredName"
        ):
            continue
        for attribute in children(model, requirement, "FeatureMembership"):
            if attribute["@type"] != "AttributeUsage":
                continue
            if _quantity(model, _bound_value(model, attribute)) is None:
                continue
            found.setdefault(requirement["declaredName"], {})[
                attribute.get("declaredName")
            ] = _type_name(model, attribute)
    return found


# ---- Fitness functions: requirements marked in the model ---------------------------


def _type_name(model, element):
    typing = next(relationships(model, element, "FeatureTyping"), None)
    target = model.get(typing["type"]["@id"]) if typing else None
    return target.get("declaredName") if target else None


def fitness_functions(model, metadata="FitnessFunction"):
    """{requirement name: trigger} for every requirement marked with
    `@FitnessFunction { trigger = Trigger::commit; }`. The trigger is the name of
    the enumeration value, or None when the marker sets none: the pilot does not
    report a missing trigger, so a test does."""
    found = {}
    for usage in model.values():
        if usage["@type"] != "MetadataUsage" or _type_name(model, usage) != metadata:
            continue
        annotations = list(relationships(model, usage, "Annotation"))
        if annotations:  # `metadata ... about x`
            targets = [model.get(a["annotatedElement"]["@id"]) for a in annotations]
        else:  # `@...` owned by the requirement it marks
            targets = [model.get(usage["owner"]["@id"])]
        trigger = None
        for feature in children(model, usage, "FeatureMembership"):
            redefinition = next(relationships(model, feature, "Redefinition"), None)
            redefined = (
                model.get(redefinition["redefinedFeature"]["@id"])
                if redefinition
                else None
            )
            if redefined is None or redefined.get("declaredName") != "trigger":
                continue
            reference = _bound_value(model, feature)
            membership = (
                next(relationships(model, reference, "Membership"), None)
                if reference
                else None
            )
            value = (
                model.get(membership["memberElement"]["@id"]) if membership else None
            )
            trigger = value.get("declaredName") if value else None
        for target in targets:
            if (
                target
                and target["@type"] == "RequirementUsage"
                and target.get("declaredName")
            ):
                found[target["declaredName"]] = trigger
    return found
