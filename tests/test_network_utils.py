"""Unit tests for network utility functions."""

from utils.network import normalize_host, is_allowed_host


def test_normalize_host():
    """Test host normalization logic."""
    assert normalize_host("LOCALHOST") == "localhost"
    assert normalize_host("  example.com  ") == "example.com"
    assert normalize_host("example.com.") == "example.com"
    assert normalize_host("example.com:5000") == "example.com"
    assert normalize_host("[::1]") == "::1"
    assert normalize_host("[::1]:5000") == "::1"
    assert normalize_host("") == ""
    assert normalize_host(None) == ""


def test_is_allowed_host():
    """Test host allow-list logic with wildcards."""
    allowed = ["localhost", "*.example.com", "other.org"]

    assert is_allowed_host("localhost", allowed) is True
    assert is_allowed_host("test.example.com", allowed) is True
    assert is_allowed_host("example.com", allowed) is False  # pattern was *.example.com
    assert is_allowed_host("other.org", allowed) is True
    assert is_allowed_host("malicious.com", allowed) is False
    assert is_allowed_host("localhost", ["*"]) is True
    assert is_allowed_host("any.thing", ["*"]) is True
    assert is_allowed_host("anything", []) is False
