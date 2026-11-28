"""The entry's certificate: renewed before it expires, and taken without a restart
(R127, entryCertificateRenewedBeforeExpiry).

The first test of the task (written before the implementation) asked whether the
key and the certificate could be replaced as two files one after the other without
the entry ever being shown a mismatched pair. Answer, observed on 2026-11-28 with
the first build (key and certificate as two files read by Kestrel): the entry
watches the certificate file and not the key file. Replacing the key first and the
certificate second was taken (the new pair was presented); replacing the
certificate first and the key second was refused by the entry (`crit ... Unable to
reload configuration ... The provided key does not match the public key`), which
kept presenting the old pair, and the later replacement of the key was not taken at
all: the renewal was missed without an error. Hence the key and the certificate
are one file, replaced by one rename (`engine/entry/entry-certificate`), and the
tests below watch every connection during a renewal. The observation is kept as a
companion of the decision (`test_logic_entry.py`, `pickup_faults`), not as a slow
test.

The engine of the renewal tests is started with a short lifetime of the
certificate, by a drop-in of the unit on that engine only, never in the shipped
unit.
"""

import hashlib
import socket
import ssl
import subprocess
import time

import pytest
from conftest import ROOT, model_thresholds, start_engine
from engine_logic import (
    certificate_facts,
    pickup_faults,
    renewal_failure_faults,
    renewal_faults,
)
from test_entry import CERTIFICATE_DIRECTORY, ENTRY_PORT
from test_services import health_report, unit_environment

ENTRY_UNIT = ROOT / "engine/entry/entry-certificate.service"
RENEWAL_LIFETIME = 180
FAILURE_LIFETIME = 240


def short_lived(tmp_path, seconds: int) -> dict[str, str]:
    """A drop-in of the entry's certificate unit that sets the lifetime, as a bind mount."""
    dropin = tmp_path / "entry-certificate-lifetime.conf"
    dropin.write_text(
        f"[Service]\nEnvironment=ANIMA_ENTRY_TLS_LIFETIME_SECONDS={seconds}\n"
    )
    return {str(dropin): "/etc/systemd/system/entry-certificate.service.d/50-test.conf"}


def authority_of(engine) -> str:
    code, authority = engine.exec("cat", f"{CERTIFICATE_DIRECTORY}/ca.crt")
    assert code == 0 and "BEGIN CERTIFICATE" in authority, authority
    return authority


def presented(engine, authority: str) -> bytes | str:
    """The certificate (DER) a connection to the entry's published port is given,
    after a complete TLS handshake that checks it against the engine's authority;
    `FAILED ...` when the connection does not complete."""
    port = int(engine.container.get_exposed_port(ENTRY_PORT))
    context = ssl.create_default_context(cadata=authority)
    try:
        with (
            socket.create_connection(("127.0.0.1", port), timeout=10) as raw,
            context.wrap_socket(raw, server_hostname="localhost") as secured,
        ):
            return secured.getpeercert(binary_form=True)
    except OSError as error:
        return f"FAILED {type(error).__name__}: {error}"


def facts_of(der: bytes) -> dict:
    shown = subprocess.run(
        ["openssl", "x509", "-inform", "DER", "-noout", "-serial", "-enddate"],
        input=der,
        capture_output=True,
        check=False,
    )
    facts = certificate_facts(shown.stdout.decode())
    assert shown.returncode == 0 and facts, shown.stderr
    return facts


def fingerprint(shown: bytes | str) -> str:
    return shown if isinstance(shown, str) else hashlib.sha256(shown).hexdigest()


class Renewal:
    """What a renewal looked like from outside."""

    def __init__(self):
        self.observed: list[str] = []
        self.first: dict = {}
        self.last: dict = {}
        self.entry_before = self.entry_after = ""
        self.log = ""
        self.ready_after = False
        self.now = 0.0


