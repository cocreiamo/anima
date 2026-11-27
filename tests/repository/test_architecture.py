"""Verifications of the architecture of the model (ADR 0001)."""

from sysml_model import children, named, relationships, specializations, usages_of


def ports_without_one_default_adapter(model):
    """Ports whose default adapter is not exactly one part. The default adapter
    is the part typed by the port itself; an alternative adapter, a stand-in
    included, is typed by a definition that specializes the port and a marker,
    so any number of them is allowed. A part typed by several ports is the
    default adapter of each."""
    ports = specializations(model, named(model, "Port"))
    assert ports, "no port specializes Port"
    wrong = {}
    for port in ports:
        defaults = usages_of(model, port)
        if len(defaults) != 1:
            wrong[model[port]["declaredName"]] = defaults
    return wrong


def test_R28_each_port_has_one_default_adapter(model):
    wrong = ports_without_one_default_adapter(model)
    assert not wrong, f"ports without exactly one default adapter: {wrong}"


def synthetic_model(ports, shared=()):
    """A model in the shape of the Pilot Implementation's export, with the
    given ports: {port name: (default adapters, alternative adapters)}. `shared`
    lists ports that also get one part typed by all of them: an adapter that
    fills several ports."""
    model = {}

    def add(kind, **fields):
        element_id = f"e{len(model)}"
        model[element_id] = {"@id": element_id, "@type": kind, **fields}
        return element_id

    def specialize(general, specific):
        add(
            "Subclassification",
            general={"@id": general},
            specific={"@id": specific},
        )

    def usage(name, definition):
        typing = add("FeatureTyping", type={"@id": definition})
        add("PartUsage", declaredName=name, ownedRelationship=[{"@id": typing}])

    port = add("PartDefinition", declaredName="Port")
    stand_in = add("PartDefinition", declaredName="StandIn")
    definitions = {}
    for name, (production, stand_ins) in ports.items():
        definition = add("PartDefinition", declaredName=name)
        definitions[name] = definition
        specialize(port, definition)
        local = add("PartDefinition", declaredName=f"Local{name}")
        specialize(definition, local)
        specialize(stand_in, local)
        for number in range(production):
            usage(f"{name}Adapter{number}", definition)
        for number in range(stand_ins):
            usage(f"{name}Alternative{number}", local)
    if shared:
        typings = [add("FeatureTyping", type={"@id": definitions[n]}) for n in shared]
        add(
            "PartUsage",
            declaredName="shared",
            ownedRelationship=[{"@id": t} for t in typings],
        )
    return model


def test_R28_each_port_has_one_default_adapter_detects_violation():
    def wrong(ports, shared=()):
        return set(ports_without_one_default_adapter(synthetic_model(ports, shared)))

    assert wrong({"A": (1, 0), "B": (1, 1), "C": (1, 3)}) == set()
    assert wrong({"A": (0, 0)}) == {"A"}
    assert wrong({"A": (2, 0)}) == {"A"}
    assert wrong({"A": (0, 2)}) == {"A"}  # alternatives are not a default
    # One part that fills two ports is the default adapter of each.
    assert wrong({"A": (0, 0), "B": (0, 0)}, shared=("A", "B")) == set()
    assert wrong({"A": (1, 0), "B": (0, 0)}, shared=("A", "B")) == {"A"}


def part_usages_below(model, usage):
    """Every part usage nested, at any depth, in the given part usage."""
    for child in children(model, usage):
        if child["@type"] == "PartUsage":
            yield child
            yield from part_usages_below(model, child)


def adapters_outside_engine(model):
    """Names of the parts that fill a port and are not nested in the engine."""
    engine_definition = named(model, "Engine")
    engines = [
        usage
        for usage in model.values()
        if usage["@type"] == "PartUsage"
        and usage.get("declaredName") in usages_of(model, engine_definition)
    ]
    assert len(engines) == 1, "the model has exactly one engine"
    inside = {u["@id"] for u in part_usages_below(model, engines[0])}
    wrong = []
    for port in specializations(model, named(model, "Port")):
        definitions = {port} | specializations(model, port)
        for usage in model.values():
            if usage["@type"] != "PartUsage":
                continue
            typed = {
                t["type"]["@id"] for t in relationships(model, usage, "FeatureTyping")
            }
            if typed & definitions and usage["@id"] not in inside:
                wrong.append(usage.get("declaredName"))
    return wrong


def test_R67_every_adapter_is_part_of_the_engine(model):
    wrong = adapters_outside_engine(model)
    assert not wrong, f"adapters outside the engine: {wrong}"


def engine_model(inside, outside):
    """A model with one port, one engine and the given adapters nested in the
    engine or beside it."""
    model = {}

    def add(element_id, kind, **fields):
        model[element_id] = {"@id": element_id, "@type": kind, **fields}

    def typed(element_id, name, definition, owned=()):
        add(f"{element_id}-t", "FeatureTyping", type={"@id": definition})
        members = []
        for child in owned:
            add(f"{element_id}-m-{child}", "FeatureMembership")
            model[f"{element_id}-m-{child}"]["ownedRelatedElement"] = [{"@id": child}]
            members.append({"@id": f"{element_id}-m-{child}"})
        add(
            element_id,
            "PartUsage",
            declaredName=name,
            ownedRelationship=[{"@id": f"{element_id}-t"}, *members],
        )

    add("port", "PartDefinition", declaredName="Port")
    add("a", "PartDefinition", declaredName="A")
    add("sub", "Subclassification", general={"@id": "port"}, specific={"@id": "a"})
    add("engine-def", "PartDefinition", declaredName="Engine")
    for name in inside + outside:
        typed(name, name, "a")
    typed("engine", "engine", "engine-def", owned=inside)
    return model


def test_R67_every_adapter_is_part_of_the_engine_detects_violation():
    assert adapters_outside_engine(engine_model(["x"], [])) == []
    assert adapters_outside_engine(engine_model(["x"], ["y"])) == ["y"]
    assert adapters_outside_engine(engine_model([], ["y"])) == ["y"]
