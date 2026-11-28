"""The decisions of the system tests that need no engine to be tested.

Each is a function of text or of a recorded state, so that it runs in every
`pytest` run and can be shown to fail on a wrong input (PM-008).
"""

import json
import re
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser

PASSED = re.compile(r"All (\d+) tests passed")


def regress_tests_passed(result: str) -> int | None:
    """The number of tests the upstream suite reports as all passed, or None.

    `result` is the file the build step keeps in the image, not the output of the
    build: a cached build does not print the step again.
    """
    matches = PASSED.findall(result)
    return int(matches[-1]) if matches else None


def container_phase(inspected_state: str) -> str:
    """`running`, `stopping`, `stopped` or `unknown`, from the JSON of `podman
    inspect --format '{{json .State}}'`. Only a state that says the container is
    not running and has `exited` is `stopped`: that status is set when the cleanup
    of the run has finished. Status `stopped` is podman's guess after its wait for
    the exit timed out (ExitCode -1); the run is not finished and is `stopping`.
    An empty or unreadable answer is `unknown`."""
    try:
        state = json.loads(inspected_state)
    except ValueError:
        return "unknown"
    if not isinstance(state, dict):
        return "unknown"
    if state.get("Running") is True and not state.get("Paused"):
        return "running"
    if state.get("Running") is False and state.get("Status") == "exited":
        return "stopped"
    if state.get("Running") is False and state.get("Status") == "stopped":
        return "stopping"
    return "unknown"


def secret_store_storage_stage(keys: list[str]) -> str:
    """How far the secret store's first start got, from the keys of its storage
    table (`path || key`, one per row): `empty`, `barrier` (key ring written,
    seal configuration not yet), `initialised` (and self-initialisation not
    marked as started, or finished), `self-initialising` (marked as started and
    not finished), or `unknown` for rows that fit none of these."""
    present = set(keys)
    if not present:
        return "empty"
    if "/core/status/self-init" in present:
        return "self-initialising"
    if "/core/seal-config" in present:
        return "initialised"
    if "/core/keyring" in present:
        return "barrier"
    return "unknown"


def certificate_facts(openssl_output: str) -> dict | None:
    """The serial and the end of validity (seconds since the epoch) of a certificate,
    from `openssl x509 -noout -serial -enddate`; None when either is missing."""
    serial = re.search(r"^serial=(\S+)", openssl_output, re.MULTILINE)
    end = re.search(r"^notAfter=(.+?)\s*$", openssl_output, re.MULTILINE)
    if not serial or not end:
        return None
    try:
        stamp = datetime.strptime(end.group(1), "%b %d %H:%M:%S %Y GMT")
    except ValueError:
        return None
    return {
        "serial": serial.group(1),
        "not_after": stamp.replace(tzinfo=UTC).timestamp(),
    }


def renewal_faults(
    before: dict, after: dict, now: float, start_before: str, start_after: str
) -> list[str]:
    """What is wrong with a renewal seen from outside (R118): the certificate must
    be another one, that outlives the first, taken while the first was still valid,
    by a server that was not restarted (its start time is the same)."""
    faults = []
    if after["serial"] == before["serial"]:
        faults.append("the certificate presented is still the first one")
    if after["not_after"] <= before["not_after"]:
        faults.append("the new certificate does not outlive the first")
    if now >= before["not_after"]:
        faults.append("the first certificate had already expired")
    if start_after != start_before:
        faults.append("the database server was restarted")
    return faults


def renewal_failure_faults(status: str, output: str) -> list[str]:
    """What is wrong with the readiness answer after a failed renewal (R119): it
    must be negative (not `healthy`) and its text must say that the certificate
    could not be renewed."""
    faults = []
    if status == "healthy":
        faults.append("the engine still answers ready")
    if "certificate renewal failed" not in output:
        faults.append("the answer does not say that the renewal failed")
    return faults


class _Forms(HTMLParser):
    """The first form of a page: its action and its named fields and buttons."""

    def __init__(self):
        super().__init__()
        self.action: str | None = None
        self.fields: list[tuple[str, str, str]] = []  # (name, type, value)
        self._inside = False
        self._done = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form" and self.action is None:
            self.action = a.get("action") or ""
            self._inside = True
        elif self._inside and tag in ("input", "button") and a.get("name"):
            kind = a.get("type") or ("submit" if tag == "button" else "text")
            self.fields.append((a["name"], kind, a.get("value") or ""))

    def handle_endtag(self, tag):
        if tag == "form" and self._inside:
            self._inside = False


