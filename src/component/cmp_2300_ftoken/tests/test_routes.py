"""Tests for the ftoken component routes."""

import json
from pathlib import Path

import pytest

COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]


class TestFtokenRoutes:
    """Integration tests for ftoken component routes."""

    def test_ftoken_js_file(self, client):
        """Test GET /ftoken/ftoken.min.js returns the JavaScript file."""
        response = client.get(f"{BASE_ROUTE}/ftoken.min.js")
        assert response.status_code == 200
        # Content type can be application/javascript or text/javascript
        assert 'javascript' in response.content_type
        assert 'Cache-Control' in response.headers

    def test_ftoken_requires_ajax_header(self, client):
        """Test /ftoken/<key>/<fetch_id>/<form_id> requires AJAX header."""
        response = client.get(f"{BASE_ROUTE}/test-key/test-fetch/test-form")
        # Should fail without AJAX header
        assert response.status_code in [400, 403]

    def test_ftoken_with_ajax_header(self, client):
        """Test /ftoken/<key>/<fetch_id>/<form_id> with AJAX header."""
        response = client.get(
            f"{BASE_ROUTE}/test-key/test-fetch/test-form",
            headers={'Requested-With-Ajax': 'true'}
        )
        # Should succeed with AJAX header
        assert response.status_code in [200, 302]


class TestFtokenAccess:
    """Tests for route access control."""

    def test_public_routes_accessible(self, client):
        """Test that public routes are accessible without authentication."""
        # The JS file should be publicly accessible
        response = client.get(f"{BASE_ROUTE}/ftoken.min.js")
        assert response.status_code == 200


class TestFtokenSecurity:
    """Tests for security-related behaviors."""

    def test_ftoken_js_cache_control(self, client):
        """Test /ftoken/ftoken.min.js sets cache control headers."""
        response = client.get(f"{BASE_ROUTE}/ftoken.min.js")
        assert response.status_code == 200
        assert 'Cache-Control' in response.headers
