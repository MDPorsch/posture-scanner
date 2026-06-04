"""
HTTP security header checks.
Pure function — takes a dict of response headers, returns check_result dicts.
No network calls. Fully testable offline.
"""

HEADER_CHECKS = [
    {
        "key": "hsts",
        "header": "strict-transport-security",
        "description": "HTTP Strict Transport Security (HSTS)",
        "min_max_age": 15_552_000,  # 6 months in seconds
        "remediation": "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains",
    },
    {
        "key": "csp",
        "header": "content-security-policy",
        "description": "Content Security Policy (CSP)",
        "remediation": "Add a Content-Security-Policy header to restrict resource loading.",
    },
    {
        "key": "x_frame_options",
        "header": "x-frame-options",
        "description": "X-Frame-Options (clickjacking protection)",
        "valid_values": ["DENY", "SAMEORIGIN"],
        "remediation": "Add: X-Frame-Options: DENY",
    },
    {
        "key": "x_content_type",
        "header": "x-content-type-options",
        "description": "X-Content-Type-Options",
        "expected": "nosniff",
        "remediation": "Add: X-Content-Type-Options: nosniff",
    },
    {
        "key": "referrer_policy",
        "header": "referrer-policy",
        "description": "Referrer-Policy",
        "valid_values": [
            "no-referrer",
            "strict-origin",
            "strict-origin-when-cross-origin",
            "same-origin",
            "no-referrer-when-downgrade",
        ],
        "remediation": "Add: Referrer-Policy: strict-origin-when-cross-origin",
    },
    {
        "key": "permissions_policy",
        "header": "permissions-policy",
        "description": "Permissions-Policy",
        "remediation": "Add a Permissions-Policy header to limit browser feature access.",
    },
]


def check_headers(response_headers: dict) -> list[dict]:
    """
    Analyse HTTP response headers for security best practices.
    Args:
        response_headers: dict of header name → value (case-insensitive lookup handled internally).
    Returns:
        List of check_result dicts.
    """
    headers_lower = {k.lower(): v for k, v in response_headers.items()}
    results = []

    for defn in HEADER_CHECKS:
        observed = headers_lower.get(defn["header"])
        base = {
            "category": "headers",
            "check_key": defn["key"],
            "observed_value": observed or "MISSING",
            "remediation": defn.get("remediation", ""),
            "detail": {},
        }

        if observed is None:
            results.append({**base, "status": "fail", "severity": "high", "score_impact": -10})
            continue

        if defn["key"] == "hsts":
            max_age = _parse_max_age(observed)
            if max_age and max_age >= defn["min_max_age"]:
                results.append({**base, "status": "pass", "severity": "info", "score_impact": 0,
                                 "detail": {"max_age": max_age}})
            else:
                results.append({**base, "status": "warn", "severity": "medium", "score_impact": -5,
                                 "detail": {"max_age": max_age},
                                 "remediation": f"Increase max-age to at least {defn['min_max_age']}."})

        elif "valid_values" in defn:
            if any(v.upper() in observed.upper() for v in defn["valid_values"]):
                results.append({**base, "status": "pass", "severity": "info", "score_impact": 0})
            else:
                results.append({**base, "status": "warn", "severity": "medium", "score_impact": -5})

        elif "expected" in defn:
            if observed.strip().lower() == defn["expected"].lower():
                results.append({**base, "status": "pass", "severity": "info", "score_impact": 0})
            else:
                results.append({**base, "status": "fail", "severity": "high", "score_impact": -10,
                                 "expected_value": defn["expected"]})
        else:
            # Header present — pass (CSP, Permissions-Policy: presence alone scores)
            results.append({**base, "status": "pass", "severity": "info", "score_impact": 0})

    return results


def _parse_max_age(hsts_value: str) -> int | None:
    for part in hsts_value.split(";"):
        part = part.strip()
        if part.lower().startswith("max-age="):
            try:
                return int(part.split("=", 1)[1].strip())
            except ValueError:
                pass
    return None
