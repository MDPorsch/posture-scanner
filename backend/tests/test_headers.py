"""
Tests for the HTTP security header checker.
Pure function — no network calls needed.
"""
from engine.headers import check_headers


GOOD_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy":   "default-src 'self'",
    "X-Frame-Options":           "DENY",
    "X-Content-Type-Options":    "nosniff",
    "Referrer-Policy":           "strict-origin-when-cross-origin",
    "Permissions-Policy":        "geolocation=()",
}


def results_by_key(headers):
    return {r["check_key"]: r for r in check_headers(headers)}


def test_all_good_headers_pass():
    results = results_by_key(GOOD_HEADERS)
    assert results["hsts"]["status"]           == "pass"
    assert results["csp"]["status"]            == "pass"
    assert results["x_frame_options"]["status"]== "pass"
    assert results["x_content_type"]["status"] == "pass"
    assert results["referrer_policy"]["status"]== "pass"
    assert results["permissions_policy"]["status"] == "pass"


def test_missing_all_headers_fail():
    results = results_by_key({})
    for r in results.values():
        assert r["status"] == "fail"
        assert r["score_impact"] < 0


def test_hsts_low_max_age_warns():
    results = results_by_key({"Strict-Transport-Security": "max-age=60"})
    assert results["hsts"]["status"] == "warn"


def test_hsts_sufficient_max_age_passes():
    results = results_by_key({"Strict-Transport-Security": "max-age=31536000"})
    assert results["hsts"]["status"] == "pass"


def test_x_content_type_wrong_value_fails():
    results = results_by_key({"X-Content-Type-Options": "something-else"})
    assert results["x_content_type"]["status"] == "fail"


def test_x_frame_sameorigin_passes():
    results = results_by_key({"X-Frame-Options": "SAMEORIGIN"})
    assert results["x_frame_options"]["status"] == "pass"


def test_header_check_is_case_insensitive():
    # Header names in lowercase should still be detected
    results = results_by_key({"x-frame-options": "DENY", "x-content-type-options": "nosniff"})
    assert results["x_frame_options"]["status"] == "pass"
    assert results["x_content_type"]["status"]  == "pass"
