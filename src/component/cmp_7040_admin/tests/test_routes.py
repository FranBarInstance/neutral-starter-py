"""Tests for the Admin component routes."""

import importlib
import json
from pathlib import Path

import pytest

COMPONENT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))
BASE_ROUTE = MANIFEST["route"]
PACKAGE_NAME = COMPONENT_ROOT.name


class TestAdminRoutesAccess:
    """Integration tests for Admin component access control."""

    def test_admin_redirects_to_login_when_not_authenticated(self, client):
        """Test GET /admin redirects to login when not authenticated."""
        response = client.get(f"{BASE_ROUTE}/")
        # Should redirect to login (302) or return 401/403/404
        # 404 can occur if PreparedRequest denies access before route match
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_user_route_requires_auth(self, client):
        """Test /admin/user requires authentication."""
        response = client.get(f"{BASE_ROUTE}/user")
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_profile_route_requires_auth(self, client):
        """Test /admin/profile requires authentication."""
        response = client.get(f"{BASE_ROUTE}/profile")
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_image_route_requires_auth(self, client):
        """Test /admin/image requires authentication."""
        response = client.get(f"{BASE_ROUTE}/image")
        assert response.status_code in [302, 401, 403, 404]

    def test_admin_post_route_requires_auth(self, client):
        """Test /admin/post requires authentication."""
        response = client.get(f"{BASE_ROUTE}/post")
        assert response.status_code in [302, 401, 403, 404]


class TestAdminRequestHandler:
    """Tests for AdminRequestHandler."""

    def test_handler_imports_correctly(self):
        """Test that AdminRequestHandler can be imported."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        assert AdminRequestHandler is not None

    def test_handler_extends_request_handler(self):
        """Test that AdminRequestHandler extends RequestHandler."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        from core.request_handler import RequestHandler
        assert issubclass(AdminRequestHandler, RequestHandler)

    def test_admin_home_handler_imports(self):
        """Test that AdminHomeRequestHandler can be imported."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminHomeRequestHandler = module.AdminHomeRequestHandler
        assert AdminHomeRequestHandler is not None

    def test_admin_user_handler_imports(self):
        """Test that AdminUserRequestHandler can be imported."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminUserRequestHandler = module.AdminUserRequestHandler
        assert AdminUserRequestHandler is not None

    def test_admin_profile_handler_imports(self):
        """Test that AdminProfileRequestHandler can be imported."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminProfileRequestHandler = module.AdminProfileRequestHandler
        assert AdminProfileRequestHandler is not None

    def test_admin_image_handler_imports(self):
        """Test that AdminImageRequestHandler can be imported."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminImageRequestHandler = module.AdminImageRequestHandler
        assert AdminImageRequestHandler is not None

    def test_admin_post_handler_imports(self):
        """Test that AdminPostRequestHandler can be imported."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminPostRequestHandler = module.AdminPostRequestHandler
        assert AdminPostRequestHandler is not None

    def test_valid_id_pattern_accepts_valid_ids(self):
        """Test that _is_valid_id accepts valid IDs."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        assert AdminRequestHandler._is_valid_id("user123") is True
        assert AdminRequestHandler._is_valid_id("user-123") is True
        assert AdminRequestHandler._is_valid_id("user_123") is True
        assert AdminRequestHandler._is_valid_id("User123") is True

    def test_valid_id_pattern_rejects_invalid_ids(self):
        """Test that _is_valid_id rejects invalid IDs."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        assert AdminRequestHandler._is_valid_id("") is False
        assert AdminRequestHandler._is_valid_id(None) is False
        assert AdminRequestHandler._is_valid_id("user@123") is False
        assert AdminRequestHandler._is_valid_id("user 123") is False
        assert AdminRequestHandler._is_valid_id("user.123") is False

    def test_valid_id_pattern_rejects_too_long_ids(self):
        """Test that _is_valid_id rejects IDs exceeding max length."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        long_id = "a" * 65  # Exceeds _MAX_ID_LENGTH of 64
        assert AdminRequestHandler._is_valid_id(long_id) is False

    def test_build_disabled_options_returns_list(self):
        """Test that _build_disabled_options returns a list."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        options = AdminRequestHandler._build_disabled_options()
        assert isinstance(options, list)
        assert len(options) > 0

    def test_build_profile_disabled_options_subset(self):
        """Test that profile disabled options is a subset of all options."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminRequestHandler = module.AdminRequestHandler
        all_options = AdminRequestHandler._build_disabled_options()
        profile_options = AdminRequestHandler._build_profile_disabled_options()
        assert len(profile_options) <= len(all_options)

    def test_default_user_state_structure(self):
        """Test that _default_user_state returns expected structure."""
        module = importlib.import_module(f"component.{PACKAGE_NAME}.route.admin_handler")
        AdminUserRequestHandler = module.AdminUserRequestHandler
        state = AdminUserRequestHandler._default_user_state()
        assert "message" in state
        assert "error" in state
        assert "search" in state
        assert "filter_role" in state
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
        manifest = MANIFEST

        assert 'security' in manifest
        assert 'routes_auth' in manifest['security']
        assert 'routes_role' in manifest['security']
        assert '/' in manifest['security']['routes_auth']
        assert '/' in manifest['security']['routes_role']

    def test_manifest_requires_auth(self):
        """Test that manifest requires authentication for all routes."""
        manifest = MANIFEST

        assert manifest['security']['routes_auth']['/'] is True

    def test_manifest_allows_admin_and_moderator_roles(self):
        """Test that manifest allows admin and moderator roles."""
        manifest = MANIFEST

        allowed_roles = manifest['security']['routes_role']['/']
        assert 'admin' in allowed_roles
        assert 'moderator' in allowed_roles
