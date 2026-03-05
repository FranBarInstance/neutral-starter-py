"""Tests for the Admin component routes."""

import pytest


class TestAdminRoutesAccess:
    """Integration tests for Admin component access control."""

    def test_admin_redirects_to_login_when_not_authenticated(self, client):
        """Test GET /admin redirects to login when not authenticated."""
        response = client.get('/admin/')
        # Should redirect to login (302) or return 401/403/404
        # 404 can occur if PreparedRequest denies access before route match
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_user_route_requires_auth(self, client):
        """Test /admin/user requires authentication."""
        response = client.get('/admin/user')
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_profile_route_requires_auth(self, client):
        """Test /admin/profile requires authentication."""
        response = client.get('/admin/profile')
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_post_route_requires_auth(self, client):
        """Test /admin/post requires authentication."""
        response = client.get('/admin/post')
        assert response.status_code in [302, 401, 403, 404]


class TestAdminRequestHandler:
    """Tests for AdminRequestHandler."""

    def test_handler_imports_correctly(self):
        """Test that AdminRequestHandler can be imported."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        assert AdminRequestHandler is not None

    def test_handler_extends_request_handler(self):
        """Test that AdminRequestHandler extends RequestHandler."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        from core.request_handler import RequestHandler
        assert issubclass(AdminRequestHandler, RequestHandler)

    def test_admin_home_handler_imports(self):
        """Test that AdminHomeRequestHandler can be imported."""
        from component.cmp_7040_admin.route.admin_handler import AdminHomeRequestHandler
        assert AdminHomeRequestHandler is not None

    def test_admin_user_handler_imports(self):
        """Test that AdminUserRequestHandler can be imported."""
        from component.cmp_7040_admin.route.admin_handler import AdminUserRequestHandler
        assert AdminUserRequestHandler is not None

    def test_admin_profile_handler_imports(self):
        """Test that AdminProfileRequestHandler can be imported."""
        from component.cmp_7040_admin.route.admin_handler import AdminProfileRequestHandler
        assert AdminProfileRequestHandler is not None

    def test_admin_post_handler_imports(self):
        """Test that AdminPostRequestHandler can be imported."""
        from component.cmp_7040_admin.route.admin_handler import AdminPostRequestHandler
        assert AdminPostRequestHandler is not None

    def test_valid_id_pattern_accepts_valid_ids(self):
        """Test that _is_valid_id accepts valid IDs."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        assert AdminRequestHandler._is_valid_id("user123") is True
        assert AdminRequestHandler._is_valid_id("user-123") is True
        assert AdminRequestHandler._is_valid_id("user_123") is True
        assert AdminRequestHandler._is_valid_id("User123") is True

    def test_valid_id_pattern_rejects_invalid_ids(self):
        """Test that _is_valid_id rejects invalid IDs."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        assert AdminRequestHandler._is_valid_id("") is False
        assert AdminRequestHandler._is_valid_id(None) is False
        assert AdminRequestHandler._is_valid_id("user@123") is False
        assert AdminRequestHandler._is_valid_id("user 123") is False
        assert AdminRequestHandler._is_valid_id("user.123") is False

    def test_valid_id_pattern_rejects_too_long_ids(self):
        """Test that _is_valid_id rejects IDs exceeding max length."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        long_id = "a" * 65  # Exceeds _MAX_ID_LENGTH of 64
        assert AdminRequestHandler._is_valid_id(long_id) is False

    def test_build_disabled_options_returns_list(self):
        """Test that _build_disabled_options returns a list."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        options = AdminRequestHandler._build_disabled_options()
        assert isinstance(options, list)
        assert len(options) > 0

    def test_build_profile_disabled_options_subset(self):
        """Test that profile disabled options is a subset of all options."""
        from component.cmp_7040_admin.route.admin_handler import AdminRequestHandler
        all_options = AdminRequestHandler._build_disabled_options()
        profile_options = AdminRequestHandler._build_profile_disabled_options()
        assert len(profile_options) <= len(all_options)

    def test_default_user_state_structure(self):
        """Test that _default_user_state returns expected structure."""
        from component.cmp_7040_admin.route.admin_handler import AdminUserRequestHandler
        state = AdminUserRequestHandler._default_user_state()
        assert "message" in state
        assert "error" in state
        assert "search" in state
        assert "role_filter" in state
        assert "disabled_filter" in state
        assert "order" in state
        assert "users" in state
        assert "can_full" in state
        assert "can_moderate" in state
        assert "is_dev_or_admin" in state
        assert state["can_full"] is False
        assert state["can_moderate"] is False


class TestAdminSecurity:
    """Tests for Admin component security policies."""

    def test_manifest_has_security_section(self):
        """Test that manifest has required security configuration."""
        import json
        import os

        manifest_path = os.path.join(
            os.path.dirname(__file__), '..', 'manifest.json'
        )
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        assert 'security' in manifest
        assert 'routes_auth' in manifest['security']
        assert 'routes_role' in manifest['security']
        assert '/' in manifest['security']['routes_auth']
        assert '/' in manifest['security']['routes_role']

    def test_manifest_requires_auth(self):
        """Test that manifest requires authentication for all routes."""
        import json
        import os

        manifest_path = os.path.join(
            os.path.dirname(__file__), '..', 'manifest.json'
        )
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        assert manifest['security']['routes_auth']['/'] is True

    def test_manifest_allows_admin_dev_moderator_roles(self):
        """Test that manifest allows admin, dev, and moderator roles."""
        import json
        import os

        manifest_path = os.path.join(
            os.path.dirname(__file__), '..', 'manifest.json'
        )
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        allowed_roles = manifest['security']['routes_role']['/']
        assert 'admin' in allowed_roles
        assert 'dev' in allowed_roles
        assert 'moderator' in allowed_roles
