"""Tests for the backtotop component routes."""

import json
from pathlib import Path


COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]


class TestBackToTopRoutes:
    """Integration tests for backtotop component routes."""

    def test_backtotop_css_file(self, client):
        """Test GET /backtotop/css/backtotop.min.css returns the CSS file."""
        response = client.get(f"{BASE_ROUTE}/css/backtotop.min.css")
        assert response.status_code == 200
        assert 'css' in response.content_type
        assert 'Cache-Control' in response.headers

    def test_backtotop_js_file(self, client):
        """Test GET /backtotop/js/backtotop.min.js returns the JavaScript file."""
        response = client.get(f"{BASE_ROUTE}/js/backtotop.min.js")
        assert response.status_code == 200
        assert 'javascript' in response.content_type
        assert 'Cache-Control' in response.headers


class TestBackToTopAccess:
    """Tests for route access control."""

    def test_static_routes_accessible(self, client):
        """Test that static routes are publicly accessible."""
        css_response = client.get(f"{BASE_ROUTE}/css/backtotop.min.css")
        js_response = client.get(f"{BASE_ROUTE}/js/backtotop.min.js")

        assert css_response.status_code == 200
        assert js_response.status_code == 200


class TestBackToTopSecurity:
    """Tests for security-related behaviors."""

    def test_css_cache_control(self, client):
        """Test CSS file has cache control headers."""
        response = client.get(f"{BASE_ROUTE}/css/backtotop.min.css")
        assert response.status_code == 200
        assert 'Cache-Control' in response.headers

    def test_js_cache_control(self, client):
        """Test JS file has cache control headers."""
        response = client.get(f"{BASE_ROUTE}/js/backtotop.min.js")
        assert response.status_code == 200
        assert 'Cache-Control' in response.headers
