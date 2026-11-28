"""The compile stages of the engine's images run with the network off. R167 (TASK-43).

A build that downloads what it compiles depends on inputs the repository does
not hold: a module proxy that is down, a registry that deleted a digest. A
converted component fetches its dependencies in one stage that does nothing else,
keeps them as an image of their own, and compiles with the network off. These
checks read the container file as text and feed on a deliberately wrong one in
their `_detects_violation` companions; that the build succeeds offline, and
fails naming what is missing, is R168 (tests/system/test_offline_build.py), which
builds.
"""

import re

from sysml_model import ROOT

# The container files converted so far, each with the stage that fetches and the
# stage that holds what was fetched (the lock file is go.sum, carried by the fork).
CONVERTED = ["engine/secrets/Containerfile"]
FETCH, DEPENDENCIES = "fetch", "dependencies"
# What can weaken the check of a dependency against the lock file, or fetch past it.
WEAKENING = re.compile(
    r"GONOSUMDB|GONOSUMCHECK|GOSUMDB\s*=\s*off|GOFLAGS\s*=\s*\S*-(?:mod=mod|insecure)|"
    r"GOINSECURE|GOPRIVATE|GONOSUMCHECK|GOPROXY\s*=\s*(?!off\b)|GOTOOLCHAIN\s*=\s*(?!local\b)"
)
# A command of the go tool that compiles, or that needs the modules to be there.
GO_COMPILE = re.compile(r"\bgo\s+(?:build|list|install|vet|test|run|generate)\b")
GO_FETCH_ONLY = re.compile(r"go mod (?:download|verify)")


def stages(text):
    """{stage name: [instruction, ...]}, the continuation lines joined. A stage
    without a name takes its position."""
    joined = re.sub(r"\\\n", " ", text)
    found, current = {}, None
    for line in joined.splitlines():
        line = line.strip()
        if m := re.match(r"FROM\s+\S+(?:\s+AS\s+(\S+))?", line, re.IGNORECASE):
            current = m.group(1) or f"stage{len(found)}"
            found[current] = [line]
        elif current and line and not line.startswith("#"):
            found[current].append(line)
    return found


def offline_faults(text):
    """What is wrong with a converted container file, as a list of sentences."""
    faults = []
    found = stages(text)
    for name in (FETCH, DEPENDENCIES):
        if name not in found:
            return [f"there is no stage `{name}`"]

    # The stage that fetches does nothing but fetch and check against go.sum.
    runs = [i for i in found[FETCH] if i.startswith("RUN ")]
    if not runs or not any("go mod download" in r for r in runs):
        faults.append(f"stage `{FETCH}` does not run `go mod download`")
    if not any("go mod verify" in r for r in runs):
        faults.append(f"stage `{FETCH}` does not run `go mod verify`")
    for r in runs:
        body = r.removeprefix("RUN ")
        if "--network" in body or not all(
            GO_FETCH_ONLY.fullmatch(part.strip()) for part in body.split("&&")
        ):
            faults.append(f"stage `{FETCH}` does more than fetch: {r}")
    for i in found[FETCH]:
        if i.startswith(("ADD ", "COPY ")) and "--from=openbao" not in i:
            faults.append(f"stage `{FETCH}` takes input other than the fork: {i}")

    # The stage that holds what was fetched is the cache and nothing else.
    holder = found[DEPENDENCIES]
    if holder[0].split()[1] != "scratch":
        faults.append(f"stage `{DEPENDENCIES}` is not made from scratch")
    if len(holder) != 2:
        faults.append(f"stage `{DEPENDENCIES}` is not one copy of the fetched cache")
    for i in holder[1:2]:
        if not re.fullmatch(rf"COPY --from={FETCH} \S+ \S+", i):
            faults.append(
                f"stage `{DEPENDENCIES}` holds more than the fetched cache: {i}"
            )

    # Every other stage that compiles runs with the network off, on the cache only.
    compile_stages = [
        n
        for n, instructions in found.items()
        if n not in (FETCH, DEPENDENCIES)
        and any(
            i.startswith("RUN ") and (GO_COMPILE.search(i) or "go mod verify" in i)
            for i in instructions
        )
    ]
    if not compile_stages:
        faults.append("no stage compiles")
    for n in compile_stages:
        for i in found[n]:
            if i.startswith("RUN ") and not re.match(r"RUN\s+--network=none\s", i):
                faults.append(f"stage `{n}` runs with the network: {i}")
    # The environment of the stages that compile, with the ones they build from.
    for n in compile_stages:
        parent = re.match(r"FROM\s+(\S+)", found[n][0]).group(1)
        chain = [n] + ([parent] if parent in found else [])
        env = " ".join(i for c in chain for i in found[c] if i.startswith("ENV "))
        if "GOPROXY=off" not in env:
            faults.append(f"stage `{n}` does not set GOPROXY=off")
        if "GOTOOLCHAIN=local" not in env:
            faults.append(f"stage `{n}` does not set GOTOOLCHAIN=local")
        if not any(
            re.fullmatch(rf"COPY --from={DEPENDENCIES} \S+ \S+", i)
            for c in chain
            for i in found[c]
        ):
            faults.append(
                f"stage `{n}` does not take its modules from `{DEPENDENCIES}`"
            )
    if "GOTOOLCHAIN=local" not in " ".join(found[FETCH]):
        faults.append(f"stage `{FETCH}` does not set GOTOOLCHAIN=local")
    if "-mod=readonly" not in " ".join(found[FETCH]):
        faults.append(f"stage `{FETCH}` may change go.sum (no -mod=readonly)")
    code = " ".join(i for instructions in found.values() for i in instructions)
    if weakened := WEAKENING.search(code):
        faults.append(
            f"the check against the lock file is weakened: {weakened.group(0)}"
        )
    # The fetch and the compile stages are built from the one builder image.
    builders = {
        base
        for n in (FETCH, *compile_stages)
        if (base := re.match(r"FROM\s+(\S+)", found[n][0]).group(1)) not in found
    }
    if len(builders) > 1:
        faults.append(f"the stages use different builder images: {sorted(builders)}")
    return faults


