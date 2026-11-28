"""The commands of the promotion, run for real. R115 and R171.

Each test runs a command of `mise-tasks/promote/` as a workflow step does, with
real podman, a throwaway registry on a local port and a tiny image (PM-013,
PM-014). The `_detects_violation` companions feed a command what it must
refuse, or show that the oracle of a test would see the fault. What is not run
here is the last call of `green` and `release` to GitHub: a fake `gh` on the
path records the calls and answers what GitHub answers (`anima-branching-and-releasing`).
"""

import base64
import json
import os
import subprocess

from helpers import ROOT, outputs, podman, run_task

REPOSITORY = "cocreiamo/anima"
# What the workflow passes to the commands that write: the installation token of the
# promote App, never the workflow's own token (R171, TASK-53).
APP_TOKEN = "app-installation-token"


def repository(registry):
    return f"{registry.host}/{REPOSITORY}"


def publish(registry, built, version="0.0.1", env=None):
    return run_task(
        "publish",
        env={
            "VERSION": version,
            "REF": built.ref,
            "ANIMA_REPOSITORY": repository(registry),
            **(env or {}),
        },
    )


# ---- R115: a published tag is never moved; "cannot tell" is not "does not exist" ----------------


def test_R115_published_tag_is_never_moved_and_unknown_is_not_absent(
    registry, make_image
):
    first, second = make_image(), make_image()
    tag = f"{repository(registry)}:0.0.1"

    assert run_task("tag-state", tag).stdout.strip() == "absent"
    pushed = publish(registry, first)
    assert pushed.returncode == 0, pushed.stderr
    held = registry.digest(REPOSITORY, "0.0.1")
    assert held and outputs(pushed) == {
        "reference": f"{repository(registry)}@{held}",
        "existing": "false",
    }
    assert run_task("tag-state", tag).stdout.strip() == "exists"
    assert run_task("registry-digest", tag).stdout.strip() == held

    # A re-run with another build: nothing is pushed, the tag keeps its digest,
    # and the reference is the digest the registry holds.
    again = publish(registry, second)
    assert again.returncode == 0, again.stderr
    assert registry.digest(REPOSITORY, "0.0.1") == held
    assert outputs(again) == {
        "reference": f"{repository(registry)}@{held}",
        "existing": "true",
    }

    # The registry cannot be reached: unknown, a failure, and nothing is pushed.
    registry.stop()
    state = run_task("tag-state", tag)
    assert (state.returncode, state.stdout.strip()) == (1, "unknown")
    refused = publish(registry, second, version="0.0.2")
    assert refused.returncode != 0
    assert "reference=" not in refused.stdout


def test_R115_published_tag_is_never_moved_and_unknown_is_not_absent_detects_violation(
    registry, make_image
):
    """The oracle sees a moved tag: pushing over it by hand, as a check that
    always answered "absent" would, changes the digest the registry reports."""
    first, second = make_image(), make_image()
    assert publish(registry, first).returncode == 0
    held = registry.digest(REPOSITORY, "0.0.1")
    podman(
        "push", "--tls-verify=false", second.ref,
        f"docker://{repository(registry)}:0.0.1",
    )  # fmt: skip
    assert registry.digest(REPOSITORY, "0.0.1") != held
    # An absent tag of a package the registry has never seen is absent, not unknown.
    other = f"{registry.host}/cocreiamo/never-pushed:1"
    assert run_task("tag-state", other).stdout.strip() == "absent"
    # The prefixed form that podman 4.9.3 cannot use is not what the command asks.
    assert (
        "docker://"
        not in (ROOT / "mise-tasks/promote/tag-state")
        .read_text()
        .split("podman manifest inspect", 1)[1]
        .split("\n", 1)[0]
    )


