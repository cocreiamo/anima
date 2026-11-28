"""The copy of an image into the mirror, run for real. R176, R165. Run through
`mise run ci:test`.

Upstream and mirror are two repositories of one throwaway registry started from its
pinned image; the copy tool is the pinned image of the register, run by podman as
the workflow runs it. The registry has no credentials to check: that GitHub's
registry accepts the token and the package is shown only by a run of the workflow.
"""

import re
import time
from types import SimpleNamespace

import pytest
from ci_support import ROOT, reference, run, task


@pytest.fixture
def scenario(store, tmp_path):
    """Two images in an upstream repository: the pinned one (`old`, by digest) and
    the one that the tag names now (`new`). Returns what the command is given."""
    suffix = f"{time.time_ns()}"
    upstream, mirror = f"up/app{suffix}", f"mirror/app{suffix}"
    old = store.push(upstream, "old", f"old {suffix}")
    new = store.push(upstream, "1", f"new {suffix}")
    assert old != new
    environment = {
        "SKOPEO": reference("skopeo"),
        "NAME": "app",
        "IM" + "AGE": f"{store.host}/{upstream}",
        "TAG": "1",
        "DIGEST": f"sha256:{old}",
        "MIRROR": f"{store.host}/{mirror}",
        "REGISTRY_TOKEN": "token",
        "ACTOR": "actor",
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_STEP_SUMMARY": str(tmp_path / "summary"),
        "ANIMA_MIRROR_INSECURE": "1",
        "ANIMA_MIRROR_NETWORK": "host",
    }
    return SimpleNamespace(
        store=store,
        upstream=upstream,
        mirror=mirror,
        old=old,
        new=new,
        environment=environment,
    )


def today():
    return time.strftime("%Y%m%d", time.gmtime())


def test_R176_mirror_copy_keeps_digests_and_never_moves_a_tag(scenario, tmp_path):
    """Proves, against a real registry, that the digest that the upstream tag names
    now and the pinned digest are both in the mirror under the digest they have
    upstream, reachable by the digest tag and by the day's tag, that a second run
    changes nothing, and that the summary names both digests."""
    store, upstream, mirror = scenario.store, scenario.upstream, scenario.mirror
    old, new, environment = scenario.old, scenario.new, scenario.environment
    result = task("mirror-copy", env=environment)
    assert result.returncode == 0, result.stderr + result.stdout

    day = f"1-{today()}"
    assert store.digest(mirror, f"sha256-{new}") == new
    assert store.digest(mirror, day) == new
    assert store.digest(mirror, f"sha256-{old}") == old
    # The upstream tag itself is there too: the update bot reads the digest of a
    # tag, so it finds in the mirror only a digest that the mirror holds.
    assert store.digest(mirror, "1") == new
    tags = sorted([f"sha256-{new}", day, f"sha256-{old}", "1"])
    assert store.tags(mirror) == tags
    summary = (tmp_path / "summary").read_text()
    assert f"sha256:{new}" in summary and f"sha256:{old}" in summary

    again = task("mirror-copy", env=environment)
    assert again.returncode == 0, again.stderr
    assert "already holds" in again.stdout
    assert store.tags(mirror) == tags

    # The upstream tag moves on: the day's tag of the mirror stays where it is, the
    # new digest gets its own tag, and the tag that is the upstream's follows it,
    # while the digest it named stays reachable by its own tag.
    newer = store.push(upstream, "1", "newer")
    moved = task("mirror-copy", env=environment)
    assert moved.returncode == 0, moved.stderr
    assert store.digest(mirror, day) == new, "a tag of the mirror was moved"
    assert store.digest(mirror, f"sha256-{newer}") == newer
    assert store.digest(mirror, "1") == newer, "the followed tag did not follow"
    assert store.digest(mirror, f"sha256-{new}") == new
    assert "left as it is" in moved.stdout


def test_R176_mirror_copy_keeps_digests_and_never_moves_a_tag_detects_violation(
    scenario,
):
    """What must stop the copy does: a tag that upstream no longer has, a pinned
    digest it no longer holds, a digest tag of the mirror that names another image,
    and a registry that does not answer, which is not read as "absent"."""
    store, mirror = scenario.store, scenario.mirror
    new, environment = scenario.new, scenario.environment

    gone = task("mirror-copy", env={**environment, "TAG": "removed"})
    assert gone.returncode != 0
    assert "does not exist upstream" in gone.stderr
    assert store.tags(mirror) == []

    missing = task("mirror-copy", env={**environment, "DIGEST": "sha256:" + "1" * 64})
    assert missing.returncode != 0
    assert f"sha256-{'1' * 64}" not in store.tags(mirror)
    # The tag that follows the upstream was moved before the pinned digest failed.
    assert store.digest(mirror, "1") == new

    # A digest tag that holds another image is a fault, and is left alone.
    other = store.push(mirror, f"sha256-{new}", "another image")
    assert other != new
    fault = task("mirror-copy", env=environment)
    assert fault.returncode != 0
    assert "not the digest it is named for" in fault.stderr
    assert store.digest(mirror, f"sha256-{new}") == other

    # Nothing answers at the address: "cannot read", not "does not exist".
    unreachable = task(
        "mirror-copy", env={**environment, "IMAGE": "127.0.0.1:1/up/app"}
    )
    assert unreachable.returncode != 0
    assert "cannot read" in unreachable.stderr

    # Every input is required.
    for name in ("SKOPEO", "MIRROR", "DIGEST"):
        assert task("mirror-copy", env={**environment, name: ""}).returncode != 0


