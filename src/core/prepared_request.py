"""Request bootstrap object built once per request and shared via Flask.g.

WARNING: This module is INTERNAL to the core framework.

PreparedRequest is designed for internal use by the framework's request
processing pipeline only. Component developers MUST NOT import or use
PreparedRequest directly.

For component route handlers, use RequestHandler instead:
    from core.request_handler import RequestHandler
    dispatch = RequestHandler(g.pr, route, bp.neutral_route)

Using PreparedRequest directly from components will bypass security checks
and may cause undefined behavior.
"""

from dataclasses import dataclass, field
from typing import Any
import os
import json
import logging
from functools import lru_cache

from app.config import Config
from constants import DELETED
from utils import merge_dict
from utils.tokens import (
    utoken_extract,
    utoken_update,
    ltoken_create,
)
from utils.sbase64url import sbase64url_md5
from utils.nonce import get_nonce
from .schema import Schema
from .session import Session
from .user import User
from .template import Template

logger = logging.getLogger(__name__)


# Cache for parsed blueprint schemas to avoid reading JSON on every request
@lru_cache(maxsize=128)
def _load_bp_schema_cached(schema_path: str) -> dict:
    """Load and parse blueprint schema with caching.

    Args:
        schema_path: Path to the schema JSON file

    Returns:
        Parsed JSON as dict
    """
    with open(schema_path, "r", encoding="utf-8") as file:
        return json.load(file)


