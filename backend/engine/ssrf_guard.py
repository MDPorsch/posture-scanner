"""
SSRF Guard — validates that a user-supplied hostname/URL resolves
to a public IP address and cannot be used to reach internal infrastructure.
"""
import ipaddress
import socket
from urllib.parse import urlparse

# IP ranges that must never be scanned
BLOCKED_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local + cloud metadata (169.254.169.254)
    ipaddress.ip_network("100.64.0.0/10"),   # shared address space
    ipaddress.ip_network("::1/128"),          # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),        # IPv6 link-local
]

ALLOWED_SCHEMES = {"http", "https"}


def validate_url(url: str) -> str:
    """
    Validate a full URL and confirm it does not point to internal resources.
    Returns the resolved IP address string on success.
    Raises ValueError on any violation.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Scheme '{parsed.scheme}' is not allowed. Use http or https.")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("No hostname found in URL.")

    return _guard_hostname(hostname)


def validate_hostname(hostname: str) -> str:
    """
    Resolve a bare hostname and confirm it is safe to scan.
    Returns the resolved IP address string on success.
    Raises ValueError on any violation.
    """
    return _guard_hostname(hostname)


def _guard_hostname(hostname: str) -> str:
    try:
        ip_str = socket.gethostbyname(hostname)
    except socket.gaierror as e:
        raise ValueError(f"DNS resolution failed for '{hostname}': {e}") from e

    ip_obj = ipaddress.ip_address(ip_str)

    for blocked in BLOCKED_RANGES:
        if ip_obj in blocked:
            raise ValueError(
                f"Hostname '{hostname}' resolves to {ip_str}, "
                f"which is in a blocked private/reserved range."
            )

    return ip_str
