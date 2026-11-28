"""The HTTP entry point (ADR 0008): what it forwards, what it never forwards, what
it tells the backend, and that it is the only way in to the identity provider.

Two kinds of test. Some start the entry's own image alone, on the host's network,
in front of a stand-in backend that this process runs and that records what it
receives: those can read what the backend was sent (R128, R129, R132). The others
use the engine of the session and reach the entry the way a client does, through
its published port, over TLS, trusting the engine's own certificate authority (R126,
R135).
"""

import http.client
import json
import os
import socket
import ssl
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from conftest import CACHE
from engine_logic import (
    OTHER_FORWARDING_HEADERS,
    certificate_chain_faults,
    forwarding_faults,
    listener_faults,
    published_faults,
    routing_faults,
)

ENTRY_PORT = 8443
CERTIFICATE_DIRECTORY = "/run/anima/entrytls"
AUTHORITY = "Anima local root"

# The prefixes the engine declares, with a path that the identity provider would
# answer under each (the stand-in answers every path 200).
FORWARDED = [
    "/realms/anima/protocol/openid-connect/certs",
    "/resources/abc/common/keycloak/web_modules/x.js",
    "/.well-known/openid-configuration",
]
# Paths that begin with no declared prefix, and the identity provider's own
# administrative realm in every spelling the routing could mistake (AC 5).
REFUSED = [
    "/",
    "/admin/master/console/",
    "/realm/anima",
    "/realms",
    "/realms/",
    "/robots.txt",
    "/realms/master",
    "/realms/master/",
    "/realms/master/protocol/openid-connect/certs",
    "/realms/Master/protocol/openid-connect/certs",
    "/realms/%6daster/protocol/openid-connect/certs",
    "/realms/anima/../master/protocol/openid-connect/certs",
]
# The identity provider's health, metrics and management endpoints, in the places
# a route could reach them.
MANAGEMENT = [
    "/health",
    "/health/ready",
    "/health/live",
    "/metrics",
    "/management",
    "/q/health",
    "/realms/anima/health",
    "/resources/health/ready",
    "/.well-known/metrics",
    "/realms/anima/../../health",
    "/HEALTH/ready",
]


class Backend:
    """A stand-in backend on the loopback: it answers 200 with the path and the
    headers it received, and keeps them."""

    def __init__(self):
        outer = self
        self.requests: list[dict] = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                seen = {
                    "path": self.path,
                    "headers": [[k, v] for k, v in self.headers.items()],
                }
                outer.requests.append(seen)
                body = json.dumps(seen).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class Standalone:
    """The entry's image, run alone on the host's network, read-only, non-root and
    with no capability: the way the engine's unit runs it, with a plain listener
    instead of the TLS one, and the backend's address replaced."""

    def __init__(self, backend: Backend, env: dict[str, str] | None = None):
        ref = CACHE / "entry.ref"
        if not ref.exists():
            pytest.fail("no entry image: run `mise run engine:build entry`")
        self.port = free_port()
        self.name = f"anima-entry-test-{os.getpid()}-{self.port}"
        settings = {
            "Kestrel__Endpoints__Http__Url": f"http://127.0.0.1:{self.port}",
            "ReverseProxy__Clusters__identity-provider__Destinations__identity-provider__Address": f"http://127.0.0.1:{backend.port}/",
            **(env or {}),
        }
        command = [
            "podman",
            "run",
            "--detach",
            "--name",
            self.name,
            "--network",
            "host",
            "--read-only",
            "--cap-drop",
            "all",
            "--security-opt",
            "no-new-privileges",
            "--tmpfs",
            "/tmp:rw,mode=1777",
        ]
        for key, value in settings.items():
            command += ["--env", f"{key}={value}"]
        command.append(ref.read_text().strip())
        started = subprocess.run(command, capture_output=True, text=True, check=False)
        assert started.returncode == 0, started.stderr
        self.wait_listening()

    def wait_listening(self, limit: float = 30.0):
        deadline = time.monotonic() + limit
        while time.monotonic() < deadline:
            try:
                socket.create_connection(("127.0.0.1", self.port), timeout=1).close()
                return
            except OSError:
                time.sleep(0.2)
        logs = subprocess.run(
            ["podman", "logs", self.name], capture_output=True, text=True, check=False
        )
        raise AssertionError(f"the entry does not listen: {logs.stdout}{logs.stderr}")

    def get(self, path: str, headers: dict[str, str] | None = None):
        return plain_get(self.port, path, headers)

    def close(self):
        subprocess.run(
            ["podman", "rm", "--force", "--time", "5", self.name],
            capture_output=True,
            check=False,
        )


def plain_get(port: int, path: str, headers: dict[str, str] | None = None):
    """(status, body) of a GET with the path exactly as given."""
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    try:
        connection.putrequest("GET", path, skip_host=False)
        for key, value in (headers or {}).items():
            connection.putheader(key, value)
        connection.endheaders()
        response = connection.getresponse()
        return response.status, response.read().decode()
    finally:
        connection.close()