def test_R165_signed_image_is_copied_with_its_signatures(scenario, tmp_path):
    """Proves that an image that its upstream signed (a signature stored next to it
    as an attachment) is copied with its signature, under the same digest."""
    store, upstream, mirror = scenario.store, scenario.upstream, scenario.mirror
    new, environment = scenario.new, scenario.environment
    key = tmp_path / "key"
    passphrase = tmp_path / "passphrase"
    passphrase.write_text("x\n")
    registries = tmp_path / "signing.d"
    registries.mkdir()
    (registries / "up.yaml").write_text(
        f"docker:\n  {store.host}:\n    use-sigstore-attachments: true\n"
    )
    skopeo = reference("skopeo")
    mounts = [
        "--volume", f"{tmp_path}:/work",
        "--volume", f"{registries}:/rd:ro",
    ]  # fmt: skip
    run(
        ["podman", "run", "--rm", "--network", "host", *mounts, skopeo,
         "generate-sigstore-key", "--output-prefix", "/work/key",
         "--passphrase-file", "/work/passphrase"],
        check=True,
    )  # fmt: skip
    assert key.with_suffix(".private").exists()
    # The upstream image is signed: copied onto itself under a new tag with a
    # signature, which writes the attachment next to its digest.
    run(
        ["podman", "run", "--rm", "--network", "host", *mounts, skopeo,
         "--registries.d", "/rd", "copy", "--all", "--preserve-digests",
         "--src-tls-verify=false", "--dest-tls-verify=false",
         "--sign-by-sigstore-private-key", "/work/key.private",
         "--sign-passphrase-file", "/work/passphrase",
         f"docker://{store.host}/{upstream}:1", f"docker://{store.host}/{upstream}:signed"],
        check=True,
    )  # fmt: skip
    signed_tags = [t for t in store.tags(upstream) if t.endswith(".sig")]
    assert signed_tags, "the upstream image has no signature attachment"

    result = task("mirror-copy", env={**environment, "TAG": "signed"})
    assert result.returncode == 0, result.stderr + result.stdout
    assert store.digest(mirror, f"sha256-{new}") == new
    assert f"sha256-{new}.sig" in store.tags(mirror)
    assert re.search(r"signed-\d{8}", " ".join(store.tags(mirror)))


def test_R165_signed_image_is_copied_with_its_signatures_detects_violation(
    scenario,
):
    """An image that nobody signed is copied, and no signature appears for it in the
    mirror: the signatures that the signed test finds were the upstream's."""
    store, mirror = scenario.store, scenario.mirror
    environment = scenario.environment
    result = task("mirror-copy", env=environment)
    assert result.returncode == 0, result.stderr
    assert [t for t in store.tags(mirror) if t.endswith(".sig")] == []


# ---- the mirror holds every pin of the register --------------------------------------------


def register_of(path, host, entries):
    """A register whose images are packages of the throwaway registry at `host`;
    `entries` is [(name, repository, digest)]."""
    path.write_text(
        "".join(
            f'[[tool_image]]\nname = "{name}"\nversion = "1"\n'
            f'image = "{host}/{repository}"\ndigest = "sha256:{digest}"\n'
            for name, repository, digest in entries
        )
    )
    return path


CHECK_ENV = {"ANIMA_MIRROR_INSECURE": "1"}


def test_mirror_holds_every_pin(store, tmp_path):
    """Proves, against a registry, that the check passes when the mirror holds the
    digest that the register pins for each image, and that the check is run after
    the copies of the mirror workflow, before the builds of the system tests and by
    the promotion's verification."""
    suffix = f"{time.time_ns()}"
    held = f"mirror/held{suffix}"
    digest = store.push(held, "1", f"held {suffix}")
    register = register_of(tmp_path / "ok.toml", store.host, [("held", held, digest)])
    result = task("mirror-check", str(register), env=CHECK_ENV)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "held: the mirror holds" in result.stdout

    workflows = ROOT / ".github" / "workflows"
    mirror = (workflows / "mirror-base-images.yml").read_text()
    system = (workflows / "system-tests.yml").read_text()
    mise = (ROOT / "mise.toml").read_text()
    assert "needs: mirror" in mirror and "run: mise run ci:mirror-check" in mirror
    assert system.index("mise run ci:mirror-check") < system.index(
        "mise run engine:image"
    ), "the check runs after a build"
    verify = mise.split('[tasks."promote:verify"]', 1)[1].split("\n[", 1)[0]
    assert verify.index("ci:mirror-check") < verify.index("engine:test")


def test_mirror_holds_every_pin_detects_violation(store, tmp_path):
    """A digest that the mirror does not hold, a package that does not exist, a
    registry that does not answer and an empty register each fail, and the failure
    names the image."""
    suffix = f"{time.time_ns()}"
    held = f"mirror/held{suffix}"
    digest = store.push(held, "1", f"held {suffix}")
    missing = register_of(
        tmp_path / "missing.toml",
        store.host,
        [("held", held, digest), ("lost", held, "1" * 64)],
    )
    result = task("mirror-check", str(missing), env=CHECK_ENV)
    assert result.returncode != 0
    assert "lost" in result.stderr and "held: the mirror holds" in result.stdout

    absent = register_of(
        tmp_path / "absent.toml",
        store.host,
        [("nowhere", f"mirror/none{suffix}", "2" * 64)],
    )
    result = task("mirror-check", str(absent), env=CHECK_ENV)
    assert result.returncode != 0 and "nowhere" in result.stderr

    dead = register_of(
        tmp_path / "dead.toml", "127.0.0.1:1", [("dead", "mirror/x", "3" * 64)]
    )
    assert task("mirror-check", str(dead), env=CHECK_ENV).returncode != 0

    empty = tmp_path / "empty.toml"
    empty.write_text("")
    assert task("mirror-check", str(empty), env=CHECK_ENV).returncode != 0
