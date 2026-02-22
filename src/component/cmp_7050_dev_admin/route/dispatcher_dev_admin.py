"""Dispatcher for dev admin component routes."""

import hmac
import ipaddress
import json
import secrets
import time

from flask import Response, abort, current_app, request, session

from app.config_db import (
    ensure_config_db,
    get_component_custom_entry,
    list_component_custom_entries,
    upsert_component_custom_override,
)
from constants import UUID_MAX_LEN, UUID_MIN_LEN
from core.dispatcher import Dispatcher
from utils.utils import get_ip

_AUTH_SESSION_KEY = "DEV_ADMIN_AUTH"
_CSRF_SESSION_KEY = "DEV_ADMIN_CSRF"
_UUID_ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_")
_LOGIN_WINDOW_SECONDS = 300
_LOGIN_MAX_ATTEMPTS = 10
_LOGIN_ATTEMPTS = {}


class DispatcherDevAdmin(Dispatcher):
    """Dev Admin route dispatcher."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None):
        self._raw_route = comp_route
        super().__init__(req, comp_route, neutral_route, ltoken)

    @staticmethod
    def _is_valid_comp_uuid(comp_uuid):
        if not isinstance(comp_uuid, str):
            return False
        if len(comp_uuid) < UUID_MIN_LEN or len(comp_uuid) > UUID_MAX_LEN:
            return False
        if "_" not in comp_uuid:
            return False
        return all(char in _UUID_ALLOWED_CHARS for char in comp_uuid)

    @staticmethod
    def _is_allowed_ip(remote_addr):
        try:
            remote_ip = ipaddress.ip_address((remote_addr or "").strip())
        except ValueError:
            return False

        if current_app.config.get("DEV_ADMIN_LOCAL_ONLY", True) and not remote_ip.is_loopback:
            return False

        allowed = current_app.config.get("DEV_ADMIN_ALLOWED_IPS", [])
        if not allowed:
            return True

        for item in allowed:
            value = (item or "").strip()
            if not value:
                continue
            try:
                network = ipaddress.ip_network(value, strict=False)
                if remote_ip in network:
                    return True
                continue
            except ValueError:
                pass
            try:
                if remote_ip == ipaddress.ip_address(value):
                    return True
            except ValueError:
                continue

        return False

    @staticmethod
    def _credentials_ready():
        return bool(
            current_app.config.get("DEV_ADMIN_USER", "")
            and current_app.config.get("DEV_ADMIN_PASSWORD", "")
        )

    @staticmethod
    def _auth_ok():
        return bool(session.get(_AUTH_SESSION_KEY))

    @staticmethod
    def _ensure_csrf_token():
        token = session.get(_CSRF_SESSION_KEY)
        if not token:
            token = secrets.token_urlsafe(32)
            session[_CSRF_SESSION_KEY] = token
        return token

    @staticmethod
    def _csrf_valid():
        posted = request.form.get("csrf_token", "")
        current = session.get(_CSRF_SESSION_KEY, "")
        if not posted or not current:
            return False
        return hmac.compare_digest(posted, current)

    @staticmethod
    def _login_rate_limited(client_ip):
        now = int(time.time())
        entries = _LOGIN_ATTEMPTS.get(client_ip, [])
        entries = [ts for ts in entries if now - ts <= _LOGIN_WINDOW_SECONDS]
        _LOGIN_ATTEMPTS[client_ip] = entries
        return len(entries) >= _LOGIN_MAX_ATTEMPTS

    @staticmethod
    def _register_login_failure(client_ip):
        now = int(time.time())
        entries = _LOGIN_ATTEMPTS.get(client_ip, [])
        entries = [ts for ts in entries if now - ts <= _LOGIN_WINDOW_SECONDS]
        entries.append(now)
        _LOGIN_ATTEMPTS[client_ip] = entries

    @staticmethod
    def _clear_login_failures(client_ip):
        _LOGIN_ATTEMPTS.pop(client_ip, None)

    def _build_initial_state(self):
        return {
            "auth_ok": False,
            "message": None,
            "error": None,
            "entries": [],
            "edit_uuid": "",
            "edit_json": '{\n    "manifest": {},\n    "schema": {}\n}',
            "edit_enabled": True,
            "csrf_token": "",
            "component_uuids": sorted(self.schema_data.get("COMPONENTS_MAP_BY_UUID", {}).keys()),
        }

    def _handle_auth_action(self, state, action, client_ip):
        if request.method == "POST" and action == "logout":
            session.pop(_AUTH_SESSION_KEY, None)

        if request.method == "POST" and action == "login" and not self._auth_ok():
            if self._login_rate_limited(client_ip):
                state["error"] = "Too many login attempts. Try again later."
                return

            username = request.form.get("username", "")
            password = request.form.get("password", "")

            user_ok = hmac.compare_digest(username, current_app.config["DEV_ADMIN_USER"])
            pass_ok = hmac.compare_digest(password, current_app.config["DEV_ADMIN_PASSWORD"])

            if user_ok and pass_ok:
                session[_AUTH_SESSION_KEY] = str(int(time.time()))
                self._clear_login_failures(client_ip)
                state["message"] = "Login successful."
            else:
                self._register_login_failure(client_ip)
                state["error"] = "Invalid credentials."

    def _handle_save_action(self, state, action, db_path):
        edit_uuid = (request.args.get("edit_uuid") or "").strip()

        if state["auth_ok"]:
            if request.method == "POST" and action == "save":
                edit_uuid = (request.form.get("comp_uuid") or "").strip()
                raw_json = request.form.get("override_json") or ""
                enabled = (request.form.get("enabled") or "") == "1"
                state["edit_uuid"] = edit_uuid
                state["edit_json"] = raw_json
                state["edit_enabled"] = enabled

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
                            state["edit_json"] = json.dumps(
                                payload, ensure_ascii=False, indent=4
                            )
                    except json.JSONDecodeError:
                        state["error"] = "Override JSON must be a JSON object."

            if edit_uuid and not state["edit_uuid"]:
                state["edit_uuid"] = edit_uuid
                entry = get_component_custom_entry(
                    db_path, edit_uuid, debug=current_app.debug
                )
                if entry is not None:
                    state["edit_enabled"] = bool(entry["enabled"])
                    try:
                        state["edit_json"] = json.dumps(
                            json.loads(entry["value_json"]), ensure_ascii=False, indent=4
                        )
                    except json.JSONDecodeError:
                        state["edit_json"] = entry["value_json"]

            state["entries"] = list_component_custom_entries(db_path, debug=current_app.debug)

    def render_route(self) -> Response:
        """Execute dev admin route logic and render."""
        client_ip = get_ip()
        if not self._is_allowed_ip(client_ip):
            abort(403)

        state = self._build_initial_state()
        state["csrf_token"] = self._ensure_csrf_token()
        db_path = current_app.config["CONFIG_DB_PATH"]

        if not ensure_config_db(db_path, debug=current_app.debug):
            state["error"] = "config.db is not available."
            self.schema_data["dev_admin"] = state
            return self.view.render()

        if not self._credentials_ready():
            state["error"] = (
                "Credentials are not configured. Set DEV_ADMIN_USER and "
                "DEV_ADMIN_PASSWORD in config/.env."
            )
            self.schema_data["dev_admin"] = state
            return self.view.render()

        action = (request.form.get("action") or "").strip()
        protected_actions = {"login", "logout", "save"}

        if request.method == "POST" and action in protected_actions and not self._csrf_valid():
            state["error"] = "Invalid CSRF token."
            self.schema_data["dev_admin"] = state
            return self.view.render()

        self._handle_auth_action(state, action, client_ip)
        state["auth_ok"] = self._auth_ok()

        current = (self._raw_route or "").strip("/")
        if current == "":
            self._handle_save_action(state, action, db_path)

        self.schema_data["dev_admin"] = state
        return self.view.render()
