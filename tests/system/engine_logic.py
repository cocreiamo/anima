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