def test_R115_promotion_loads_only_the_image_that_passed(
    registry, make_image, tmp_path
):
    built = make_image()
    cache = tmp_path / "engine"
    cache.mkdir()
    (cache / "engine.ref").write_text(built.ref)
    (cache / "engine.id").write_text(built.id)
    archive = tmp_path / "engine-image.tar"

    archived = run_task("archive", str(archive), env={"ANIMA_ENGINE_CACHE": str(cache)})
    assert archived.returncode == 0, archived.stderr
    assert outputs(archived) == {"image-id": built.id}

    podman("rmi", "--force", built.ref)
    loaded = run_task("load", str(archive), built.id)
    assert loaded.returncode == 0, loaded.stderr
    assert outputs(loaded) == {"ref": built.ref}
    assert (
        podman("image", "inspect", "--format", "{{.Id}}", built.ref).stdout.strip()
        == built.id
    )

    # What was loaded is what is published: the registry holds the image's config.
    pushed = publish(registry, built)
    assert pushed.returncode == 0, pushed.stderr
    manifest = podman(
        "manifest", "inspect", "--tls-verify=false", f"{repository(registry)}:0.0.1"
    ).stdout
    assert json.loads(manifest)["config"]["digest"] == f"sha256:{built.id}"


def test_R115_promotion_loads_only_the_image_that_passed_detects_violation(
    make_image, tmp_path
):
    built, other = make_image(), make_image()
    archive = tmp_path / "other.tar"
    podman("save", "--output", str(archive), other.ref)
    podman("rmi", "--force", other.ref)
    # The archive holds another image than the one that passed.
    wrong = run_task("load", str(archive), built.id)
    assert wrong.returncode != 0
    assert "ref=" not in wrong.stdout
    # An archive that is not one.
    junk = tmp_path / "junk.tar"
    junk.write_text("not an archive")
    assert run_task("load", str(junk), built.id).returncode != 0
    # An engine record that names an image other than the one verified.
    cache = tmp_path / "engine"
    cache.mkdir()
    (cache / "engine.ref").write_text(built.ref)
    (cache / "engine.id").write_text(other.id)
    mismatch = run_task(
        "archive", str(tmp_path / "x.tar"), env={"ANIMA_ENGINE_CACHE": str(cache)}
    )
    assert mismatch.returncode != 0
    assert not (tmp_path / "x.tar").exists()


