# Extracted from manuscript/book1-traditional/10-security-fundamentals.md §10.7.3 (listing 5). Edit the manuscript, not this file.
"""Defense-in-depth check for user-supplied URLs fetched by a server (SSRF)."""
import ipaddress
import socket
from urllib.parse import urlsplit

ALLOWED_SCHEMES = {"https"}
ALLOWED_PORTS = {443}

def resolve_and_check(url: str) -> list[str]:
    parts = urlsplit(url)
    if parts.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"scheme {parts.scheme!r} not allowed")
    port = parts.port or 443
    if port not in ALLOWED_PORTS or not parts.hostname:
        raise ValueError("port or host not allowed")
    infos = socket.getaddrinfo(parts.hostname, port, proto=socket.IPPROTO_TCP)
    addrs = sorted({info[4][0] for info in infos})
    for a in addrs:
        ip = ipaddress.ip_address(a)
        if not ip.is_global:   # rejects private, loopback, link-local (169.254.169.254), etc.
            raise ValueError(f"{parts.hostname} resolves to non-public {ip}")
    # Caller must connect to one of THESE addresses (pin them) to avoid DNS rebinding.
    return addrs