@dataclass
class PreparedRequest:  # pylint: disable=too-many-instance-attributes
    """Core bootstrap object shared for the current request.

    Built once per request in the global before_request handler.
    Evaluates security policies and exposes the final access decision.

    WARNING: INTERNAL USE ONLY.

    This class is part of the framework's internal request processing
    infrastructure. It is NOT intended for use by component code.

    Component route handlers must use RequestHandler instead:
        from core.request_handler import RequestHandler
        from flask import g

        @bp.route("/")
        def index(route):
            dispatch = RequestHandler(g.pr, route, bp.neutral_route)
            return dispatch.render_route()

    Accessing PreparedRequest directly from components bypasses the
    component-specific context setup and may lead to security issues.
    """

    # Request object (required)
    req: Any

    # Core objects (initialized by build())
    schema: Any | None = None
    session: Any | None = None
    user: Any | None = None
    view: Any | None = None

    # Shared request data (initialized by build())
    schema_data: dict = field(default_factory=dict)
    schema_local_data: dict = field(default_factory=dict)
    ajax_request: bool = False

    # Routing/policy context
    route_path: str = "/"
    policy: dict | None = None
    allowed_roles: list[str] | None = None
    route_require_auth: bool | None = None

    # Access decision (fail closed by default)
    allowed: bool = False
    deny_status: int | None = None
    deny_reason: str | None = None

    # Internal state
    _component_bp: Any = None
    _component_uuid: str | None = None

    def build(self, component_bp=None, full_path: str = "") -> "PreparedRequest":
        """Build all request-scoped core context and evaluate policies.

        Args:
            component_bp: The component blueprint
            full_path: Full request path (for security policy evaluation)

        Stages:
        1. Core schema initialization
        2. Component context setup (including CURRENT_BP_SCHEMA)
        3. Blueprint schema merge
        4. Core objects initialization (Session, User, Template)
        5. Context materialization (user, tokens, cookies)
        6. Route/policy resolution
        7. Policy evaluation (auth → status → roles)
        """
        self._component_bp = component_bp

        # Stage 1: Initialize schema (needed for everything else)
        self.schema = Schema(self.req)
        self.schema_data = self.schema.properties["data"]
        self.schema_local_data = self.schema.properties["inherit"]["data"]

        # Stage 2: Setup component context (establishes CURRENT_BP_SCHEMA)
        # Note: CURRENT_COMP_ROUTE will be set by RequestHandler
        self._setup_component_context()

        # Stage 3: Merge blueprint-specific schema
        self._merge_bp_schema()

        # Stage 4: Initialize remaining core objects
        self._init_core_objects()

        # Stage 5: Materialize request context
        self._materialize_context()

        # Stage 6: Resolve route security policy (uses full path)
        self._resolve_route_policy(full_path)

        # Stage 7: Evaluate security policy
        self._evaluate_policy()

        return self

    def _setup_component_context(self) -> None:
        """Setup component context variables in schema data.

        Establishes:
        - CURRENT_COMP_ROUTE (set by RequestHandler with actual route)
        - CURRENT_COMP_ROUTE_SANITIZED
        - CURRENT_NEUTRAL_ROUTE
        - CURRENT_COMP_NAME
        - CURRENT_COMP_UUID
        - CURRENT_COMP_PATH
        - CURRENT_BP_SCHEMA

        Note: All requests must belong to a component. If no blueprint is provided,
        the component UUID will be None and the request will be denied.

        Note: CURRENT_COMP_ROUTE is intentionally left for RequestHandler to set,
        as it has access to the actual component-relative route from the route handler.
        """
        data = self.schema_data

        # CURRENT_COMP_ROUTE will be set by RequestHandler with the actual route
        # We only set a placeholder here for backward compatibility
        data["CURRENT_COMP_ROUTE"] = Config.COMP_ROUTE_ROOT
        data["CURRENT_COMP_ROUTE_SANITIZED"] = Config.COMP_ROUTE_ROOT.replace("/", ":")

        # Get component info from blueprint (required)
        # If no blueprint, UUID remains None and request will be denied
        name = None
        uuid = None
        neutral_route = data.get("CURRENT_NEUTRAL_ROUTE", "")

        if self._component_bp and hasattr(self._component_bp, "component"):
            component = self._component_bp.component
            name = component.get("name")
            uuid = component.get("manifest", {}).get("uuid")
            neutral_route = getattr(self._component_bp, "neutral_route", neutral_route)

        data["CURRENT_NEUTRAL_ROUTE"] = neutral_route
        data["CURRENT_COMP_NAME"] = name
        data["CURRENT_COMP_UUID"] = uuid
        self._component_uuid = uuid

        # Component path
        data["CURRENT_COMP_PATH"] = (
            os.path.join(Config.COMPONENT_DIR, name)
            if name
            else data.get("CURRENT_COMP_PATH", "")
        )

        # Blueprint schema path (critical for _merge_bp_schema)
        if uuid and uuid in data:
            data["CURRENT_BP_SCHEMA"] = data[uuid].get("bp_schema")
        else:
            data["CURRENT_BP_SCHEMA"] = None

    def _merge_bp_schema(self) -> None:
        """Merge component-specific schema into main schema.

        Fail closed: if schema exists but cannot be loaded, raise exception.
        Uses cached schema to avoid repeated file I/O.
        """
        schema_path = self.schema_data.get("CURRENT_BP_SCHEMA")
        if not schema_path:
            return

        # Use cached schema to avoid repeated file reads
        try:
            cached_schema = _load_bp_schema_cached(schema_path)
            merge_dict(self.schema.properties, cached_schema)
        except Exception:  # pylint: disable=broad-except
            # Fail closed: schema errors propagate (request will fail)
            # Invalidate cache on error and retry once
            _load_bp_schema_cached.cache_clear()
            cached_schema = _load_bp_schema_cached(schema_path)
            merge_dict(self.schema.properties, cached_schema)

    def _init_core_objects(self) -> None:
        """Initialize core framework objects that depend on schema."""
        self.session = Session(self.schema_data["CONTEXT"]["SESSION"])
        self.user = User()
        self.view = Template(self.schema)

        # Detect AJAX request
        self.ajax_request = bool(
            self.schema_data["CONTEXT"]["HEADERS"].get("Requested-With-Ajax")
        )

    def _materialize_context(self) -> None:
        """Build request context: session, user, tokens, cookies."""
        # Session handling
        session_id, session_cookie = self.session.get()
        self.schema_data["CONTEXT"]["SESSION"] = session_id

        # Session data
        session_data = self.session.get_session_properties() if session_id else {}
        self.schema_data["CONTEXT"]["SESSION_DATA"] = (
            session_data if isinstance(session_data, dict) else {}
        )

        # Request user (rebuilt from DB per request, not persisted in session)
        self.schema_data["USER"] = self._build_request_user(
            self.schema_data["CONTEXT"]["SESSION_DATA"]
        )
        self.schema_data["CONTEXT"]["SESSION_DATA"].pop("user", None)
        self.schema_data["CONTEXT"]["SESSION_DATA"].pop("user_data", None)
        # Add localdev role if SessionDev session is active
        self._add_localdev_role_if_session_dev()

        # Session flags
        self.schema_data["HAS_SESSION"] = "true" if session_id else None
        self.schema_data["HAS_SESSION_STR"] = "true" if session_id else "false"

        # Security tokens
        self.schema_data["CSP_NONCE"] = get_nonce()
        self._parse_utoken()
        self.schema_data["LTOKEN"] = ltoken_create(
            self.schema_data["CONTEXT"]["UTOKEN"]
        )

        # Non-AJAX: setup cookies
        if not self.ajax_request:
            self._setup_cookies(session_cookie)

    def _build_request_user(self, session_data: dict) -> dict:
        """Build schema_data['USER'] from session identity and current DB state."""
        user_id = self._extract_session_user_id(session_data)
        return self.user.get_runtime_user(user_id)

    @staticmethod
    def _extract_session_user_id(session_data: dict) -> str:
        """Extract persistent session userId, with fallback for legacy sessions."""
        if not isinstance(session_data, dict):
            return ""

        user_id = str(session_data.get("userId") or "").strip()
        if user_id:
            return user_id

        legacy_user = session_data.get("user")
        if not isinstance(legacy_user, dict):
            legacy_user = session_data.get("user_data", {})
        if not isinstance(legacy_user, dict):
            return ""

        return str(legacy_user.get("userId") or legacy_user.get("id") or "").strip()

    def _add_localdev_role_if_session_dev(self) -> None:
        """Add 'localdev' role to USER if SessionDev session is active."""
        # Avoid circular import by importing here
        # pylint: disable=import-outside-toplevel
        from .session_dev import SessionDev

        session_dev = SessionDev()
        if session_dev.check_session():
            self._get_current_user()["profile_roles"]["localdev"] = "localdev"

    def _get_current_user(self) -> dict:
        """Return normalized request user data."""
        user = self.schema_data.get("USER", {})
        return user if isinstance(user, dict) else {}

    def _parse_utoken(self) -> None:
        """Parse/update UTOKEN for form submission protection."""
        utoken_cookie_value = self.req.cookies.get(Config.UTOKEN_KEY)

        if self.req.method == "GET" and not self.ajax_request:
            utoken_token, utoken_cookie = utoken_update(utoken_cookie_value)
        else:
            utoken_token, utoken_cookie = utoken_extract(utoken_cookie_value)

        self.schema_data["CONTEXT"]["UTOKEN"] = utoken_token

        if not self.ajax_request:
            self.view.add_cookie({**utoken_cookie})

    def _setup_cookies(self, session_cookie: dict) -> None:
        """Setup all non-AJAX cookies."""
        # Tab change detection cookie
        detect = "start"
        detect += self.schema_data["CONTEXT"].get("UTOKEN") or "none"
        detect += self.schema_data["CONTEXT"].get("SESSION") or "none"

        cookies = {
            **session_cookie,
            Config.TAB_CHANGES_KEY: {
                "key": Config.TAB_CHANGES_KEY,
                "value": sbase64url_md5(detect),
            },
            Config.THEME_KEY: {
                "key": Config.THEME_KEY,
                "value": self.schema_data["current"]["theme"]["theme"],
            },
            Config.THEME_COLOR_KEY: {
                "key": Config.THEME_COLOR_KEY,
                "value": self.schema_data["current"]["theme"]["color"],
            },
            Config.LANG_KEY: {
                "key": Config.LANG_KEY,
                "value": self.schema.properties["inherit"]["locale"]["current"],
            },
        }

        self.view.add_cookie(cookies)

    def _resolve_route_policy(self, route: str) -> None:
        """Resolve route metadata and security policy from blueprint manifest.

        Policy keys in manifest are relative to component route.
        They are expanded with component route for matching against full request path.
        """
        # Normalize route path (use full path as-is)
        self.route_path = self._normalize_route_path(route)

        # Reset policy state
        self.policy = None
        self.allowed_roles = None
        self.route_require_auth = None

        # Ensure we have component UUID and blueprint
        self._component_uuid = self.schema_data.get("CURRENT_COMP_UUID")
        if not self._component_uuid:
            # No component UUID - policy remains None, will be denied in _evaluate_policy
            return

        # Load security policy from blueprint manifest (required)
        # If no blueprint or no security policy, request will be denied
        if not self._component_bp or not hasattr(self._component_bp, "manifest"):
            return

        manifest = self._component_bp.manifest
        if not isinstance(manifest, dict):
            return

        security = manifest.get("security")
        if not isinstance(security, dict):
            return

        self.policy = security

        # Get component route for expanding relative policy keys
        # e.g., component route="/admin", policy key "/users" → expanded "/admin/users"
        component_route = manifest.get("route", "")

        # Resolve routes_auth policy
        routes_auth = security.get("routes_auth")
        if isinstance(routes_auth, dict):
            self.route_require_auth = self._resolve_policy_by_prefix(
                self.route_path, routes_auth, expected_type=bool,
                component_route=component_route
            )

        # Resolve routes_role policy
        routes_role = security.get("routes_role")
        if isinstance(routes_role, dict):
            matched_roles = self._resolve_policy_by_prefix(
                self.route_path, routes_role, expected_type=list,
                component_route=component_route
            )
            if matched_roles is not None:
                self.allowed_roles = [
                    str(role).strip().lower()
                    for role in matched_roles
                    if str(role).strip()
                ]

    def _evaluate_policy(self) -> None:
        """Evaluate core security policy: auth → status → roles.

        Fail closed by default. Any missing policy or failed check denies access.
        """
        self.allowed = False
        self.deny_status = None
        self.deny_reason = None

        # Fail closed: policy must exist (all requests must belong to a component)
        if self.policy is None:
            self._deny(403, "missing_component_policy")
            return

        # Validate policy structure
        if not isinstance(self.policy, dict):
            self._deny(403, "invalid_security_policy")
            return

        routes_auth = self.policy.get("routes_auth")
        routes_role = self.policy.get("routes_role")

        if not isinstance(routes_auth, dict):
            self._deny(403, "missing_routes_auth_policy")
            return

        if not isinstance(routes_role, dict):
            self._deny(403, "missing_routes_role_policy")
            return

        # Check 1: Route must be mapped in both policies
        if self.route_require_auth is None:
            self._deny(403, "route_not_mapped_in_auth_policy")
            return

        if self.allowed_roles is None:
            self._deny(403, "route_not_mapped_in_roles_policy")
            return

        # Check 2: Roles list must not be empty
        if not self.allowed_roles:
            self._deny(403, "empty_roles_policy")
            return

        # Check 3: Wildcard '*' cannot be mixed with explicit roles
        if "*" in self.allowed_roles and len(self.allowed_roles) > 1:
            self._deny(403, "invalid_roles_wildcard_mixed")
            return

        # Stage 1: Authentication check
        is_authenticated = bool(self._get_current_user().get("auth"))
        if self.route_require_auth and not is_authenticated:
            self._deny(401, "auth_required")
            return

        # Stage 2: Status restrictions (core policy)
        status_reason = self._get_restricted_status_reason()
        if status_reason:
            self._deny(403, status_reason)
            return

        # Stage 3: Role authorization check
        if "*" in self.allowed_roles:
            # Wildcard allows any role (including no role if auth not required)
            self.allowed = True
            return

        # Check if user has any of the allowed roles
        user_role_map = self._get_current_user().get("profile_roles", {})
        user_roles = set(user_role_map.keys())

        if not user_roles.intersection(set(self.allowed_roles)):
            self._deny(403, "role_not_allowed")
            return

        self.allowed = True

    def _get_restricted_status_reason(self) -> str | None:
        """Check if user/profile status restricts access.

        Returns deny reason string if restricted, None if allowed.
        """
        current_user = self._get_current_user()
        user_disabled = current_user.get("user_disabled", {})
        profile_disabled = current_user.get("profile_disabled", {})

        if not isinstance(user_disabled, dict):
            user_disabled = {}
        if not isinstance(profile_disabled, dict):
            profile_disabled = {}

        # Deleted users are always blocked (highest priority)
        if DELETED in user_disabled:
            return "user_status_deleted"

        # Any other user status flag restricts access
        if user_disabled:
            return "user_status_restricted"

        # Profile status restrictions
        if profile_disabled:
            return "profile_status_restricted"

        return None

    def _deny(self, status: int, reason: str) -> None:
        """Record denial and log structured deny event."""
        self.allowed = False
        self.deny_status = status
        self.deny_reason = reason

        # Structured deny log for observability
        logger.warning(
            "Access denied: component=%s route=%s reason=%s status=%d",
            self._component_uuid or "none",
            self.route_path,
            reason,
            status,
            extra={
                "event": "access_denied",
                "component_uuid": self._component_uuid,
                "route_path": self.route_path,
                "deny_reason": reason,
                "deny_status": status,
                "user_id": self._get_current_user().get("id"),
                "has_session": self.schema_data.get("HAS_SESSION") == "true",
            }
        )

    @staticmethod
    def _normalize_route_path(route: str) -> str:
        """Normalize route path for policy lookup.

        Rules:
        - Empty path -> /
        - Ensure leading slash
        - Remove trailing slash except root
        """
        path = (route or "").strip()

        if not path:
            return "/"

        if not path.startswith("/"):
            path = f"/{path}"

        # Remove trailing slash except for root
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

        return path or "/"

    @staticmethod
    def _route_matches_prefix(route_path: str, prefix_path: str) -> bool:
        """Check if route_path matches the given prefix.

        - Root prefix "/" matches all routes
        - Otherwise matches exact or prefix with segment boundary
        """
        if prefix_path == "/":
            return True
        return (
            route_path == prefix_path or
            route_path.startswith(f"{prefix_path}/")
        )

    def _resolve_policy_by_prefix(
        self,
        route_path: str,
        policy_map: dict | None,
        expected_type: type,
        component_route: str = ""
    ) -> Any:
        """Resolve policy by prefix matching (most specific wins).

        Args:
            route_path: Normalized route path (full request path)
            policy_map: Dict mapping relative path prefixes to policy values
            expected_type: Expected type of policy value
            component_route: Component's base route for expanding relative keys

        Returns:
            Best matching policy value or None if no match
        """
        if not isinstance(policy_map, dict):
            return None

        best_prefix: str | None = None
        best_value: Any = None

        for prefix, value in policy_map.items():
            # Expand relative policy key with component route
            # e.g., prefix="/users" + component_route="/admin" → expanded="/admin/users"
            if component_route and prefix.startswith("/"):
                expanded_prefix = component_route + prefix
            else:
                expanded_prefix = prefix

            normalized_prefix = self._normalize_route_path(expanded_prefix)

            if not self._route_matches_prefix(route_path, normalized_prefix):
                continue

            if not isinstance(value, expected_type):
                continue

            # Most specific (longest) prefix wins
            if best_prefix is None or len(normalized_prefix) > len(best_prefix):
                best_prefix = normalized_prefix
                best_value = value

        return best_value
def clear_bp_schema_cache() -> None:
    """Clear the blueprint schema cache. Useful for development/hot reloading."""
    _load_bp_schema_cached.cache_clear()
