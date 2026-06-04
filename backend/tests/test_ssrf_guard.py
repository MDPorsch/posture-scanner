"""
Tests for the SSRF guard — the most security-critical module in the engine.
All tests use monkeypatching so no real DNS lookups are made.
"""
import pytest
from engine.ssrf_guard import validate_hostname, validate_url


def _mock_dns(ip):
    """Helper: monkeypatch socket.gethostbyname to return a fixed IP."""
    import socket
    return lambda h: ip


def test_rejects_private_rfc1918_10(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "gethostbyname", _mock_dns("10.0.0.1"))
    with pytest.raises(ValueError, match="blocked"):
        validate_hostname("internal.example.com")


def test_rejects_private_rfc1918_192(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "gethostbyname", _mock_dns("192.168.1.100"))
    with pytest.raises(ValueError, match="blocked"):
        validate_hostname("home-router.local")


def test_rejects_loopback(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "gethostbyname", _mock_dns("127.0.0.1"))
    with pytest.raises(ValueError, match="blocked"):
        validate_hostname("localhost")


def test_rejects_cloud_metadata_ip(monkeypatch):
    """169.254.169.254 is the AWS/GCP/Azure instance metadata endpoint."""
    import socket
    monkeypatch.setattr(socket, "gethostbyname", _mock_dns("169.254.169.254"))
    with pytest.raises(ValueError, match="blocked"):
        validate_hostname("metadata.google.internal")


def test_rejects_bad_scheme():
    with pytest.raises(ValueError, match="Scheme"):
        validate_url("ftp://example.com")


def test_rejects_file_scheme():
    with pytest.raises(ValueError, match="Scheme"):
        validate_url("file:///etc/passwd")


def test_accepts_public_ip(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "gethostbyname", _mock_dns("93.184.216.34"))
    result = validate_hostname("example.com")
    assert result == "93.184.216.34"


def test_accepts_https_url(monkeypatch):
    import socket
    monkeypatch.setattr(socket, "gethostbyname", _mock_dns("93.184.216.34"))
    result = validate_url("https://example.com/path?q=1")
    assert result == "93.184.216.34"


def test_dns_failure_raises(monkeypatch):
    import socket
    def fail(h):
        raise socket.gaierror("Name or service not known")
    monkeypatch.setattr(socket, "gethostbyname", fail)
    with pytest.raises(ValueError, match="DNS resolution failed"):
        validate_hostname("does-not-exist-xyz.example")
