"""Dispatcher for local-admin component routes."""

import hmac
import secrets

from flask import Response, abort, request, session

from core.dispatcher import Dispatcher
from core.session_dev import SessionDev
from utils.utils import get_ip


class DispatcherLocalAdmin(Dispatcher):
    """Local Admin route dispatcher."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None):
        self._cookie_updates = []
        self._raw_route = (comp_route or "").strip("/")
        self._session_dev = None  # Will be created on first use
        super().__init__(req, comp_route, neutral_route, ltoken)

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
            "dev_admin_role": "true" if auth_ok else None,
            "is_ajax": bool(self.ajax_request),
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
            state["error"] = "Session dev not available."
            return

        if session_dev._login_rate_limited(client_ip):
            state["error"] = "Too many login attempts. Try again later."
            return

        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

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
        state["dev_admin_role"] = "true"
        state["message"] = "Login successful."

    def _handle_logout(self, state):
        session_dev = self._get_session_dev()
        if session_dev:
            cookies = session_dev.delete_session()
            for _key, cookie_data in cookies.items():
                self._cookie_updates.append(cookie_data)

        state["auth_ok"] = False
        state["dev_admin_role"] = None
        state["message"] = "Session closed."

    def _handle_post(self, state, client_ip, user_agent):
        action = (request.form.get("action") or "").strip()
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

    def render_route(self) -> Response:
        """Execute route logic and render response."""
        session_dev = self._get_session_dev()

        if not session_dev:
            abort(500, "Session dev not initialized")

        client_ip = get_ip()
        if not session_dev.check_ip_allowed():
            abort(403)

        user_agent = request.headers.get("User-Agent", "")
        auth_ok = session_dev.check_session()

        state = self._build_initial_state(auth_ok)
        state["csrf_token"] = self._ensure_csrf_token()

        if request.method == "POST":
            self._handle_post(state, client_ip, user_agent)

        session_dev = self._get_session_dev()
        if session_dev and not session_dev.are_credentials_ready():
            if self._raw_route.startswith("login") or self._raw_route == "logout/ajax":
                state["error"] = (
                    "Credentials are not configured. Set DEV_ADMIN_USER and DEV_ADMIN_PASSWORD in config/.env."
                )

        self.schema_data["local_admin"] = state
        self.schema_data["dev_admin_role"] = state["dev_admin_role"]

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
