"""
TLS/SSL checks — certificate validity, expiry, and protocol version.
Uses Python's built-in ssl module; no extra dependencies needed.
"""
import ssl
import socket
from datetime import datetime, timezone


DEPRECATED_PROTOCOLS = {"TLSv1", "TLSv1.1", "SSLv2", "SSLv3"}


def check_tls(hostname: str, port: int = 443) -> list[dict]:
    """
    Connect to hostname:port over TLS and inspect the certificate and negotiated protocol.
    Returns a list of check_result dicts.
    """
    results = []
    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as tls_sock:
                cert = tls_sock.getpeercert()
                protocol = tls_sock.version() or "unknown"
                cipher = tls_sock.cipher()

                # --- Certificate expiry ---
                expiry_str = cert.get("notAfter", "")
                expiry = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z").replace(
                    tzinfo=timezone.utc
                )
                days_remaining = (expiry - datetime.now(timezone.utc)).days

                if days_remaining <= 0:
                    results.append({
                        "category": "tls", "check_key": "cert_expiry",
                        "status": "fail", "severity": "critical", "score_impact": -20,
                        "observed_value": f"Expired {abs(days_remaining)} day(s) ago",
                        "remediation": "Renew your TLS certificate immediately.",
                        "detail": {"days_remaining": days_remaining, "expiry": expiry_str},
                    })
                elif days_remaining <= 30:
                    results.append({
                        "category": "tls", "check_key": "cert_expiry",
                        "status": "warn", "severity": "high", "score_impact": -10,
                        "observed_value": f"Expires in {days_remaining} day(s)",
                        "remediation": "Renew your TLS certificate soon.",
                        "detail": {"days_remaining": days_remaining, "expiry": expiry_str},
                    })
                else:
                    results.append({
                        "category": "tls", "check_key": "cert_expiry",
                        "status": "pass", "severity": "info", "score_impact": 0,
                        "observed_value": f"Valid for {days_remaining} more day(s)",
                        "detail": {"days_remaining": days_remaining, "expiry": expiry_str},
                    })

                # --- Protocol version ---
                is_deprecated = protocol in DEPRECATED_PROTOCOLS
                results.append({
                    "category": "tls", "check_key": "tls_protocol",
                    "status": "fail" if is_deprecated else "pass",
                    "severity": "high" if is_deprecated else "info",
                    "score_impact": -15 if is_deprecated else 0,
                    "observed_value": protocol,
                    "remediation": "Disable TLS 1.0 and 1.1; require TLS 1.2+ only." if is_deprecated else "",
                    "detail": {"protocol": protocol, "cipher": cipher},
                })

    except ssl.SSLCertVerificationError as e:
        results.append({
            "category": "tls", "check_key": "cert_valid",
            "status": "fail", "severity": "critical", "score_impact": -25,
            "observed_value": str(e),
            "remediation": "Fix the certificate chain or replace with a trusted certificate.",
            "detail": {},
        })
    except Exception as e:
        results.append({
            "category": "tls", "check_key": "tls_connection",
            "status": "fail", "severity": "critical", "score_impact": -25,
            "observed_value": str(e),
            "remediation": "Ensure the host is reachable and TLS is configured on port 443.",
            "detail": {},
        })

    return results