@pytest.fixture(scope="module")
def renewal(podman_service, tmp_path_factory):
    """One engine whose entry certificate lives RENEWAL_LIFETIME seconds, watched
    through its first renewal: every connection made during it is recorded."""
    engine = start_engine(
        "entry-renewal",
        binds=short_lived(tmp_path_factory.mktemp("d"), RENEWAL_LIFETIME),
    )
    try:
        engine.wait_ready()
        authority = authority_of(engine)
        result = Renewal()
        first = presented(engine, authority)
        assert isinstance(first, bytes), first
        result.first = facts_of(first)
        result.entry_before = engine.inner_container_started_at("entry")
        first_print = fingerprint(first)
        log_before = engine.exec("podman", "logs", "entry")[1]
        deadline = time.monotonic() + RENEWAL_LIFETIME
        settled = None
        last = first
        while time.monotonic() < deadline:
            shown = presented(engine, authority)
            result.observed.append(fingerprint(shown))
            if isinstance(shown, bytes):
                last = shown
            if settled is None and fingerprint(shown) != first_print:
                settled = time.monotonic() + 5
            if settled and time.monotonic() > settled:
                break
            time.sleep(0.2)
        result.last = facts_of(last)
        result.now = float(engine.exec("date", "+%s")[1])
        result.entry_after = engine.inner_container_started_at("entry")
        result.log = engine.exec("podman", "logs", "entry")[1][len(log_before) :]
        result.ready_after = engine.active("anima-ready.target")
        yield result
    finally:
        engine.remove()


def test_R127_entry_takes_renewed_certificate_without_restart(renewal):
    """Every connection during a renewal completes (a key that did not belong to
    its certificate would fail the handshake), the certificate presented changes,
    and the entry is not restarted and reports no failure to load."""
    faults = pickup_faults(
        renewal.observed,
        renewal.entry_before,
        renewal.entry_after,
        renewal.log,
    )
    assert not faults, (faults, renewal.observed[-5:], renewal.log[-1500:])
    assert len(renewal.observed) > 20, "the watch was too short to prove anything"
    assert renewal.ready_after


def test_entry_certificate_renewed_before_expiry(renewal):
    """With a short lifetime, the certificate that the entry presents is replaced
    by another before the first expires, and the entry is not restarted; the
    shipped unit carries the thresholds of the model and nothing else does."""
    faults = renewal_faults(
        renewal.first,
        renewal.last,
        renewal.now,
        renewal.entry_before,
        renewal.entry_after,
    )
    assert not faults, faults
    limits, _ = model_thresholds("entryCertificateRenewedBeforeExpiry")
    assert limits["certificateLifetime"][1] == "s"
    unit = unit_environment(ENTRY_UNIT)
    assert unit["ANIMA_ENTRY_TLS_LIFETIME_SECONDS"] == str(
        limits["certificateLifetime"][0]
    )
    assert unit["ANIMA_ENTRY_TLS_RENEW_AFTER_PERCENT"] == str(
        limits["renewAfterPercent"][0]
    )
    # The same lifetime and share as the database server's certificate (R118).
    same, _ = model_thresholds("certificateRenewedBeforeExpiry")
    assert limits["certificateLifetime"] == same["certificateLifetime"]
    assert limits["renewAfterPercent"] == same["renewAfterPercent"]


def test_entry_certificate_renewed_before_expiry_failure_leaves_engine_not_ready(
    own_engine, tmp_path
):
    """The secret store refuses the entry's machine login once the engine is ready:
    when the renewal falls due it fails, the engine stops answering ready, its
    answer says that the certificate could not be renewed, and the entry keeps
    presenting the certificate in place."""
    engine = own_engine("r184", short_lived(tmp_path, FAILURE_LIFETIME))
    engine.wait_ready()
    authority = authority_of(engine)
    secret_id = engine.exec("cat", "/run/anima/configurator/secret_store_secret_id")[1]
    code, token = engine.inner(
        "secrets",
        "bao",
        "write",
        "-field=token",
        "auth/configurator/login",
        "role_id=configurator",
        f"secret_id={secret_id.strip()}",
    )
    assert code == 0, token
    code, out = engine.exec(
        "podman",
        "exec",
        "--env",
        f"BAO_TOKEN={token.strip()}",
        "secrets",
        "bao",
        "delete",
        "auth/approle/role/entry",
    )
    assert code == 0, out

    def reported() -> bool:
        status, output = health_report(engine)
        return status != "healthy" and "certificate renewal failed" in output

    try:
        engine.wait_for("the failure is reported", reported, FAILURE_LIFETIME + 60, 3)
    finally:
        status, output = health_report(engine)
    faults = renewal_failure_faults(status, output)
    assert not faults, (faults, output)
    assert not engine.active("anima-ready.target")
    # The certificate in place is still the one the entry serves.
    assert isinstance(presented(engine, authority), bytes)