def test_R115_commands_run_through_mise(registry):
    """A step calls `mise run`: its standard output is the command's alone."""
    done = subprocess.run(
        [
            "mise",
            "run",
            "--quiet",
            "promote:tag-state",
            f"{repository(registry)}:0.0.1",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert (done.returncode, done.stdout) == (0, "absent\n"), done.stderr


def test_R115_commands_run_through_mise_detects_violation(registry):
    done = subprocess.run(
        ["mise", "run", "--quiet", "promote:tag-state"],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert done.returncode != 0


# ---- R171: what is planned, advanced and released, with GitHub replaced by a recorder ---------


def fake_gh(tmp_path, released=False, green=False, version="0.0.1"):
    """A `gh` that records its calls and answers as GitHub does."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    log = tmp_path / "gh.log"
    content = base64.b64encode(json.dumps({".": version}).encode()).decode()
    script = tmp_path / "bin" / "gh"
    script.parent.mkdir()
    script.write_text(
        "#!/bin/bash\n"
        f'echo "$@" >> "{log}"\n'
        f'echo "$GH_TOKEN" >> "{log}.tokens"\n'
        'case "$1 $2" in\n'
        f'  "release view") exit {0 if released else 1};;\n'
        f'  "api repos/cocreiamo/anima/git/ref/heads/main-green") exit {0 if green else 1};;\n'
        f'  "api repos/cocreiamo/anima/contents/.github/release-please-manifest.json?ref=abc123") echo "{content}";;\n'
        "esac\n"
    )
    script.chmod(0o755)
    env = {
        "PATH": f"{script.parent}:{os.environ['PATH']}",
        "GITHUB_REPOSITORY": REPOSITORY,
        "GH_TOKEN": APP_TOKEN,
    }
    return log, env


def calls(log):
    return log.read_text().splitlines() if log.exists() else []


def tokens(log):
    """The token the fake `gh` saw at each call: what the command was given."""
    path = log.parent / "gh.log.tokens"
    return path.read_text().splitlines() if path.exists() else []


def test_R171_release_commands_decide_as_stated(tmp_path):
    manifest = tmp_path / "manifest.json"
    # A version is prepared and has no release: publish.
    manifest.write_text('{".": "0.0.1"}')
    log, env = fake_gh(tmp_path / "a")
    planned = run_task("plan", str(manifest), env=env)
    assert outputs(planned) == {"version": "0.0.1", "publish": "true"}
    assert calls(log) == ["release view v0.0.1 --repo cocreiamo/anima"]

    # Nothing is prepared, or the version is released: do not publish.
    manifest.write_text('{".": "0.0.0"}')
    assert outputs(run_task("plan", str(manifest), env=env))["publish"] == "false"
    manifest.write_text('{".": "0.0.1"}')
    _, released = fake_gh(tmp_path / "b", released=True)
    assert outputs(run_task("plan", str(manifest), env=released))["publish"] == "false"

    # main-green is created when absent, fast-forwarded (never forced) when present.
    log, env = fake_gh(tmp_path / "c")
    assert run_task("green", "abc123", env=env).returncode == 0
    assert calls(log)[-1] == (
        "api --method POST repos/cocreiamo/anima/git/refs "
        "-f ref=refs/heads/main-green -f sha=abc123 --silent"
    )
    log, env = fake_gh(tmp_path / "d", green=True)
    assert run_task("green", "abc123", env=env).returncode == 0
    assert calls(log)[-1] == (
        "api --method PATCH repos/cocreiamo/anima/git/refs/heads/main-green "
        "-f sha=abc123 -F force=false --silent"
    )

    # The release names the image, and says so when an earlier run pushed it.
    published = "ghcr.io/cocreiamo/anima@sha256:" + "a" * 64
    log, env = fake_gh(tmp_path / "e")
    done = run_task("release", "abc123", env={**env, "IMAGE": published})
    assert done.returncode == 0, done.stderr
    assert calls(log)[-1] == (
        "release create v0.0.1 --repo cocreiamo/anima --target abc123 "
        f"--generate-notes --notes Engine image: `{published}`"
    )
    log, env = fake_gh(tmp_path / "f")
    run_task("release", "abc123", env={**env, "IMAGE": published, "EXISTING": "true"})
    assert "published by an earlier run; the tag already existed" in calls(log)[-1]

    # Every call that moves main-green or creates the release is made with the token
    # the step gave.
    for name, written in (("g", "green"), ("r", "release")):
        log, env = fake_gh(tmp_path / name)
        run_task(written, "abc123", env={**env, "IMAGE": published})
        assert tokens(log) and set(tokens(log)) == {APP_TOKEN}


def test_R171_release_commands_decide_as_stated_detects_violation(tmp_path):
    # No image was published: the release is refused, and nothing is created.
    log, env = fake_gh(tmp_path / "a")
    refused = run_task("release", "abc123", env={**env, "IMAGE": ""})
    assert refused.returncode != 0
    assert not any(c.startswith("release create") for c in calls(log))
    # Already released: nothing is created.
    log, env = fake_gh(tmp_path / "b", released=True)
    run_task("release", "abc123", env={**env, "IMAGE": "x@sha256:" + "b" * 64})
    assert not any(c.startswith("release create") for c in calls(log))
    # No version prepared: nothing is created.
    log, env = fake_gh(tmp_path / "c", version="0.0.0")
    run_task("release", "abc123", env={**env, "IMAGE": "x@sha256:" + "b" * 64})
    assert not any(c.startswith("release create") for c in calls(log))
    # No token given: the commands fail before calling the platform, instead of
    # falling back to another credential.
    for name in ("green", "release"):
        log, env = fake_gh(tmp_path / f"t{name}")
        env["GH_TOKEN"] = ""
        given = "ghcr.io/cocreiamo/anima@sha256:" + "b" * 64
        refused = run_task(name, "abc123", env={**env, "IMAGE": given})
        assert refused.returncode != 0 and "GH_TOKEN" in refused.stderr
        assert calls(log) == []
    # No repository named: the commands fail instead of guessing.
    assert run_task("green", "abc123", env={"GITHUB_REPOSITORY": ""}).returncode != 0
