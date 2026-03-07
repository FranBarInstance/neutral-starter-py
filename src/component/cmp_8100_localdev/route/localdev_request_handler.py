"""Request handler for local-admin component routes."""

import hmac
import json
import secrets

from flask import Response, current_app, request, session

from app.config_db import (
    delete_component_custom_override,
    ensure_config_db,
    get_component_custom_entry,
    list_component_custom_entries,
    upsert_component_custom_override,
)
from constants import UUID_MAX_LEN, UUID_MIN_LEN
from core.request_handler import RequestHandler
from core.session_dev import SessionDev
from utils.utils import get_ip

_UUID_ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_")


class LocalDevRequestHandler(RequestHandler):
    """Local Admin route request handler."""

    _PUBLIC_ROUTES = {"", "login", "login/ajax", "logout/ajax"}

    def __init__(self, prepared_request, comp_route: str = "", neutral_route: str | None = None):
        self._cookie_updates = []
        self._raw_route = (comp_route or "").strip("/")
        self._session_dev = None  # Will be created on first use
        super().__init__(prepared_request, comp_route, neutral_route)

    def _get_session_dev(self):
        """Get or create SessionDev instance."""
        if self._session_dev is None:
            self._session_dev = SessionDev()
        return self._session_dev

    @staticmethod
    def _ensure_csrf_token():
        csrf_key = SessionDev.get_csrf_session_key()
        token = session.get(csrf_key)
        if not token:
            token = secrets.token_urlsafe(48)
            session[csrf_key] = token
        return token

    @staticmethod
    def _csrf_valid():
        posted = request.form.get("csrf_token", "")
        current = session.get(SessionDev.get_csrf_session_key(), "")
        if not posted or not current:
            return False
        return hmac.compare_digest(posted, current)

    def _apply_cookie_updates(self, response):
        for cookie_data in self._cookie_updates:
            response.set_cookie(**cookie_data)

    def _build_initial_state(self, auth_ok):
        return {
            "auth_ok": auth_ok,
            "csrf_token": "",
            "message": None,
            "error": None,
            "localdev_role": "true" if auth_ok else None,
            "is_ajax": bool(self.ajax_request),
            "custom_entries": [],
            "custom_edit_uuid": "",
            "custom_edit_json": '{\n    "manifest": {},\n    "schema": {}\n}',
            "custom_edit_enabled": True,
            "component_uuids": [
                {
                    "uuid": uuid,
                    "name": self.schema_data.get("COMPONENTS_MAP_BY_UUID", {}).get(uuid, "")
                }
                for uuid in sorted(self.schema_data.get("COMPONENTS_MAP_BY_UUID", {}).keys())
            ],
        }

    def _current_auth_status(self):
        """Get current auth status using SessionDev from schema."""
        session_dev = self._get_session_dev()
        if session_dev:
            return session_dev.check_session()
        return False

    def _handle_login(self, state, client_ip, _user_agent):
        """Handle login form submission. _user_agent is required by SessionDev."""
        # pylint: disable=protected-access
        session_dev = self._get_session_dev()
        if not session_dev:
            state["error"] = "Localdev session is not available."
            return

        if session_dev._login_rate_limited(client_ip):
            state["error"] = "Too many login attempts. Try again later."
            return

        username = (self.req.form.get("username") or "").strip()
        password = self.req.form.get("password") or ""

        if len(username) > 128 or len(password) > 256:
            session_dev._register_login_failure(client_ip)
            state["error"] = "Invalid credentials."
            return

        if not session_dev.validate_credentials(username, password):
            session_dev._register_login_failure(client_ip)
            state["error"] = "Invalid credentials."
            return

        session_dev._clear_login_failures(client_ip)

        # Create session cookies
        cookies = session_dev.create_session()
        for _key, cookie_data in cookies.items():
            self._cookie_updates.append(cookie_data)

        state["auth_ok"] = True
        state["localdev_role"] = "true"
        state["message"] = "Login successful."

    def _handle_logout(self, state):
        session_dev = self._get_session_dev()
        if session_dev:
            cookies = session_dev.delete_session()
            for _key, cookie_data in cookies.items():
                self._cookie_updates.append(cookie_data)

        state["auth_ok"] = False
        state["localdev_role"] = None
        state["message"] = "Session closed."

    def _handle_post(self, state, client_ip, user_agent):
        action = (self.req.form.get("action") or "").strip()
        if self._raw_route == "logout/ajax":
            action = "logout"
        if action not in {"login", "logout"}:
            state["error"] = "Invalid action."
            return

        if not self._csrf_valid():
            state["error"] = "Invalid CSRF token."
            return

        if action == "logout":
            self._handle_logout(state)
            return

        if state["auth_ok"]:
            state["message"] = "Session already active."
            return

        session_dev = self._get_session_dev()
        if not session_dev or not session_dev.are_credentials_ready():
            state["error"] = (
                "Credentials are not configured. Set DEV_ADMIN_USER and DEV_ADMIN_PASSWORD in config/.env."
            )
            return

        self._handle_login(state, client_ip, user_agent)

    @staticmethod
    def _is_valid_comp_uuid(comp_uuid):
        if not isinstance(comp_uuid, str):
            return False
        if len(comp_uuid) < UUID_MIN_LEN or len(comp_uuid) > UUID_MAX_LEN:
            return False
        if "_" not in comp_uuid:
            return False
        return all(char in _UUID_ALLOWED_CHARS for char in comp_uuid)

    def _handle_custom_route(self, state, action):
        db_path = current_app.config["CONFIG_DB_PATH"]
        if not ensure_config_db(db_path, debug=current_app.debug):
            state["error"] = "config.db is not available."
            return

        if not state["auth_ok"]:
            return

        edit_uuid = (self.req.args.get("edit_uuid") or "").strip()

        if self.req.method == "POST" and action == "save":
            edit_uuid = (self.req.form.get("comp_uuid") or "").strip()
            raw_json = self.req.form.get("override_json") or ""
            enabled = (self.req.form.get("enabled") or "") == "1"

            state["custom_edit_uuid"] = edit_uuid
            state["custom_edit_json"] = raw_json
            state["custom_edit_enabled"] = enabled

            if not self._is_valid_comp_uuid(edit_uuid):
                state["error"] = "comp_uuid format is invalid."
            elif edit_uuid not in self.schema_data.get("COMPONENTS_MAP_BY_UUID", {}):
                state["error"] = "Selected UUID does not exist in loaded components."
            else:
                try:
                    payload = json.loads(raw_json)
                    if not isinstance(payload, dict):
                        state["error"] = "Override JSON must be a JSON object."
                    else:
                        upsert_component_custom_override(
                            db_path, edit_uuid, payload, enabled=enabled
                        )
                        state["message"] = "Override saved."
                        state["custom_edit_json"] = json.dumps(
                            payload, ensure_ascii=False, indent=4
                        )
                except json.JSONDecodeError:
                    state["error"] = "Override JSON must be a JSON object."

        if self.req.method == "POST" and action == "delete":
            delete_uuid = (self.req.form.get("comp_uuid") or "").strip()

            if not self._is_valid_comp_uuid(delete_uuid):
                state["error"] = "comp_uuid format is invalid."
            else:
                deleted = delete_component_custom_override(db_path, delete_uuid)
                if deleted:
                    state["message"] = "Override deleted."
                    # Clear edit fields after delete
                    state["custom_edit_uuid"] = ""
                    state["custom_edit_json"] = '{\n    "manifest": {},\n    "schema": {}\n}'
                    state["custom_edit_enabled"] = True
                else:
                    state["error"] = "Failed to delete override."

        if edit_uuid and edit_uuid != state.get("custom_edit_uuid", ""):
            state["custom_edit_uuid"] = edit_uuid
            entry = get_component_custom_entry(
                db_path, edit_uuid, debug=current_app.debug
            )
            if entry is not None:
                state["custom_edit_enabled"] = bool(entry["enabled"])
                try:
                    state["custom_edit_json"] = json.dumps(
                        json.loads(entry["value_json"]), ensure_ascii=False, indent=4
                    )
                except json.JSONDecodeError:
                    state["custom_edit_json"] = entry["value_json"]

        state["custom_entries"] = list_component_custom_entries(
            db_path, debug=current_app.debug
        )

    def _render_http_error(self, status_code, status_text, status_param):
        """Render Neutral custom HTTP error page."""
        return self.view.render_error(status_code, status_text, status_param)

    def render_route(self) -> Response:
        """Execute route logic and render response."""
        session_dev = self._get_session_dev()

        if not session_dev:
            return self._render_http_error(
                500, "Internal Server Error", "Localdev session not initialized"
            )

        client_ip = get_ip()
        if not session_dev.check_ip_allowed():
            return self._render_http_error(
                403, "Forbidden", "Access allowed only from configured local IPs."
            )

        user_agent = self.req.headers.get("User-Agent", "")
        auth_ok = session_dev.check_session()
        if self._raw_route not in self._PUBLIC_ROUTES and not auth_ok:
            return self._render_http_error(
                403, "Forbidden", "Local admin session required."
            )

        state = self._build_initial_state(auth_ok)
        state["csrf_token"] = self._ensure_csrf_token()

        action = (self.req.form.get("action") or "").strip()
        custom_route_processed = False
        if self.req.method == "POST":
            if self._raw_route == "custom":
                if action in ("save", "delete"):
                    if not self._csrf_valid():
                        state["error"] = "Invalid CSRF token."
                    else:
                        self._handle_custom_route(state, action)
                    custom_route_processed = True
                else:
                    state["error"] = "Invalid action."
                    custom_route_processed = True
            else:
                self._handle_post(state, client_ip, user_agent)

        if self._raw_route == "custom" and not custom_route_processed:
            self._handle_custom_route(state, action)

        session_dev = self._get_session_dev()
        if session_dev and not session_dev.are_credentials_ready():
            if self._raw_route.startswith("login") or self._raw_route == "logout/ajax":
                state["error"] = (
                    "Credentials are not configured. Set DEV_ADMIN_USER and DEV_ADMIN_PASSWORD in config/.env."
                )

        self.schema_data["local_admin"] = state
        self.schema_data["localdev_role"] = state["localdev_role"]

        response = self.view.render(
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
            }
        )
        self._apply_cookie_updates(response)
        return response
