"""The build of the identity provider's image. R168 and R169 (PM-015, TASK-43).

The container file is read as text: building it takes minutes and the network.
Each check is a function of its inputs and has a `_detects_violation` companion
that feeds it a deliberately wrong one. The Maven that the builder holds is
recorded in the register as part of the image's tag, so the check against the
fork's wrapper needs no network; it reads the fork's file when the fork is
checked out and is skipped, with its reason, when it is not.
"""

import re

import pytest
from repo_facts import tool_images
from sysml_model import ROOT

CONTAINERFILE = ROOT / "engine" / "access" / "Containerfile"
WRAPPER = (
    ROOT / "third_party" / "keycloak" / ".mvn" / "wrapper" / "maven-wrapper.properties"
)
BUILDER = re.compile(
    r"^ARG BUILDER=(?P<image>[^:@\s]+):(?P<tag>\S+?)@(?P<digest>sha256:[0-9a-f]{64})$",
    re.MULTILINE,
)
# Words that start a download in a container file: the wrapper, and the programs
# that fetch a file. The package installer is not one of them: the distribution's
# packages are pinned by TASK-43 step 4.
DOWNLOADERS = re.compile(r"(?<![\w-])(mvnw(?:\.cmd)?|wget|curl|fetch)(?![\w-])")
MAX_RETRIES = 20


def code(text):
    """The lines of a container file that are not comments, continuations joined."""
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    return re.sub(r"\\\n", " ", "\n".join(lines))


def maven_entry(register):
    found = [t for t in register if t.get("name") == "maven"]
    return found[0] if len(found) == 1 else None


def build_faults(containerfile, register):
    """Why the build may download a build tool, or []."""
    faults = []
    entry = maven_entry(register)
    if entry is None:
        return ["the register holds no single entry for the Maven image"]
    m = BUILDER.search(containerfile)
    if not m:
        return ["the builder is not an image with a tag and a digest"]
    if m["image"] != entry["image"] or m["digest"] != entry["digest"]:
        faults.append("the builder is not the register's Maven image at its digest")
    if m["tag"] != entry["version"]:
        faults.append("the builder's tag is not the register's version")
    body = code(containerfile)
    if not re.search(r"^RUN\s+mvn\s", body, re.MULTILINE):
        faults.append("no step runs `mvn` of the builder")
    faults += [f"calls `{w}`" for w in sorted(set(DOWNLOADERS.findall(body)))]
    return faults


def wrapper_version(properties):
    m = re.search(
        r"^distributionUrl=.*/apache-maven-([0-9][^/-]*)-bin\.",
        properties,
        re.MULTILINE,
    )
    return m.group(1) if m else None


def version_faults(properties, register):
    entry = maven_entry(register)
    wanted = wrapper_version(properties)
    if entry is None or wanted is None:
        return ["cannot read the versions"]
    have = entry["version"].split("-", 1)[0]
    return (
        []
        if have == wanted
        else [f"image has Maven {have}, the wrapper names {wanted}"]
    )


def retry_faults(containerfile):
    body = code(containerfile)
    m = re.search(r"-Daether\.connector\.http\.retryHandler\.count=(\d+)", body)
    if not m:
        return ["no retry count is set through the resolver's setting"]
    if not 1 <= int(m[1]) <= MAX_RETRIES:
        return [f"the retry count {m[1]} is not between 1 and {MAX_RETRIES}"]
    if re.search(r"\b(until|while|for)\b[^\n]*\bmvn\b|\bretry\b", body):
        return ["a shell loop wraps the build"]
    return []


# ---- the checks -------------------------------------------------------------------------------


def test_R168_build_downloads_no_build_tool():
    assert build_faults(CONTAINERFILE.read_text(), tool_images()) == []


def test_R168_build_downloads_no_build_tool_detects_violation():
    # The samples take the image's name from the register: no reference of their own.
    entry = {
        **maven_entry(tool_images()),
        "version": "3.9.1-x",
        "digest": "sha256:" + "a" * 64,
    }
    register = [entry]
    where = entry["image"]
    good = (
        f"ARG BUILDER={where}:3.9.1-x@sha256:" + "a" * 64 + "\n"
        "FROM ${BUILDER} AS dist\n"
        "# ./mvnw is not run: only a comment\n"
        "RUN mvn -B clean install\n"
    )
    assert build_faults(good, register) == []
    assert build_faults(good.replace("RUN mvn", "RUN ./mvnw"), register)
    assert build_faults(good + "RUN wget https://example.invalid/m.zip\n", register)
    assert build_faults(good.replace("a" * 64, "b" * 64), register)
    assert build_faults(good.replace("3.9.1-x@", "3.9.2-x@"), register)
    assert build_faults(good.replace(where, where + "-other"), register)
    assert build_faults(good, [])
    assert build_faults(good.replace("RUN mvn", "RUN echo"), register)


def test_R168_maven_version_equals_the_forks_wrapper():
    if not WRAPPER.is_file():
        pytest.skip(
            "third_party/keycloak is not checked out: the wrapper cannot be read"
        )
    assert version_faults(WRAPPER.read_text(), tool_images()) == []


def test_R168_maven_version_equals_the_forks_wrapper_detects_violation():
    register = [{"name": "maven", "version": "3.9.16-eclipse-temurin-21"}]
    url = "distributionUrl=https://r.example/maven2/org/apache/maven/apache-maven/{}/apache-maven-{}-bin.zip\n"
    assert version_faults(url.format("3.9.16", "3.9.16"), register) == []
    assert version_faults(url.format("3.9.17", "3.9.17"), register)
    assert version_faults("distributionType=only-script\n", register)
    assert version_faults(url.format("3.9.16", "3.9.16"), [])


def test_R169_build_retries_downloads_bounded():
    assert retry_faults(CONTAINERFILE.read_text()) == []


def test_R169_build_retries_downloads_bounded_detects_violation():
    good = "RUN mvn -B -Daether.connector.http.retryHandler.count=10 clean install\n"
    assert retry_faults(good) == []
    assert retry_faults("RUN mvn -B clean install\n")
    assert retry_faults(good.replace("=10", "=0"))
    assert retry_faults(good.replace("=10", "=500"))
    assert retry_faults("RUN until mvn -B clean install; do sleep 5; done\n" + good)
    assert retry_faults("# " + good)
