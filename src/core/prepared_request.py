"""Request bootstrap object built once per request and shared via Flask.g."""

import os
import json
from dataclasses import dataclass
from typing import Any

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


@dataclass
class PreparedRequest:  # pylint: disable=too-many-instance-attributes
    """Core bootstrap object shared for the current request."""

    req: Any

    # initialized by build()
    schema: Any | None = None
    session: Any | None = None
    user: Any | None = None
    view: Any | None = None
    schema_data: dict | None = None
    schema_local_data: dict | None = None
    ajax_request: bool = False

    # routing/policy
    route_path: str = "/"
    policy: dict | None = None
    allowed_roles: list[str] | None = None
    route_require_auth: bool | None = None

    # access decision
    allowed: bool = False
    deny_status: int | None = None
    deny_reason: str | None = None
    component_bp: Any | None = None

    def build(self, component_bp=None, route="") -> "PreparedRequest":
        """Build all request-scoped core context."""
        self.component_bp = component_bp
        self.schema = Schema(self.req)
        self._set_current_comp(route, component_bp=component_bp)
        self._merge_bp_schema()

        self.schema_data = self.schema.properties["data"]
        self.schema_local_data = self.schema.properties["inherit"]["data"]
        self.ajax_request = bool(
            self.schema_data["CONTEXT"]["HEADERS"].get("Requested-With-Ajax")
        )
        self.session = Session(self.schema_data["CONTEXT"]["SESSION"])
        self.user = User()
        self.view = Template(self.schema)

        self._build_common()
        self._resolve_route_metadata(component_bp=component_bp, route=route)
        self._evaluate_core_policy()
        return self

    def set_route_context(self, route="", neutral_route=None, component_bp=None) -> "PreparedRequest":
        """Refresh route metadata and access decision for current request."""
        component_bp = component_bp or self.component_bp
        self._set_current_comp(route, neutral_route=neutral_route, component_bp=component_bp)
        self._resolve_route_metadata(component_bp=component_bp, route=route)
        self._evaluate_core_policy()
        return self

    def _merge_bp_schema(self) -> None:
        schema_path = self.schema.properties["data"]["CURRENT_BP_SCHEMA"]
        if schema_path:
            with open(schema_path, "r", encoding="utf-8") as file:
                merge_dict(self.schema.properties, json.load(file))

    def _set_current_comp(self, comp_route, neutral_route=None, component_bp=None) -> None:
        data = self.schema.properties["data"]
        normalized_comp_route = f"{Config.COMP_ROUTE_ROOT}/{comp_route or ''}".strip("/")
        data["CURRENT_COMP_ROUTE"] = normalized_comp_route

        data["CURRENT_COMP_ROUTE_SANITIZED"] = normalized_comp_route.replace("/", ":")
        data["CURRENT_NEUTRAL_ROUTE"] = (
            neutral_route
            or getattr(component_bp, "neutral_route", None)
            or data["CURRENT_NEUTRAL_ROUTE"]
        )

        name, uuid = self.extract_comp_from_path(data["CURRENT_NEUTRAL_ROUTE"])
        data["CURRENT_COMP_NAME"] = name
        data["CURRENT_COMP_UUID"] = uuid
        data["CURRENT_COMP_PATH"] = (
            os.path.join(Config.COMPONENT_DIR, name)
            if name
            else data.get("CURRENT_COMP_PATH")
        )
        data["CURRENT_BP_SCHEMA"] = data.get(uuid, {}).get("bp_schema", None) if uuid else None

    def _build_common(self) -> None:
        """Perform request bootstrap tasks reused by request handlers."""
        session_id, session_cookie = self.session.get()
        self.schema_data["CONTEXT"]["SESSION"] = session_id
        session_data = self.session.get_session_properties() if session_id else {}
        self.schema_data["CONTEXT"]["SESSION_DATA"] = (
            session_data if isinstance(session_data, dict) else {}
        )
        self.schema_data["CURRENT_USER"] = self._build_current_user(
            self.schema_data["CONTEXT"]["SESSION_DATA"]
        )
        self.schema_data["HAS_SESSION"] = "true" if session_id else None
        self.schema_data["HAS_SESSION_STR"] = "true" if session_id else "false"
        self.schema_data["CSP_NONCE"] = get_nonce()
        self._parse_utoken()
        self.schema_data["LTOKEN"] = ltoken_create(self.schema_data["CONTEXT"]["UTOKEN"])

        if not self.ajax_request:
            self._cookie_tab_changes()
            self.view.add_cookie(
                {
                    **session_cookie,
                    Config.THEME_KEY: {
                        "key": Config.THEME_KEY,
                        "value": self.schema_local_data["current"]["theme"]["theme"],
                    },
                    Config.THEME_COLOR_KEY: {
                        "key": Config.THEME_COLOR_KEY,
                        "value": self.schema_local_data["current"]["theme"]["color"],
                    },
                    Config.LANG_KEY: {
                        "key": Config.LANG_KEY,
                        "value": self.schema.properties["inherit"]["locale"]["current"],
                    },
                }
            )

    def _build_current_user(self, session_data: dict) -> dict:
        current_user = {
            "auth": False,
            "id": "",
            "roles": {},
            "status": {},
            "profile": {
                "id": "",
                "alias": "",
                "locale": "",
                "status": {},
            },
        }

        if not isinstance(session_data, dict):
            return current_user

        user_data = session_data.get("user_data", {})
        if not isinstance(user_data, dict):
            return current_user

        user_id = str(user_data.get("userId") or "")
        if not user_id:
            return current_user

        current_user["auth"] = True
        current_user["id"] = user_id

        roles = user_data.get("roles", [])
        if user_id:
            db_roles = self.user.get_roles(user_id)
            if db_roles:
                roles = db_roles

        role_map = {}
        for role in roles:
            role_code = str(role).strip().lower()
            if role_code:
                role_key = f"role_{role_code}"
                role_map[role_key] = role_key
        current_user["roles"] = role_map

        user_disabled = user_data.get("user_disabled", {})
        if isinstance(user_disabled, dict):
            current_user["status"] = {
                str(key): "true"
                for key, value in user_disabled.items()
                if str(key).strip() and str(value).strip()
            }

        current_user["profile"]["id"] = str(user_data.get("profileId") or "")
        current_user["profile"]["alias"] = str(user_data.get("alias") or "")
        current_user["profile"]["locale"] = str(user_data.get("locale") or "")
        profile_disabled = user_data.get("profile_disabled", {})
        if isinstance(profile_disabled, dict):
            current_user["profile"]["status"] = {
                str(key): "true"
                for key, value in profile_disabled.items()
                if str(key).strip() and str(value).strip()
            }

        return current_user

    def _cookie_tab_changes(self) -> None:
        detect = "start"
        detect += self.schema_data["CONTEXT"].get("UTOKEN") or "none"
        detect += self.schema_data["CONTEXT"].get("SESSION") or "none"
        self.view.add_cookie(
            {
                Config.TAB_CHANGES_KEY: {
                    "key": Config.TAB_CHANGES_KEY,
                    "value": sbase64url_md5(detect),
                }
            }
        )

    def _parse_utoken(self) -> None:
        if self.req.method == "GET" and not self.ajax_request:
            utoken_token, utoken_cookie = utoken_update(
                self.req.cookies.get(Config.UTOKEN_KEY)
            )
        else:
            utoken_token, utoken_cookie = utoken_extract(
                self.req.cookies.get(Config.UTOKEN_KEY)
            )

        self.schema_data["CONTEXT"]["UTOKEN"] = utoken_token
        if not self.ajax_request:
            self.view.add_cookie({**utoken_cookie})

    def _resolve_route_metadata(self, component_bp=None, route="") -> None:
        self.route_path = self._normalize_route_path(route)
        self.policy = None
        self.allowed_roles = None
        self.route_require_auth = None

        # Security policy is resolved from request schema data (single source in runtime).
        component_uuid = (self.schema_data or {}).get("CURRENT_COMP_UUID")
        if not component_uuid:
            return

        component_data = (self.schema_data or {}).get(component_uuid, {})
        manifest = component_data.get("manifest", {}) if isinstance(component_data, dict) else {}
        security = manifest.get("security") if isinstance(manifest, dict) else None
        self.policy = security if isinstance(security, dict) else {}
        if not isinstance(self.policy, dict):
            return

        routes_auth = self.policy.get("routes_auth")
        matched_require_auth = self._resolve_policy_by_prefix(
            self.route_path,
            routes_auth if isinstance(routes_auth, dict) else None,
            expected_type=bool,
        )
        if isinstance(matched_require_auth, bool):
            self.route_require_auth = matched_require_auth

        routes_role = self.policy.get("routes_role")
        matched_roles = self._resolve_policy_by_prefix(
            self.route_path,
            routes_role if isinstance(routes_role, dict) else None,
            expected_type=list,
        )
        if isinstance(matched_roles, list):
            self.allowed_roles = [
                str(role).strip().lower()
                for role in matched_roles
                if str(role).strip()
            ]

    def _evaluate_core_policy(self) -> None:
        self.allowed = False
        self.deny_status = None
        self.deny_reason = None

        # Non-component requests are not evaluated with component manifest policy.
        if self.policy is None:
            self.allowed = True
            return

        if not isinstance(self.policy, dict):
            self.deny_status = 403
            self.deny_reason = "invalid_security_policy"
            return

        routes_auth = self.policy.get("routes_auth")
        if not isinstance(routes_auth, dict):
            self.deny_status = 403
            self.deny_reason = "missing_routes_auth_policy"
            return

        routes_role = self.policy.get("routes_role")
        if not isinstance(routes_role, dict):
            self.deny_status = 403
            self.deny_reason = "missing_routes_role_policy"
            return

        if self.allowed_roles is None:
            self.deny_status = 403
            self.deny_reason = "route_not_mapped_in_policy"
            return

        if not self.allowed_roles:
            self.deny_status = 403
            self.deny_reason = "empty_roles_policy"
            return

        if "*" in self.allowed_roles and len(self.allowed_roles) > 1:
            self.deny_status = 403
            self.deny_reason = "invalid_roles_policy_wildcard_mixed"
            return

        # 1) Authentication (route-level policy)
        if self.route_require_auth is None:
            self.deny_status = 403
            self.deny_reason = "route_not_mapped_in_auth_policy"
            return

        require_auth = self.route_require_auth

        is_auth = bool(self.schema_data["CURRENT_USER"].get("auth"))
        if require_auth and not is_auth:
            self.deny_status = 401
            self.deny_reason = "auth_required"
            return

        # 2) Status restrictions (core)
        restricted_reason = self._get_restricted_status_reason()
        if restricted_reason:
            self.deny_status = 403
            self.deny_reason = restricted_reason
            return

        # 3) Role policy
        if "*" in self.allowed_roles:
            self.allowed = True
            return

        role_map = self.schema_data["CURRENT_USER"].get("roles", {})
        current_roles = {
            str(key).replace("role_", "", 1).strip().lower()
            for key in role_map.keys()
            if str(key).startswith("role_")
        }
        if not current_roles.intersection(set(self.allowed_roles)):
            self.deny_status = 403
            self.deny_reason = "role_not_allowed"
            return

        self.allowed = True

    def _get_restricted_status_reason(self) -> str | None:
        """Return deny reason if current user/profile is in restricted status."""
        current_user = self.schema_data.get("CURRENT_USER", {})
        user_status = current_user.get("status", {})
        profile_status = current_user.get("profile", {}).get("status", {})

        if not isinstance(user_status, dict):
            user_status = {}
        if not isinstance(profile_status, dict):
            profile_status = {}

        # Deleted users are always blocked.
        if DELETED in user_status:
            return "user_status_deleted"

        # Any remaining status flag is treated as restricted by core policy.
        if user_status:
            return "user_status_restricted"

        if profile_status:
            return "profile_status_restricted"

        return None

    @staticmethod
    def _normalize_route_path(route) -> str:
        path = (route or "").strip()
        if not path:
            return "/"
        if not path.startswith("/"):
            path = f"/{path}"
        if len(path) > 1:
            path = path.rstrip("/")
            if not path:
                return "/"
        return path

    @staticmethod
    def _route_matches_prefix(route_path: str, prefix_path: str) -> bool:
        """Prefix matching with segment boundary (except root, which matches all)."""
        if prefix_path == "/":
            return True
        return route_path == prefix_path or route_path.startswith(f"{prefix_path}/")

    def _resolve_policy_by_prefix(self, route_path: str, mapping: dict | None, expected_type: type):
        """Return best policy match by prefix (most specific wins)."""
        if not isinstance(mapping, dict):
            return None

        matched_prefix = None
        matched_value = None

        for prefix, value in mapping.items():
            normalized_prefix = self._normalize_route_path(prefix)
            if not self._route_matches_prefix(route_path, normalized_prefix):
                continue
            if not isinstance(value, expected_type):
                continue
            if matched_prefix is None or len(normalized_prefix) > len(matched_prefix):
                matched_prefix = normalized_prefix
                matched_value = value

        return matched_value

    def extract_comp_from_path(self, path) -> tuple[str | None, str | None]:
        if "/component/cmp_" in path:
            part = path.split("component/cmp_")[1]
            name = "cmp_" + part.split("/")[0]
        else:
            return None, None

        uuid = self.schema.properties["data"]["COMPONENTS_MAP_BY_NAME"].get(name)
        return name, uuid