@pytest.fixture
def standalone():
    started: list[tuple[Standalone, Backend]] = []

    def make(env: dict[str, str] | None = None) -> tuple[Standalone, Backend]:
        backend = Backend()
        entry = Standalone(backend, env)
        started.append((entry, backend))
        return entry, backend

    yield make
    for entry, backend in started:
        entry.close()
        backend.close()


def answers_of(get, paths: list[str]) -> dict[str, int]:
    return {path: get(path)[0] for path in paths}


# ---- R128 ---------------------------------------------------------------------


def test_R128_entry_forwards_only_declared_prefixes(standalone, engine):
    """A request goes to the backend only when its path begins with a declared
    prefix, and to the declared backend; everything else is answered 404 by the
    entry. First against the entry alone and a recording backend, then through
    the engine's own entry to the real identity provider."""
    entry, backend = standalone()
    answers = answers_of(entry.get, FORWARDED + REFUSED)
    faults = routing_faults(answers, FORWARDED, REFUSED)
    assert not faults, faults
    # Only the forwarded ones reached the backend, each as asked, none other.
    assert sorted(r["path"] for r in backend.requests) == sorted(FORWARDED)

    # The same through the engine: the identity provider answers its own paths and
    # its administrative realm is refused by the entry, not by the provider (which
    # would answer 200 to its key set and its discovery document).
    tls = EngineEntry(engine)
    real_forwarded = [
        "/realms/anima/.well-known/openid-configuration",
        "/realms/anima/protocol/openid-connect/certs",
    ]
    real_refused = [
        "/",
        "/admin/master/console/",
        "/realms/master/",
        "/realms/master/protocol/openid-connect/certs",
        "/realms/master/.well-known/openid-configuration",
        "/realms/Master/protocol/openid-connect/certs",
    ]
    answers = answers_of(tls.get, real_forwarded + real_refused)
    faults = routing_faults(answers, real_forwarded, real_refused)
    assert not faults, faults


# ---- R129 ---------------------------------------------------------------------


def test_R129_entry_never_forwards_management(standalone, engine):
    """The health, metrics and management endpoints are answered 404 by the entry
    wherever a route could reach them, and also when the configuration declares a
    route to them."""
    entry, backend = standalone()
    answers = answers_of(entry.get, FORWARDED[:1] + MANAGEMENT)
    faults = routing_faults(answers, FORWARDED[:1], MANAGEMENT)
    assert not faults, faults
    assert [r["path"] for r in backend.requests] == FORWARDED[:1]

    # A configuration that declares such a route anyway: a catch-all, and routes
    # named after the endpoints.
    declared = {
        "ReverseProxy__Routes__everything__ClusterId": "identity-provider",
        "ReverseProxy__Routes__everything__Match__Path": "/{**rest}",
        "ReverseProxy__Routes__health__ClusterId": "identity-provider",
        "ReverseProxy__Routes__health__Match__Path": "/health/{**rest}",
        "ReverseProxy__Routes__metrics__ClusterId": "identity-provider",
        "ReverseProxy__Routes__metrics__Match__Path": "/metrics",
        "ReverseProxy__Routes__management__ClusterId": "identity-provider",
        "ReverseProxy__Routes__management__Match__Path": "/management/{**rest}",
    }
    entry, backend = standalone(declared)
    answers = answers_of(entry.get, ["/robots.txt"] + MANAGEMENT)
    faults = routing_faults(answers, ["/robots.txt"], MANAGEMENT)
    assert not faults, faults
    assert [r["path"] for r in backend.requests] == ["/robots.txt"]

    # And through the engine: nothing of the provider's management reaches a client.
    tls = EngineEntry(engine)
    faults = routing_faults(
        answers_of(
            tls.get, ["/realms/anima/.well-known/openid-configuration"] + MANAGEMENT
        ),
        ["/realms/anima/.well-known/openid-configuration"],
        MANAGEMENT,
    )
    assert not faults, faults


# ---- R132 ---------------------------------------------------------------------


def test_R132_entry_overwrites_forwarded_header(standalone):
    """A client that sends its own forwarding headers gets them replaced: the
    backend receives one `Forwarded` header, made by the entry from the
    connection, and none of the others."""
    entry, backend = standalone()
    forged = {
        "Forwarded": "for=6.6.6.6;host=forged.example;proto=https",
        **{name: "forged-6.6.6.6" for name in OTHER_FORWARDING_HEADERS},
    }
    status, _ = entry.get(FORWARDED[0], forged)
    assert status == 200
    received = [tuple(pair) for pair in backend.requests[-1]["headers"]]
    host = f"127.0.0.1:{entry.port}"
    faults = forwarding_faults(received, "127.0.0.1", host, "http")
    assert not faults, (faults, received)
    # A request that sends nothing of the kind gets the same header.
    status, _ = entry.get(FORWARDED[0])
    assert status == 200
    received = [tuple(pair) for pair in backend.requests[-1]["headers"]]
    assert not forwarding_faults(received, "127.0.0.1", host, "http"), received


