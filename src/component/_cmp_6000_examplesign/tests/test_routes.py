"""Tests for the example sign component routes."""

import json
from pathlib import Path


COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]


class TestExampleSignRoutes:
    """Integration tests for example sign routes."""

    def test_example_sign_home_page(self, client):
        """Test GET /example-sign returns the component home page."""
        response = client.get(f"{BASE_ROUTE}/")
        assert response.status_code in [200, 302]

    def test_example_sign_login_page(self, client):
        """Test GET /example-sign/login returns the login page."""
        response = client.get(f"{BASE_ROUTE}/login")
        assert response.status_code in [200, 302]

    def test_example_sign_logout_page(self, client):
        """Test GET /example-sign/logout returns the logout page."""
        response = client.get(f"{BASE_ROUTE}/logout")
        assert response.status_code in [200, 302]


class TestExampleSignAjax:
    """Tests for example sign AJAX routes."""

    def test_help_requires_ajax_header(self, client):
        """Test /example-sign/help/<item> requires the AJAX header."""
        response = client.get(f"{BASE_ROUTE}/help/notrobot")
        assert response.status_code in [400, 403]

    def test_help_with_ajax_header(self, client):
        """Test /example-sign/help/<item> works with the AJAX header."""
        response = client.get(
            f"{BASE_ROUTE}/help/notrobot",
            headers={"Requested-With-Ajax": "true"},
        )
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            assert "Cache-Control" in response.headers


class TestExampleSignSecurity:
    """Tests for example sign security-related behaviour."""

    def test_login_ajax_with_invalid_token_is_handled(self, client):
        """Test login AJAX routes handle invalid tokens gracefully."""
        response = client.get(f"{BASE_ROUTE}/login/ajax/invalid-token")
        assert response.status_code in [200, 302, 400]

    def test_logout_ajax_with_invalid_token_is_handled(self, client):
        """Test logout AJAX routes handle invalid tokens gracefully."""
        response = client.get(f"{BASE_ROUTE}/logout/ajax/invalid-token")
        assert response.status_code in [200, 302, 400]
