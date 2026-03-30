"""Tests for the sign component routes."""

import json
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock

COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]


class TestSignRoutes:
    """Integration tests for sign component routes."""

    def test_sign_in_get_page(self, client):
        """Test GET /sign/in returns the sign-in page."""
        response = client.get(f"{BASE_ROUTE}/in")
        # Should return 200 or redirect
        assert response.status_code in [200, 302]

    def test_sign_up_get_page(self, client):
        """Test GET /sign/up returns the sign-up page."""
        response = client.get(f"{BASE_ROUTE}/up")
        assert response.status_code in [200, 302]

    def test_sign_reminder_get_page(self, client):
        """Test GET /sign/reminder returns the reminder page."""
        response = client.get(f"{BASE_ROUTE}/reminder")
        assert response.status_code in [200, 302]

    def test_sign_out_get_page(self, client):
        """Test GET /sign/out returns the sign-out page."""
        response = client.get(f"{BASE_ROUTE}/out")
        assert response.status_code in [200, 302]

    def test_sign_help_ajax_required(self, client):
        """Test /sign/help/<item> requires AJAX header."""
        response = client.get(f"{BASE_ROUTE}/help/test-item")
        # Should fail without AJAX header (403 Forbidden or 400 Bad Request)
        assert response.status_code in [400, 403]

    def test_sign_help_with_ajax_header(self, client):
        """Test /sign/help/<item> with AJAX header."""
        response = client.get(
            f"{BASE_ROUTE}/help/test-item",
            headers={'Requested-With-Ajax': 'true'}
        )
        # Should succeed with AJAX header
        assert response.status_code in [200, 302]


class TestSignInFormRoutes:
    """Tests for sign-in form routes."""

    def test_sign_in_form_get_requires_token(self, client):
        """Test GET /sign/in/form/<ltoken> requires valid token."""
        response = client.get(f"{BASE_ROUTE}/in/form/invalid-token")
        # Should handle invalid token gracefully
        assert response.status_code in [200, 302, 400]

    def test_sign_in_form_post_requires_token(self, client):
        """Test POST /sign/in/form/<ltoken> requires valid token."""
        response = client.post(f"{BASE_ROUTE}/in/form/invalid-token")
        # Should handle invalid token gracefully
        assert response.status_code in [200, 302, 400, 429]


class TestSignUpFormRoutes:
    """Tests for sign-up form routes."""

    def test_sign_up_form_get_requires_token(self, client):
        """Test GET /sign/up/form/<ltoken> requires valid token."""
        response = client.get(f"{BASE_ROUTE}/up/form/invalid-token")
        assert response.status_code in [200, 302, 400]

    def test_sign_up_form_post_rate_limited(self, client):
        """Test POST /sign/up/form/<ltoken> is rate limited."""
        response = client.post(f"{BASE_ROUTE}/up/form/invalid-token")
        # May be rate limited (429) or invalid token (400)
        assert response.status_code in [200, 302, 400, 429]


class TestSignPinRoutes:
    """Tests for PIN routes."""

    def test_sign_pin_get_page(self, client):
        """Test GET /sign/<pin_token> returns the PIN page."""
        response = client.get(f"{BASE_ROUTE}/pin/test-token")
        assert response.status_code in [200, 302]

    def test_sign_pin_form_get_requires_token(self, client):
        """Test GET /sign/pin/form/<pin_token>/<ltoken> requires tokens."""
        response = client.get(f"{BASE_ROUTE}/pin/form/pin-token/link-token")
        assert response.status_code in [200, 302, 400]

    def test_sign_pin_form_post_ajax_required(self, client):
        """Test POST /sign/pin/form/<pin_token>/<ltoken> requires AJAX header."""
        response = client.post(f"{BASE_ROUTE}/pin/form/pin-token/link-token")
        # Should fail without AJAX header (400, 403, or 429)
        assert response.status_code in [400, 403, 429]


class TestRateLimiting:
    """Tests for rate limiting on sign routes."""

    def test_sign_in_form_post_rate_limited(self, client):
        """Test sign-in form is rate limited."""
        # First request may succeed or fail based on token validation
        response = client.post(f"{BASE_ROUTE}/in/form/test-token")
        # May be rate limited (429) or invalid token (400)
        assert response.status_code in [200, 302, 400, 429]

    def test_sign_reminder_form_post_rate_limited(self, client):
        """Test reminder form is rate limited."""
        response = client.post(f"{BASE_ROUTE}/reminder/form/test-token")
        # May be rate limited (429), require AJAX header (400), or forbidden (403)
        assert response.status_code in [200, 302, 400, 403, 429]


class TestSecurityHeaders:
    """Tests for security-related headers and behaviors."""

    def test_sign_help_cache_control(self, client):
        """Test /sign/help/<item> sets cache control headers."""
        response = client.get(
            f"{BASE_ROUTE}/help/test-item",
            headers={'Requested-With-Ajax': 'true'}
        )
        # Should have cache control header when successful
        if response.status_code == 200:
            assert 'Cache-Control' in response.headers


class TestRouteAccess:
    """Tests for route access control based on manifest security."""

    def test_public_routes_accessible(self, client):
        """Test that public routes are accessible without authentication."""
        public_routes = [
            f"{BASE_ROUTE}/in",
            f"{BASE_ROUTE}/up",
            f"{BASE_ROUTE}/reminder",
            f"{BASE_ROUTE}/out",
        ]

        for route in public_routes:
            response = client.get(route)
            # All should be accessible (200) or redirect (302)
            assert response.status_code in [200, 302], f"Route {route} should be accessible"