# ---- R126, R135 -----------------------------------------------------------------


class EngineEntry:
    """The engine's entry as a client reaches it: the published port, over TLS, the
    certificate checked against the engine's own authority for the name `localhost`."""

    def __init__(self, engine):
        self.engine = engine
        self.port = int(engine.container.get_exposed_port(ENTRY_PORT))
        code, authority = engine.exec("cat", f"{CERTIFICATE_DIRECTORY}/ca.crt")
        assert code == 0 and "BEGIN CERTIFICATE" in authority, authority
        self.context = ssl.create_default_context(cadata=authority)
        self.authority = authority

    def connect(self) -> ssl.SSLSocket:
        raw = socket.create_connection(("127.0.0.1", self.port), timeout=30)
        return self.context.wrap_socket(raw, server_hostname="localhost")

    def get(self, path: str, headers: dict[str, str] | None = None):
        class Connection(http.client.HTTPSConnection):
            def connect(inner):
                inner.sock = self.connect()

        connection = Connection("localhost", self.port, timeout=30)
        try:
            connection.putrequest("GET", path)
            for key, value in (headers or {}).items():
                connection.putheader(key, value)
            connection.endheaders()
            response = connection.getresponse()
            return response.status, response.read().decode()
        finally:
            connection.close()


def test_R126_entry_terminates_tls_with_engine_certificate(engine):
    """The entry answers over TLS with a certificate that chains to the engine's
    certificate authority and names the public host (`localhost` and its
    loopback address)."""
    entry = EngineEntry(engine)
    with entry.connect() as secured:
        assert secured.version() in ("TLSv1.2", "TLSv1.3")
        der = secured.getpeercert(binary_form=True)
    pem = ssl.DER_cert_to_PEM_cert(der)
    shown = subprocess.run(
        ["openssl", "x509", "-noout", "-issuer", "-ext", "subjectAltName"],
        input=pem,
        capture_output=True,
        text=True,
        check=False,
    )
    assert shown.returncode == 0, shown.stderr
    faults = certificate_chain_faults(
        shown.stdout, AUTHORITY, ["localhost", "127.0.0.1"]
    )
    assert not faults, (faults, shown.stdout)
    # Not trusted by anything but the engine's authority: the system's roots refuse it.
    raw = socket.create_connection(("127.0.0.1", entry.port), timeout=30)
    with pytest.raises(ssl.SSLCertVerificationError):
        ssl.create_default_context().wrap_socket(raw, server_hostname="localhost")
    # The serving process holds that certificate and key files.
    code, out = engine.exec("ls", CERTIFICATE_DIRECTORY)
    assert code == 0 and "ca.crt" in out and "server.crt" in out, out


def test_R135_identity_provider_reachable_only_through_entry(engine):
    """From outside the pod only the entry's port and the database server's are
    published; the identity provider's ports are listened on the loopback of the
    pod only, and what the identity provider serves is reached through the entry."""
    out = subprocess.run(
        [
            "podman",
            "inspect",
            "--format",
            "{{json .NetworkSettings.Ports}}",
            engine.name,
        ],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    ports = json.loads(out)
    published = {
        port: [b["HostIp"] for b in bindings or []]
        for port, bindings in ports.items()
        if bindings
    }
    faults = published_faults(published, {"5432/tcp", f"{ENTRY_PORT}/tcp"})
    assert not faults, faults

    code, listening = engine.exec("ss", "-H", "-l", "-t", "-n")
    assert code == 0, listening
    faults = listener_faults(listening.splitlines(), [8080, 9000])
    assert not faults, (faults, listening)
    # The entry itself does listen on the address the outer publish reaches.
    assert any(
        line.split()[3].endswith(f":{ENTRY_PORT}")
        and not line.split()[3].startswith("127.")
        for line in listening.splitlines()
        if len(line.split()) >= 4
    ), listening

    # No address of the container but the loopback accepts a connection to the
    # identity provider's ports.
    code, addresses = engine.exec("hostname", "-I")
    assert code == 0 and addresses.strip(), addresses
    for address in addresses.split():
        for port in (8080, 9000):
            code, out = engine.exec("bash", "-c", f"exec 3<>/dev/tcp/{address}/{port}")
            assert code != 0, (address, port, out)
        code, out = engine.exec(
            "bash", "-c", f"exec 3<>/dev/tcp/{address}/{ENTRY_PORT}"
        )
        assert code == 0, (address, out)

    # And through the entry the identity provider answers.
    entry = EngineEntry(engine)
    status, text = entry.get("/realms/anima/.well-known/openid-configuration")
    assert status == 200 and '"issuer"' in text, (status, text[:200])