def form_submission(
    html: str, username: str, password: str
) -> tuple[str, dict[str, str]] | None:
    """What a person's browser sends for the first form of `html`: the action and
    the fields, with the username and password filled in. A submit button is sent
    unless it is the one that refuses (`cancel`). None when the page has no form,
    that is, the flow is over."""
    page = _Forms()
    page.feed(html)
    if page.action is None:
        return None
    data: dict[str, str] = {}
    for name, kind, value in page.fields:
        if name == "username":
            data[name] = username
        elif name == "password":
            data[name] = password
        elif kind == "submit":
            if name != "cancel":
                data[name] = value
        elif kind != "checkbox":
            data[name] = value
    return unescape(page.action), data


def audit_names_person(log: str, person: str, role: str) -> bool:
    """True when one session of the server log shows the identity `person` and the
    role `role` together: the line `connection authenticated: identity="<person>"
    method=oauth` and a line that opens the session as `user=<role>`, with the
    same process number in their prefix. Not enough: the person in one session and
    the role in another."""
    authenticated = re.compile(
        r"\[(\d+)\][^\n]*connection authenticated: identity=\""
        + re.escape(person)
        + r"\" method=oauth"
    )
    authorized = re.compile(
        r"\[(\d+)\][^\n]*connection authorized:[^\n]* user="
        + re.escape(role)
        + r"(?:\s|$)"
    )
    people = {m.group(1) for m in authenticated.finditer(log)}
    roles = {m.group(1) for m in authorized.finditer(log)}
    return bool(people & roles)


def production_faults(log: str, database_rows: int) -> list[str]:
    """What is wrong with the identity provider's start, seen from its log and its
    database (R123): it must report the production profile, never the development
    one nor its warning, and its state must be rows of its own database."""
    faults = []
    if "Profile prod activated" not in log:
        faults.append("the log does not report the production profile")
    if "Profile dev activated" in log or "development mode" in log:
        faults.append("the log reports the development mode")
    if database_rows <= 0:
        faults.append("its own database holds no realm")
    return faults


def issuer_faults(issuers: dict[str, str], expected: str) -> list[str]:
    """The names of the requests (R116) whose answer carried another issuer than
    the configured one; `issuers` maps the name used to the issuer received, and
    holds at least two names (one name proves nothing about "whatever name")."""
    faults = [
        f"{name}: {issuer!r}" for name, issuer in issuers.items() if issuer != expected
    ]
    if len(issuers) < 2:
        faults.append("fewer than two names were tried")
    return faults


def temporary_administrators(users: list[dict]) -> list[str]:
    """The users of a realm marked temporary administrators (R117): the attribute
    `is_temporary_admin` holding `true`. A service account is a user too."""
    return [
        str(user.get("username"))
        for user in users
        if "true" in (user.get("attributes") or {}).get("is_temporary_admin", [])
    ]


# ---- The HTTP entry point (ADR 0008) -----------------------------------------

# Every forwarding header other than the standard one (RFC 7239) that a client can
# send and that a backend could be made to trust (R132).
OTHER_FORWARDING_HEADERS = (
    "X-Forwarded-For",
    "X-Forwarded-Host",
    "X-Forwarded-Proto",
    "X-Forwarded-Port",
    "X-Forwarded-Prefix",
    "X-Forwarded-Server",
    "X-Forwarded-Ssl",
    "X-Original-Forwarded-For",
    "X-Real-IP",
    "Front-End-Https",
    "X-Url-Scheme",
)


def routing_faults(
    answers: dict[str, int], forwarded: list[str], refused: list[str]
) -> list[str]:
    """What is wrong with the answers of the entry (R128, R129), by request path:
    a path that must be forwarded and was not answered 200, and a path that must
    be refused and was answered anything else than 404. Both lists must be
    non-empty: a check that asked nothing proves nothing."""
    faults = []
    if not forwarded or not refused:
        faults.append("the check asked for no forwarded path or for no refused path")
    for path in forwarded:
        if answers.get(path) != 200:
            faults.append(f"{path} was answered {answers.get(path)}, not forwarded")
    for path in refused:
        if answers.get(path) != 404:
            faults.append(f"{path} was answered {answers.get(path)}, not 404")
    return faults


