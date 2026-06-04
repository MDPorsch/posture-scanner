"""
Cookie security flag checks.
Pure function — takes a list of raw Set-Cookie header strings.
No network calls. Fully testable offline.
"""


def check_cookies(set_cookie_headers: list[str]) -> list[dict]:
    """
    Inspect each Set-Cookie header for Secure, HttpOnly, and SameSite flags.
    Args:
        set_cookie_headers: list of raw Set-Cookie header values.
    Returns:
        List of check_result dicts (one per cookie).
    """
    if not set_cookie_headers:
        return []

    results = []
    for raw in set_cookie_headers:
        parts = [p.strip() for p in raw.split(";")]
        cookie_name = parts[0].split("=", 1)[0].strip() if parts else "unknown"

        flags: dict = {}
        for part in parts[1:]:
            if "=" in part:
                k, v = part.split("=", 1)
                flags[k.strip().lower()] = v.strip()
            else:
                flags[part.strip().lower()] = True

        has_secure   = "secure" in flags
        has_httponly = "httponly" in flags
        samesite_val = flags.get("samesite", None)
        samesite_ok  = isinstance(samesite_val, str) and samesite_val.lower() in ("strict", "lax")

        detail = {
            "cookie": cookie_name,
            "secure": has_secure,
            "httponly": has_httponly,
            "samesite": samesite_val,
        }

        if has_secure and has_httponly and samesite_ok:
            results.append({
                "category": "cookies", "check_key": f"cookie_{cookie_name}",
                "status": "pass", "severity": "info", "score_impact": 0,
                "observed_value": raw[:120], "detail": detail,
                "remediation": "",
            })
        elif not has_secure or not has_httponly:
            missing = [f for f, ok in [("Secure", has_secure), ("HttpOnly", has_httponly)] if not ok]
            results.append({
                "category": "cookies", "check_key": f"cookie_{cookie_name}",
                "status": "fail", "severity": "high", "score_impact": -10,
                "observed_value": raw[:120], "detail": detail,
                "remediation": f"Add missing flags to cookie '{cookie_name}': {', '.join(missing)}.",
            })
        else:
            results.append({
                "category": "cookies", "check_key": f"cookie_{cookie_name}",
                "status": "warn", "severity": "medium", "score_impact": -5,
                "observed_value": raw[:120], "detail": detail,
                "remediation": f"Set SameSite=Strict or SameSite=Lax on cookie '{cookie_name}'.",
            })

    return results
