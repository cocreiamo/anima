"""The cache of the inner images, run with podman: save them as one archive, load
them back. R171. Run through `mise run ci:test`.

Tiny images built from nothing stand for the inner images; their references are
written the way `engine:build` writes them (`<name>.ref`).
"""

import os
from pathlib import Path

import pytest
from ci_support import run, task

NAMES = "alpha beta"


@pytest.fixture
def images(tmp_path):
    """Two built images and the directory of their `.ref` files; removed after."""
    refs = tmp_path / "refs"
    refs.mkdir()
    built = []
    for name in NAMES.split():
        reference = f"localhost/anima-ci-test/{name}:{os.urandom(4).hex()}"
        context = tmp_path / f"context-{name}"
        context.mkdir()
        (context / "Containerfile").write_text("FROM scratch\nCOPY f /f\n")
        (context / "f").write_text(name)
        run(["podman", "build", "--tag", reference, str(context)], check=True)
        (refs / f"{name}.ref").write_text(reference + "\n")
        built.append(reference)
    try:
        yield refs, built
    finally:
        run(["podman", "rmi", "--force", *built])


def exists(reference):
    return run(["podman", "image", "exists", reference]).returncode == 0


def environment(refs):
    return {"ANIMA_ENGINE_REFS": str(refs), "ANIMA_INNER_IMAGES": NAMES}


def test_R171_inner_images_survive_a_round_trip_through_the_cache(images, tmp_path):
    """Proves that the images are saved as one archive, that a second save writes
    over the first (PM-010: the tool refuses to), and that loading brings them back
    after they were removed and leaves no archive behind."""
    refs, built = images
    cache = tmp_path / "cache"
    first = task("cache-pack", str(cache), env=environment(refs))
    assert first.returncode == 0, first.stderr
    archive = cache / "images.tar"
    assert archive.stat().st_size > 0

    # The archive of an earlier run is in the way of `podman save`: it is replaced.
    archive.write_text("left by an earlier run")
    second = task("cache-pack", str(cache), env=environment(refs))
    assert second.returncode == 0, second.stderr
    assert archive.stat().st_size > len("left by an earlier run")

    run(["podman", "rmi", "--force", *built], check=True)
    assert not any(exists(reference) for reference in built)

    loaded = task("cache-load", str(cache))
    assert loaded.returncode == 0, loaded.stderr
    assert all(exists(reference) for reference in built)
    assert not archive.exists()


def test_R171_inner_images_survive_a_round_trip_through_the_cache_detects_violation(
    images, tmp_path
):
    """An image that was not built, a reference file that is empty, a cache without
    an archive and an archive that is not one fail the commands, and a failed save
    leaves no archive when a reference is missing."""
    refs, _built = images
    cache = tmp_path / "cache"

    (refs / "beta.ref").unlink()
    result = task("cache-pack", str(cache), env=environment(refs))
    assert result.returncode != 0 and "beta" in result.stderr
    assert not (cache / "images.tar").exists()

    (refs / "beta.ref").write_text("")
    assert task("cache-pack", str(cache), env=environment(refs)).returncode != 0

    # A reference to an image that is not in the store.
    (refs / "beta.ref").write_text("localhost/anima-ci-test/absent:none\n")
    assert task("cache-pack", str(cache), env=environment(refs)).returncode != 0

    empty = tmp_path / "empty"
    empty.mkdir()
    assert task("cache-load", str(empty)).returncode != 0

    (empty / "images.tar").write_text("not an archive")
    assert task("cache-load", str(empty)).returncode != 0
    assert Path(empty / "images.tar").exists(), (
        "a failed load keeps what it could not read"
    )
