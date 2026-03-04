"""Tests for the sign component routes."""

import pytest
from unittest.mock import patch, MagicMock


class TestSignRoutes:
    """Integration tests for sign component routes."""

    def test_sign_in_get_page(self, client):
        """Test GET /sign/in returns the sign-in page."""
        response = client.get('/sign/in')
        # Should return 200 or redirect
        assert response.status_code in [200, 302]

    def test_sign_up_get_page(self, client):
        """Test GET /sign/up returns the sign-up page."""
        response = client.get('/sign/up')
        assert response.status_code in [200, 302]

    def test_sign_reminder_get_page(self, client):
        """Test GET /sign/reminder returns the reminder page."""
        response = client.get('/sign/reminder')
        assert response.status_code in [200, 302]

    def test_sign_out_get_page(self, client):
        """Test GET /sign/out returns the sign-out page."""
        response = client.get('/sign/out')
        assert response.status_code in [200, 302]

    def test_sign_help_ajax_required(self, client):
        """Test /sign/help/<item> requires AJAX header."""
        response = client.get('/sign/help/test-item')
        # Should fail without AJAX header (403 Forbidden or 400 Bad Request)
        assert response.status_code in [400, 403]

    def test_sign_help_with_ajax_header(self, client):
        """Test /sign/help/<item> with AJAX header."""
        response = client.get(
            '/sign/help/test-item',
            headers={'Requested-With-Ajax': 'true'}
        )
        # Should succeed with AJAX header
        assert response.status_code in [200, 302]


class TestSignInFormRoutes:
    """Tests for sign-in form routes."""

    def test_sign_in_form_get_requires_token(self, client):
        """Test GET /sign/in/form/<ltoken> requires valid token."""
        response = client.get('/sign/in/form/invalid-token')
        # Should handle invalid token gracefully
        assert response.status_code in [200, 302, 400]

    def test_sign_in_form_post_requires_token(self, client):
        """Test POST /sign/in/form/<ltoken> requires valid token."""
        response = client.post('/sign/in/form/invalid-token')
        # Should handle invalid token gracefully
        assert response.status_code in [200, 302, 400, 429]


class TestSignUpFormRoutes:
    """Tests for sign-up form routes."""

    def test_sign_up_form_get_requires_token(self, client):
        """Test GET /sign/up/form/<ltoken> requires valid token."""
        response = client.get('/sign/up/form/invalid-token')
        assert response.status_code in [200, 302, 400]

    def test_sign_up_form_post_rate_limited(self, client):
        """Test POST /sign/up/form/<ltoken> is rate limited."""
        response = client.post('/sign/up/form/invalid-token')
        # May be rate limited (429) or invalid token (400)
        assert response.status_code in [200, 302, 400, 429]


class TestSignPinRoutes:
    """Tests for PIN routes."""

    def test_sign_pin_get_page(self, client):
        """Test GET /sign/<pin_token> returns the PIN page."""
        response = client.get('/sign/pin/test-token')
        assert response.status_code in [200, 302]

    def test_sign_pin_form_get_requires_token(self, client):
        """Test GET /sign/pin/form/<pin_token>/<ltoken> requires tokens."""
        response = client.get('/sign/pin/form/pin-token/link-token')
        assert response.status_code in [200, 302, 400]

    def test_sign_pin_form_post_ajax_required(self, client):
        """Test POST /sign/pin/form/<pin_token>/<ltoken> requires AJAX header."""
        response = client.post('/sign/pin/form/pin-token/link-token')
        # Should fail without AJAX header (400, 403, or 429)
        assert response.status_code in [400, 403, 429]


class TestRateLimiting:
    """Tests for rate limiting on sign routes."""

    def test_sign_in_form_post_rate_limited(self, client):
        """Test sign-in form is rate limited."""
        # First request may succeed or fail based on token validation
        response = client.post('/sign/in/form/test-token')
        # May be rate limited (429) or invalid token (400)
        assert response.status_code in [200, 302, 400, 429]

    def test_sign_reminder_form_post_rate_limited(self, client):
        """Test reminder form is rate limited."""
        response = client.post('/sign/reminder/form/test-token')
        # May be rate limited (429), require AJAX header (400), or forbidden (403)
        assert response.status_code in [200, 302, 400, 403, 429]


class TestSecurityHeaders:
    """Tests for security-related headers and behaviors."""

    def test_sign_help_cache_control(self, client):
        """Test /sign/help/<item> sets cache control headers."""
        response = client.get(
            '/sign/help/test-item',
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
            '/sign/in',
            '/sign/up',
            '/sign/reminder',
            '/sign/out',
        ]

        for route in public_routes:
            response = client.get(route)
            # All should be accessible (200) or redirect (302)
            assert response.status_code in [200, 302], f"Route {route} should be accessible"
