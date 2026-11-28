"""Companions of the entry's tests that show their decisions failing (R56): no
container is started; each feeds the pure decision a deliberately wrong input."""

from engine_logic import (
    OTHER_FORWARDING_HEADERS,
    certificate_chain_faults,
    entry_pin_faults,
    forwarding_faults,
    listener_faults,
    published_faults,
    routing_faults,
)

FORWARDED = ["/realms/anima/x", "/resources/y"]
REFUSED = ["/", "/realms/master/x"]


def test_R128_entry_forwards_only_declared_prefixes_detects_violation():
    """A forwarded path answered 404, a refused path answered 200 (or anything but
    404), a path not answered at all, and a check that asked nothing are faults."""
    good = {
        "/realms/anima/x": 200,
        "/resources/y": 200,
        "/": 404,
        "/realms/master/x": 404,
    }
    assert routing_faults(good, FORWARDED, REFUSED) == []
    assert routing_faults({**good, "/resources/y": 404}, FORWARDED, REFUSED)
    assert routing_faults({**good, "/realms/master/x": 200}, FORWARDED, REFUSED)
    assert routing_faults({**good, "/": 503}, FORWARDED, REFUSED)
    assert routing_faults({**good, "/": 502}, FORWARDED, REFUSED)
    assert routing_faults(
        {"/realms/anima/x": 200, "/resources/y": 200}, FORWARDED, REFUSED
    )
    assert routing_faults(good, [], REFUSED)
    assert routing_faults(good, FORWARDED, [])


def test_R129_entry_never_forwards_management_detects_violation():
    """A management path that was forwarded is a fault, whatever it was answered."""
    refused = ["/health", "/metrics"]
    assert (
        routing_faults({"/ok": 200, "/health": 404, "/metrics": 404}, ["/ok"], refused)
        == []
    )
    assert routing_faults(
        {"/ok": 200, "/health": 200, "/metrics": 404}, ["/ok"], refused
    )
    assert routing_faults({"/ok": 200, "/health": 404}, ["/ok"], refused)


def received(*extra: tuple[str, str]) -> list[tuple[str, str]]:
    return [
        ("Host", "127.0.0.1:8080"),
        ("Forwarded", 'for=10.0.0.9;host="entry.example:8443";proto=https'),
        *extra,
    ]


def test_R132_entry_overwrites_forwarded_header_detects_violation():
    """A forged value passed on, a second or a missing `Forwarded`, a wrong address,
    host or scheme, and every other forwarding header are faults."""
    args = ("10.0.0.9", "entry.example:8443", "https")
    assert forwarding_faults(received(), *args) == []
    assert forwarding_faults([("Forwarded", "for=6.6.6.6;host=x;proto=https")], *args)
    assert forwarding_faults(received(("Forwarded", "for=6.6.6.6")), *args)
    assert forwarding_faults([("Host", "x")], *args)
    assert forwarding_faults(received(), "10.0.0.8", "entry.example:8443", "https")
    assert forwarding_faults(received(), "10.0.0.9", "other.example", "https")
    assert forwarding_faults(received(), "10.0.0.9", "entry.example:8443", "http")
    for name in OTHER_FORWARDING_HEADERS:
        assert forwarding_faults(received((name.lower(), "1.1.1.1")), *args), name
    # An address in brackets (IPv6) is the address.
    v6 = [("Forwarded", 'for="[2001:db8::1]";host=h;proto=https')]
    assert forwarding_faults(v6, "2001:db8::1", "h", "https") == []


