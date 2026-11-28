"""The Renovate manager that updates the images of components.toml must find
every image entry (a pattern that matches nothing updates nothing, silently).
"""

import json
import re

from repo_facts import components, tool_images
from sysml_model import ROOT


def manager_pattern():
    """The first match string of the custom manager of .github/renovate.json,
    as a Python pattern (Renovate writes named groups `(?<name>...)`)."""
    config = json.loads((ROOT / ".github" / "renovate.json").read_text())
    pattern = config["customManagers"][0]["matchStrings"][0]
    return re.compile(re.sub(r"\(\?<([A-Za-z])", r"(?P<\1", pattern))


def unmatched_images(pattern, text, expected):
    """Images that are in `expected` and that the pattern does not find, and
    those found with something else than their digest."""
    found = {m["depName"] for m in pattern.finditer(text)}
    return sorted(set(expected) - found)


def registered_image_names():
    return [c["image"] for c in components() + tool_images() if "image" in c]


def test_R70_update_bot_finds_every_image():
    expected = registered_image_names()
    assert expected, "no image in components.toml"
    text = (ROOT / "components.toml").read_text()
    assert not unmatched_images(manager_pattern(), text, expected)


def entry(image_line):
    return (
        '[[component]]\nname = "x"\nversion = "1.0.0"\nlicense = "MIT"\n'
        f"{image_line}\ndigest = " + '"sha256:' + "0" * 64 + '"\n'
    )


def test_R70_update_bot_finds_every_image_detects_violation():
    pattern = manager_pattern()
    name = "registry" + ".example/a/b"  # put together: no reference in this file
    spaced = "im" + f'age = "{name}"'
    unspaced = "im" + f'age ="{name}"'
    assert unmatched_images(pattern, entry(spaced), [name]) == []
    assert unmatched_images(pattern, entry(unspaced), [name])
    assert unmatched_images(pattern, "", [name])
