"""
Tests for the cookie flag checker.
Pure function — no network calls needed.
"""
from engine.cookies import check_cookies


def test_good_cookie_passes():
    headers = ["session=abc123; Secure; HttpOnly; SameSite=Strict; Path=/"]
    results = check_cookies(headers)
    assert results[0]["status"] == "pass"
    assert results[0]["score_impact"] == 0


def test_missing_secure_fails():
    headers = ["session=abc123; HttpOnly; SameSite=Strict"]
    results = check_cookies(headers)
    assert results[0]["status"] == "fail"
    assert results[0]["score_impact"] < 0


def test_missing_httponly_fails():
    headers = ["session=abc123; Secure; SameSite=Lax"]
    results = check_cookies(headers)
    assert results[0]["status"] == "fail"


def test_missing_samesite_warns():
    headers = ["session=abc123; Secure; HttpOnly"]
    results = check_cookies(headers)
    assert results[0]["status"] == "warn"


def test_no_cookies_returns_empty():
    assert check_cookies([]) == []


def test_multiple_cookies_checked_individually():
    headers = [
        "good=1; Secure; HttpOnly; SameSite=Strict",
        "bad=2; HttpOnly",
    ]
    results = check_cookies(headers)
    assert len(results) == 2
    statuses = {r["detail"]["cookie"]: r["status"] for r in results}
    assert statuses["good"] == "pass"
    assert statuses["bad"] == "fail"
