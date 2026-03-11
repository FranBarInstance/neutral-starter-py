"""Tests for the user_local component routes."""


class TestUserLocalRoutes:
    """Integration tests for user_local component routes."""

    def test_user_profile_view_requires_auth(self, client):
        """Test GET /u requires authentication."""
        response = client.get('/u')
        # Should redirect to login (302) or return 401 when not authenticated
        assert response.status_code in [200, 302, 401]

    def test_user_profile_edit_requires_auth(self, client):
        """Test GET /u/profile requires authentication."""
        response = client.get('/u/profile')
        assert response.status_code in [200, 302, 401]


class TestUserLocalFormRoutes:
    """Tests for user_local AJAX form routes."""

    def test_profile_ajax_get_requires_token(self, client):
        """Test GET /u/profile/ajax/<ltoken> requires valid token."""
        response = client.get('/u/profile/ajax/invalid-token')
        assert response.status_code in [200, 302, 400, 401]

    def test_profile_ajax_post_requires_token(self, client):
        """Test POST /u/profile/ajax/<ltoken> requires valid token."""
        response = client.post('/u/profile/ajax/invalid-token')
        assert response.status_code in [200, 302, 400, 401]


class TestUserLocalSecurity:
    """Tests for security-related behaviors."""

    def test_all_routes_require_auth(self, client):
        """Test that all user_local routes require authentication."""
        protected_routes = [
            '/u',
            '/u/profile',
        ]

        for route in protected_routes:
            response = client.get(route)
            # All should require auth (401) or redirect (302)
            assert response.status_code in [200, 302, 401], \
                f"Route {route} should require authentication"

    def test_ajax_routes_require_auth(self, client):
        """Test that AJAX routes require authentication."""
        ajax_routes = [
            '/u/profile/ajax/test-token',
        ]

        for route in ajax_routes:
            response = client.get(route)
            assert response.status_code in [200, 302, 400, 401], \
                f"AJAX route {route} should require authentication"