def forwarding_faults(
    received: list[tuple[str, str]], client: str, host: str, proto: str
) -> list[str]:
    """What is wrong with the headers a backend received after a client sent forged
    forwarding headers (R132): exactly one `Forwarded` header, naming the client's
    address, the host the client asked for and the scheme of the connection, with no
    trace of the forged values, and none of the other forwarding headers."""
    faults = []
    forwarded = [v for k, v in received if k.lower() == "forwarded"]
    if len(forwarded) != 1:
        faults.append(f"{len(forwarded)} Forwarded headers received, one expected")
    else:
        value = forwarded[0]
        pairs = {}
        for part in value.split(";"):
            key, _, text = part.partition("=")
            pairs[key.strip().lower()] = text.strip().strip('"').strip("[]")
        if pairs.get("for") != client:
            faults.append(f"for is {pairs.get('for')!r}, not {client!r}")
        if pairs.get("host") != host:
            faults.append(f"host is {pairs.get('host')!r}, not {host!r}")
        if pairs.get("proto") != proto:
            faults.append(f"proto is {pairs.get('proto')!r}, not {proto!r}")
        if "forged" in value.lower() or "6.6.6.6" in value:
            faults.append("the forged value was passed on")
    present = {k.lower() for k, _ in received}
    for name in OTHER_FORWARDING_HEADERS:
        if name.lower() in present:
            faults.append(f"{name} was passed on")
    return faults


def listener_faults(listeners: list[str], loopback_only: list[int]) -> list[str]:
    """What is wrong with the listening sockets of the engine (R135), from the lines
    of `ss -Hltn` (`LISTEN 0 4096 <address>:<port> <peer>`): each port of
    `loopback_only` must be listened on, and only on the loopback address."""
    faults = []
    for port in loopback_only:
        addresses = []
        for line in listeners:
            fields = line.split()
            if len(fields) >= 4:
                address, _, number = fields[3].rpartition(":")
                if number == str(port):
                    addresses.append(address.strip("[]"))
        if not addresses:
            faults.append(f"port {port} is not listened on")
        for address in addresses:
            if address not in ("127.0.0.1", "::1", "::ffff:127.0.0.1"):
                faults.append(f"port {port} is listened on at {address}")
    return faults


def published_faults(published: dict[str, list[str]], expected: set[str]) -> list[str]:
    """What is wrong with the ports published to the outside (R135, R30): exactly the
    expected ports, each on the loopback address of the host only."""
    faults = []
    if set(published) != expected:
        faults.append(f"published {sorted(published)}, expected {sorted(expected)}")
    for port, addresses in published.items():
        if addresses != ["127.0.0.1"]:
            faults.append(f"{port} is published on {addresses}")
    return faults


def certificate_chain_faults(text: str, authority: str, names: list[str]) -> list[str]:
    """What is wrong with the certificate the entry presents (R126), from `openssl
    x509 -noout -issuer -ext subjectAltName`: its issuer is the engine's
    authority and every name of the public host is among its subject
    alternative names."""
    faults = []
    issuer = re.search(r"^issuer\s*=\s*(.+)$", text, re.MULTILINE)
    if not issuer or authority not in issuer.group(1):
        faults.append(f"issuer is {issuer.group(1) if issuer else None!r}")
    for name in names:
        if not re.search(rf"(DNS|IP Address):{re.escape(name)}(,|\s|$)", text):
            faults.append(f"{name} is not a name of the certificate")
    return faults


