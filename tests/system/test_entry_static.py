"""Checks of the HTTP entry point's declarations that start nothing: the routes it
declares and what its build pins (GAP-057). They run in every `pytest` run."""

import json
import tomllib

from conftest import ROOT
from engine_logic import entry_pin_faults


def test_entry_declares_only_three_prefixes_and_one_loopback_backend():
    """The declaration of the engine names exactly the three prefixes and one
    backend on the loopback: a route added to it is a change of this list."""
    settings = json.loads((ROOT / "engine/entry/appsettings.json").read_text())
    routes = settings["ReverseProxy"]["Routes"].values()
    prefixes = sorted(r["Match"]["Path"].split("/{", 1)[0] for r in routes)
    assert prefixes == ["/.well-known", "/realms", "/resources"], prefixes
    addresses = {
        d["Address"]
        for c in settings["ReverseProxy"]["Clusters"].values()
        for d in c["Destinations"].values()
    }
    assert addresses == {"http://127.0.0.1:8080/"}, addresses


def test_entry_build_pins_match_components():
    """The entry's container file pins what the register says it pins: the base
    image by digest, the library by version and by the hash of its package file,
    the distribution's packages by version, and it checks the hash and restores
    from the lock file; the skill of the entry and the gaps of the build exist."""
    components = tomllib.loads((ROOT / "components.toml").read_text())["component"]
    containerfile = (ROOT / "engine/entry/Containerfile").read_text()
    faults = entry_pin_faults(containerfile, components)
    assert not faults, faults
    lock = json.loads((ROOT / "engine/entry/packages.lock.json").read_text())
    resolved = lock["dependencies"]["net10.0"]["Yarp.ReverseProxy"]
    assert resolved["resolved"] == "2.3.0" and resolved["contentHash"]
    skill = (ROOT / "skills/anima-entry-design.md").read_text()
    assert "GAP-057" in skill and "/realms/master/" in skill
    gaps = tomllib.loads((ROOT / "gaps.toml").read_text())["gap"]
    assert {"GAP-057", "GAP-058"} <= {g["id"] for g in gaps}
