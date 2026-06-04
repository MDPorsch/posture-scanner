"""
Open redirect probe.
Sends a single benign request per common redirect parameter and checks
whether the server redirects to an off-domain URL.
This is a passive/read-only check — no exploitation.
"""
import httpx

REDIRECT_PARAMS = ["next", "url", "redirect", "return", "goto", "redirect_uri", "redir"]
# A public domain clearly outside the target; we check if the server bounces to it
TEST_PAYLOAD = "https://example-redirect-check.com"


def check_redirects(base_url: str) -> list[dict]:
    """
    Probe common redirect parameters on base_url for open redirect behaviour.
    Returns a list with a single check_result dict.
    """
    found_redirects = []

    for param in REDIRECT_PARAMS:
        probe_url = f"{base_url}?{param}={TEST_PAYLOAD}"
        try:
            resp = httpx.get(probe_url, follow_redirects=False, timeout=8)
            if resp.status_code in (301, 302, 303, 307, 308):
                location = resp.headers.get("location", "")
                if TEST_PAYLOAD in location:
                    found_redirects.append({"param": param, "location": location})
        except Exception:
            pass  # Network/timeout errors are not an open-redirect signal

    if found_redirects:
        return [{
            "category": "redirects", "check_key": "open_redirect",
            "status": "fail", "severity": "high", "score_impact": -15,
            "observed_value": f"Vulnerable params: {[r['param'] for r in found_redirects]}",
            "remediation": "Validate and whitelist redirect destinations server-side.",
            "detail": {"vulnerable_params": found_redirects},
        }]
    else:
        return [{
            "category": "redirects", "check_key": "open_redirect",
            "status": "pass", "severity": "info", "score_impact": 0,
            "observed_value": f"No open redirects detected on: {REDIRECT_PARAMS}",
            "remediation": "",
            "detail": {"params_tested": REDIRECT_PARAMS},
        }]