def entry_pin_faults(containerfile: str, components: list[dict]) -> list[str]:
    """What is wrong with the pins of the entry's container file against the
    register (GAP-057): the base image's digest, the library's version and the
    SHA-256 of its package file, the versions of the distribution's packages,
    the check of the package hash and the locked restore."""
    faults = []
    by_name = {c["name"]: c for c in components}
    base = re.search(
        r"^ARG BASE=\S+@(sha256:[0-9a-f]{64})", containerfile, re.MULTILINE
    )
    registered = by_name.get("fedora-minimal", {}).get("digest")
    if not base or base.group(1) != registered:
        faults.append("the base digest is not the registered one")
    yarp = by_name.get("yarp", {})
    sha = re.search(r"^ARG YARP_SHA256=([0-9a-f]{64})$", containerfile, re.MULTILINE)
    if not sha or sha.group(1) != yarp.get("package_sha256"):
        faults.append("the package hash of the library is not the registered one")
    version = re.search(r"^ARG YARP_VERSION=(\S+)$", containerfile, re.MULTILINE)
    if not version or version.group(1) != yarp.get("version"):
        faults.append("the library version is not the registered one")
    dotnet = by_name.get("dotnet", {})
    packages = dotnet.get("packages", [])
    for package in packages:
        if not re.search(
            rf"^ARG DOTNET_\w+={re.escape(package)}$", containerfile, re.MULTILINE
        ):
            faults.append(f"{package} is not pinned in the container file")
    if len(packages) != 2:
        faults.append("the register names no runtime package and SDK package")
    if "sha256sum --check" not in containerfile:
        faults.append("the build does not check the package hash")
    if "--locked-mode" not in containerfile:
        faults.append("the restore is not locked")
    return faults


# ---- One engine shared by the tests that do not disturb it ---------------------


def inner_start_times(listing: str) -> dict[str, str]:
    """The running containers of the engine's pod and when each started, from
    `podman ps --format '{{.Names}} {{.StartedAt}}'` run inside the engine. A line
    that is not a name and a time is left out."""
    found = {}
    for line in listing.splitlines():
        fields = line.split()
        if len(fields) == 2:
            found[fields[0]] = fields[1]
    return found


def shared_engine_faults(before: dict | None, after: dict | None) -> list[str]:
    """What a test did to the engine that the session shares (R181), from the
    snapshots taken before and after it: the outer container and its start, the
    start of every inner container that ran before, the readiness answer. `None`
    is a snapshot that could not be taken. A test that restarts, replaces or
    stops any part, or leaves the engine not ready, has disturbed it."""
    if before is None or after is None:
        return ["the state of the shared engine could not be read"]
    faults = []
    if before["health"] != "healthy":
        faults.append(f"the engine was already {before['health']} before the test")
    if after["container"] != before["container"]:
        faults.append("the engine container was replaced")
    elif after["started"] != before["started"]:
        faults.append("the engine container was started again")
    for name, started in sorted(before["inner"].items()):
        now = after["inner"].get(name)
        if now is None:
            faults.append(f"{name} no longer runs")
        elif now != started:
            faults.append(f"{name} was started again")
    if after["health"] != "healthy":
        faults.append(f"the engine answers {after['health']}, not healthy")
    if not after["ready"]:
        faults.append("the readiness target is not active")
    return faults


def on_hosted_runner(environment: dict[str, str]) -> bool:
    """True on the hosted runner that the merge gate runs in: GitHub sets
    `GITHUB_ACTIONS` to `true` there (documented by GitHub). Anywhere else the
    machine is not the one the limit was set for."""
    return environment.get("GITHUB_ACTIONS") == "true"


def session_duration_faults(
    elapsed: float, limits: dict, doc: str, enforced: bool = True
) -> list[str]:
    """What is wrong with the duration of the system tests (R180): the limit is held
    in the model as `maxSystemTestTime`, in seconds, positive; the text of the
    requirement states no number; and, where the limit is enforced (the hosted
    runner), the session did not take longer. Elsewhere the time is only reported."""
    name = "maxSystemTestTime"
    if name not in limits:
        return [f"the requirement has no attribute {name}"]
    faults = []
    value, unit = limits[name]
    if unit != "s":
        faults.append(f"{name} is in {unit}, not in seconds")
    if not isinstance(value, int | float) or value <= 0:
        faults.append(f"{name} is not a positive number")
    elif enforced and elapsed > value:
        faults.append(f"the system tests took {elapsed:.0f} s; the limit is {value} s")
    if re.search(r"\d", doc):
        faults.append("the text of the requirement states a number of its own")
    return faults