def test_R135_identity_provider_reachable_only_through_entry_detects_violation():
    """A port of the identity provider listened on a wider address, or not at all,
    a port published that is not declared, and one published on every address are
    faults."""
    listening = [
        "LISTEN 0 4096 127.0.0.1:8080 0.0.0.0:*",
        "LISTEN 0 4096 127.0.0.1:9000 0.0.0.0:*",
        "LISTEN 0 4096 0.0.0.0:8443 0.0.0.0:*",
    ]
    assert listener_faults(listening, [8080, 9000]) == []
    assert listener_faults(
        ["LISTEN 0 4096 0.0.0.0:8080 0.0.0.0:*", listening[1]], [8080, 9000]
    )
    assert listener_faults(["LISTEN 0 4096 *:9000 *:*", listening[0]], [8080, 9000])
    assert listener_faults(
        ["LISTEN 0 4096 [::]:8080 [::]:*", listening[1]], [8080, 9000]
    )
    assert listener_faults([listening[0]], [8080, 9000])
    assert listener_faults([], [8080])
    assert listener_faults(["LISTEN 0 4096 [::1]:8080 [::]:*"], [8080]) == []
    assert listener_faults(["LISTEN 0 4096 [::ffff:127.0.0.1]:8080 *:*"], [8080]) == []
    assert listener_faults(["LISTEN 0 4096 [::ffff:10.0.0.2]:8080 *:*"], [8080])
    declared = {"5432/tcp", "8443/tcp"}
    published = {"5432/tcp": ["127.0.0.1"], "8443/tcp": ["127.0.0.1"]}
    assert published_faults(published, declared) == []
    assert published_faults({**published, "8080/tcp": ["127.0.0.1"]}, declared)
    assert published_faults({"5432/tcp": ["127.0.0.1"]}, declared)
    assert published_faults({**published, "8443/tcp": ["0.0.0.0"]}, declared)
    assert published_faults({**published, "8443/tcp": ["127.0.0.1", "::1"]}, declared)


def test_R126_entry_terminates_tls_with_engine_certificate_detects_violation():
    """A certificate of another issuer, or without a name of the public host, is a
    fault; a name matches whole, not as the start of another name."""
    shown = (
        "issuer=CN = Anima local root\n"
        "X509v3 Subject Alternative Name:\n"
        "    DNS:localhost, IP Address:127.0.0.1\n"
    )
    names = ["localhost", "127.0.0.1"]
    assert certificate_chain_faults(shown, "Anima local root", names) == []
    assert certificate_chain_faults(shown, "Another root", names)
    assert certificate_chain_faults(shown, "Anima local root", [*names, "idp.example"])
    assert certificate_chain_faults(
        "issuer=CN = Anima local root\n", "Anima local root", names
    )
    assert certificate_chain_faults(
        shown.replace("DNS:localhost,", "DNS:localhost.example,"),
        "Anima local root",
        ["localhost"],
    )


CONTAINERFILE = """\
ARG BASE=base-image:45@sha256:{base}
ARG DOTNET_SDK=dotnet-sdk-10.0-10.0.115
ARG YARP_VERSION=2.3.0
ARG YARP_SHA256={package}
RUN echo "${{YARP_SHA256}}  f" | sha256sum --check -
RUN dotnet restore --locked-mode
ARG DOTNET_RUNTIME=aspnetcore-runtime-10.0-10.0.15
"""
COMPONENTS = [
    {"name": "fedora-minimal", "digest": "sha256:" + "a" * 64},
    {
        "name": "yarp",
        "version": "2.3.0",
        "package_sha256": "b" * 64,
    },
    {
        "name": "dotnet",
        "version": "10.0.15",
        "packages": ["aspnetcore-runtime-10.0-10.0.15", "dotnet-sdk-10.0-10.0.115"],
    },
]


def test_entry_build_pins_match_components_detects_violation():
    """A base, a package hash, a version or a package that differs from the
    register, a build that does not check the hash, and an unlocked restore are
    faults."""
    good = CONTAINERFILE.format(base="a" * 64, package="b" * 64)
    assert entry_pin_faults(good, COMPONENTS) == []
    assert entry_pin_faults(
        CONTAINERFILE.format(base="c" * 64, package="b" * 64), COMPONENTS
    )
    assert entry_pin_faults(
        CONTAINERFILE.format(base="a" * 64, package="c" * 64), COMPONENTS
    )
    assert entry_pin_faults(good.replace("2.3.0", "2.4.0"), COMPONENTS)
    assert entry_pin_faults(good.replace("10.0.15", "10.0.16"), COMPONENTS)
    assert entry_pin_faults(good.replace("sha256sum --check", "echo"), COMPONENTS)
    assert entry_pin_faults(good.replace("--locked-mode", ""), COMPONENTS)
    assert entry_pin_faults(good, [c for c in COMPONENTS if c["name"] != "dotnet"])
