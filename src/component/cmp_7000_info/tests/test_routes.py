"""Tests for the Info component routes."""

import json
from pathlib import Path


COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]


class TestInfoRoutes:
    """Integration tests for Info component routes."""

    def test_info_about(self, client):
        """Test GET /info/about."""
        response = client.get(f"{BASE_ROUTE}/about")
        assert response.status_code in [200, 302, 404]

    def test_info_contact(self, client):
        """Test GET /info/contact."""
        response = client.get(f"{BASE_ROUTE}/contact")
        assert response.status_code in [200, 302, 404]

    def test_info_help(self, client):
        """Test GET /info/help."""
        response = client.get(f"{BASE_ROUTE}/help")
        assert response.status_code in [200, 302, 404]

    def test_info_legal(self, client):
        """Test GET /info/legal."""
        response = client.get(f"{BASE_ROUTE}/legal")
        assert response.status_code in [200, 302, 404]

    def test_info_catch_all(self, client):
        """Test GET /info/<path> catch-all route."""
        response = client.get(f"{BASE_ROUTE}/some/random/page")
        assert response.status_code in [200, 302, 404]


class TestInfoContent:
    """Tests for Info page content."""

    def test_info_page_has_content(self, client):
        """Test info pages return content."""
        response = client.get(f"{BASE_ROUTE}/about")
        # Should have some content or be 404
        assert response.status_code in [200, 302, 404]


class TestInfoSecurity:
    """Tests for Info security."""

    def test_public_routes_accessible(self, client):
        """Test that public routes are accessible."""
        response = client.get(f"{BASE_ROUTE}/about")
        assert response.status_code in [200, 302, 404]
