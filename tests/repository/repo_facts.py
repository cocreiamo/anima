"""Facts about the repository that several verifications read: the registers and
the files outside the forks. The checks themselves are functions of their
inputs and live with their tests."""

import subprocess
import tomllib

from sysml_model import ROOT


def load_toml(name):
    return tomllib.loads((ROOT / name).read_text())


def components():
    """The shipped components of components.toml."""
    return load_toml("components.toml")["component"]


def tool_images():
    """The images used only by tools and tests (not shipped), if any."""
    return load_toml("components.toml").get("tool_image", [])


def submodule_commits():
    """Commit pinned by each submodule, read from the git index."""
    out = subprocess.run(
        ["git", "ls-files", "--stage"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    pins = {}
    for line in out.splitlines():
        mode, commit, _stage, path = line.split(maxsplit=3)
        if mode == "160000":
            pins[path] = commit
    return pins


def repository_files():
    """Files of the repository outside the submodules, tracked or not ignored."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    submodules = set(submodule_commits())
    for name in filter(None, out.split("\0")):
        path = ROOT / name
        if name not in submodules and path.is_file() and not path.is_symlink():
            yield name, path


def outside_snapshot(root=ROOT, levels=3):
    """Names of the files directly in the `levels` directories above the
    repository: where the model exporter once wrote a file by mistake (PM-003)."""
    names = set()
    for directory in list(root.parents)[:levels]:
        try:
            names |= {
                str(p) for p in directory.iterdir() if p.is_file() or p.is_symlink()
            }
        except OSError:
            continue
    return names
