"""Tests for the cmp_5000_user component routes."""

BASE_ROUTE = "/user"


class TestUserRoutes:
    """Integration tests for user component routes."""

    def test_user_profile_view_requires_auth(self, client):
        """GET /user requires authentication."""
        response = client.get(BASE_ROUTE)
        assert response.status_code == 401

    def test_user_profile_edit_requires_auth(self, client):
        """GET /user/profile requires authentication."""
        response = client.get(f"{BASE_ROUTE}/profile")
        assert response.status_code == 401

    def test_user_email_requires_auth(self, client):
        """GET /user/email requires authentication."""
        response = client.get(f"{BASE_ROUTE}/email")
        assert response.status_code == 401

    def test_user_account_requires_auth(self, client):
        """GET /user/account requires authentication."""
        response = client.get(f"{BASE_ROUTE}/account")
        assert response.status_code == 401


class TestUserFormRoutes:
    """Tests for user AJAX form routes."""

    def test_profile_ajax_get_requires_token(self, client):
        """GET /user/profile/ajax/<ltoken> requires authentication."""
        response = client.get(f"{BASE_ROUTE}/profile/ajax/invalid-token")
        assert response.status_code == 401

    def test_profile_ajax_post_requires_token(self, client):
        """POST /user/profile/ajax/<ltoken> requires authentication."""
        response = client.post(f"{BASE_ROUTE}/profile/ajax/invalid-token")
        assert response.status_code == 401


class TestUserSecurity:
    """Tests for security-related behaviors."""

    def test_all_routes_require_auth(self, client):
        """All user routes require authentication."""
        protected_routes = [
            BASE_ROUTE,
            f"{BASE_ROUTE}/profile",
            f"{BASE_ROUTE}/email",
            f"{BASE_ROUTE}/account",
        ]

        for route in protected_routes:
            response = client.get(route)
            assert response.status_code == 401, f"Route {route} should require authentication"

    def test_ajax_routes_require_auth(self, client):
        """All AJAX routes require authentication."""
        ajax_routes = [
            f"{BASE_ROUTE}/profile/ajax/test-token",
            f"{BASE_ROUTE}/email/pin/ajax/test-token",
            f"{BASE_ROUTE}/email/add/ajax/test-token",
            f"{BASE_ROUTE}/email/delete/ajax/test-token",
            f"{BASE_ROUTE}/account/password/pin/ajax/test-token",
            f"{BASE_ROUTE}/account/password/ajax/test-token",
            f"{BASE_ROUTE}/account/birthdate/pin/ajax/test-token",
            f"{BASE_ROUTE}/account/birthdate/ajax/test-token",
            f"{BASE_ROUTE}/account/login/ajax/test-token",
        ]

        for route in ajax_routes:
            response = client.get(route)
            assert response.status_code == 401, f"AJAX route {route} should require authentication"

            response = client.post(route)
            assert response.status_code == 401, f"AJAX route {route} should require authentication"