def converted():
    return {path: (ROOT / path).read_text() for path in CONVERTED}


def test_R167_compile_stages_run_with_network_off():
    """Proves that each converted container file fetches in one stage that does
    nothing else, compiles with the network off from that stage's cache, with the
    builder's own toolchain and the lock file's check intact."""
    for path, text in converted().items():
        assert offline_faults(text) == [], path
    # The build task builds the dependencies image from its own stage, tags it from the
    # fork's go.mod and go.sum, and hands it to the build as the context `dependencies`.
    build = (ROOT / "mise-tasks/engine/build").read_text()
    assert (
        "build secrets-dependencies engine/secrets/Containerfile dependencies" in build
    )
    assert '--build-context "dependencies=container-image://' in build
    assert 'extra="third_party/openbao/go.mod third_party/openbao/go.sum"' in build


def test_R167_compile_stages_run_with_network_off_detects_violation():
    text = converted()["engine/secrets/Containerfile"]
    assert offline_faults(text) == []
    wrong = {
        "a compile with the network": text.replace(
            "RUN --network=none CGO_ENABLED=0 go build", "RUN CGO_ENABLED=0 go build"
        ),
        "a verification with the network": text.replace(
            "RUN --network=none go mod verify", "RUN go mod verify"
        ),
        "a proxy": text.replace("GOPROXY=off", "GOPROXY=https://proxy.golang.org"),
        "no toolchain pin": text.replace(
            "GOTOOLCHAIN=local GOPROXY=off", "GOPROXY=off"
        ),
        "a toolchain that may be downloaded": text.replace(
            "GOTOOLCHAIN=local GOPROXY", "GOTOOLCHAIN=auto GOPROXY"
        ),
        "a sum database switched off": text.replace(
            "GOPROXY=off", "GOPROXY=off GONOSUMDB=*"
        ),
        "a go.sum that may change": text.replace(
            "GOFLAGS=-mod=readonly GOMODCACHE=/deps/mod\nCOPY",
            "GOMODCACHE=/deps/mod\nCOPY",
        ),
        "a fetch that compiles": text.replace(
            "RUN go mod download && go mod verify",
            "RUN go mod download && go mod verify && go build ./...",
        ),
        "a fetch that is not verified": text.replace(
            "RUN go mod download && go mod verify", "RUN go mod download"
        ),
        "a cache with more than the cache": text.replace(
            "COPY --from=fetch /deps/mod /mod",
            "COPY --from=fetch /deps/mod /mod\nCOPY --from=fetch /src /src",
        ),
        "modules not from the cache": text.replace(
            "COPY --from=dependencies /mod /deps/mod\n", ""
        ),
        "another builder": text.replace(
            "FROM ${GOLANG} AS verified",
            "FROM " + "docker.io" + "/library/golang:1.27 AS verified",
        ),
    }
    for what, changed in wrong.items():
        assert changed != text, what
        assert offline_faults(changed), what
    assert offline_faults("FROM scratch AS bin\n")
