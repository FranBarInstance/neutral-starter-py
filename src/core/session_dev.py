"""Local admin session management module - without database."""

import base64
import hashlib
import hmac
import json
import secrets
import time

from flask import current_app, request
from utils.utils import get_ip


class SessionDev:
    """Local admin session manager - credentials from Config, no database."""

    # Default cookie names (can be overridden in config/.env)
    _AUTH_COOKIE_KEY = "DEV_ADMIN_SESSION"
    _ROLE_COOKIE_KEY = "dev_admin_role"
    _CSRF_SESSION_KEY = "DEV_ADMIN_CSRF"

    @staticmethod
    def get_auth_cookie_key():
        """Auth cookie name from config or default."""
        return current_app.config.get("DEV_ADMIN_AUTH_COOKIE_KEY", SessionDev._AUTH_COOKIE_KEY)

    @staticmethod
    def get_role_cookie_key():
        """Role cookie name from config or default."""
        return current_app.config.get("DEV_ADMIN_ROLE_COOKIE_KEY", SessionDev._ROLE_COOKIE_KEY)

    @staticmethod
    def get_csrf_session_key():
        """CSRF session key from config or default."""
        return current_app.config.get("DEV_ADMIN_CSRF_SESSION_KEY", SessionDev._CSRF_SESSION_KEY)
    _LOGIN_WINDOW_SECONDS = 300
    _LOGIN_MAX_ATTEMPTS = 7
    _LOGIN_ATTEMPTS = {}

    def __init__(self):
        self._cookie_updates = []
        self.now = int(time.time())
        self._client_ip = get_ip()

    # === Config getters (from .env) ===

    @staticmethod
    def _credentials_ready():
        return bool(
            current_app.config.get("DEV_ADMIN_USER")
        ) and bool(
            current_app.config.get("DEV_ADMIN_PASSWORD")
        )

    @staticmethod
    def _get_expected_user():
        return str(current_app.config.get("DEV_ADMIN_USER", ""))

    @staticmethod
    def _get_expected_password():
        return str(current_app.config.get("DEV_ADMIN_PASSWORD", ""))

    # === IP validation ===

    @staticmethod
    def _is_allowed_ip(remote_addr):
        import ipaddress  # pylint: disable=import-outside-toplevel
        try:
            remote_ip = ipaddress.ip_address((remote_addr or "").strip())
        except ValueError:
            return False

        allowed = current_app.config.get(
            "DEV_ADMIN_ALLOWED_IPS",
            ["127.0.0.1", "::1", "192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]
        )
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

    # === Cookie validation (from dispatcher_devadm.py) ===

    def _auth_secret(self):
        app_secret = str(current_app.config.get("SECRET_KEY") or "")
        if not app_secret:
            raise RuntimeError(
                "SECRET_KEY is not configured. "
                "Set a secure SECRET_KEY in config/.env to start the application."
            )
        return hashlib.sha256((app_secret + "::dev-admin").encode("utf-8")).digest()

    def _hash_client_value(self, raw_value):
        return hashlib.sha256((raw_value or "").encode("utf-8")).hexdigest()

    def _b64url_encode(self, raw_bytes):
        return base64.urlsafe_b64encode(raw_bytes).rstrip(b"=").decode("ascii")

    def _b64url_decode(self, raw_str):
        missing = (-len(raw_str)) % 4
        return base64.urlsafe_b64decode(raw_str + ("=" * missing))

    def _is_auth_cookie_valid(self, token):
        """Validate auth token. Multiple returns are intentional for security checks."""
        # pylint: disable=too-many-return-statements
        if not token or "." not in token:
            return False

        payload_b64, signature_b64 = token.split(".", 1)
        expected_signature = hmac.new(
            self._auth_secret(),
            payload_b64.encode("ascii"),
            hashlib.sha256,
        ).digest()

        try:
            provided_signature = self._b64url_decode(signature_b64)
        except (ValueError, TypeError):
            return False

        if not hmac.compare_digest(provided_signature, expected_signature):
            return False

        try:
            payload = json.loads(self._b64url_decode(payload_b64).decode("utf-8"))
        except (ValueError, TypeError, json.JSONDecodeError):
            return False

        now = int(time.time())
        exp = int(payload.get("exp") or 0)
        iat = int(payload.get("iat") or 0)

        if exp <= now or iat <= 0 or iat > (now + 60):
            return False

        if payload.get("cip") != self._hash_client_value(self._client_ip):
            return False

        return True

    # === Public API for schema.py ===

    def check_session(self):
        """Check if local admin session is valid. Returns bool."""
        token = request.cookies.get(self.get_auth_cookie_key(), "")
        return self._is_auth_cookie_valid(token)

    def check_ip_allowed(self):
        """Check if current IP is allowed for dev admin."""
        return self._is_allowed_ip(self._client_ip)

    def are_credentials_ready(self):
        """Check if credentials are configured in .env."""
        return self._credentials_ready()

    def get_expected_user(self):
        """Get expected username from config."""
        return self._get_expected_user()

    def get_expected_password(self):
        """Get expected password from config."""
        return self._get_expected_password()

    def get_session_data(self):
        """Return session data for templates."""
        return {
            "session_dev": self.check_session(),
            "auth_cookie": self.get_auth_cookie_key(),
            "role_cookie": self.get_role_cookie_key(),
        }

    # === For component: login/logout ===

    def _cookie_settings(self):
        max_age = int(current_app.config.get("DEV_ADMIN_SESSION_MAX_AGE", 1800))
        secure = bool(current_app.config.get("DEV_ADMIN_COOKIE_SECURE", True))
        return {
            "path": "/",
            "secure": secure,
            "httponly": True,
            "samesite": "Strict",
            "max_age": max_age,
        }

    def _create_auth_token(self):
        now = int(time.time())
        max_age = self._cookie_settings()["max_age"]
        payload = {
            "iat": now,
            "exp": now + max_age,
            "cip": self._hash_client_value(self._client_ip),
            "nonce": secrets.token_urlsafe(18),
        }

        payload_raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        payload_b64 = self._b64url_encode(payload_raw)
        signature = hmac.new(
            self._auth_secret(),
            payload_b64.encode("ascii"),
            hashlib.sha256,
        ).digest()
        signature_b64 = self._b64url_encode(signature)
        return f"{payload_b64}.{signature_b64}"

    def create_session(self):
        """Create dev session - returns cookie dict."""
        token = self._create_auth_token()
        settings = self._cookie_settings()
        auth_key = self.get_auth_cookie_key()
        role_key = self.get_role_cookie_key()

        return {
            auth_key: {
                "key": auth_key,
                "value": token,
                **settings,
            },
            role_key: {
                "key": role_key,
                "value": "true",
                **settings,
            }
        }

    def delete_session(self):
        """Delete dev session - returns cookie dict."""
        settings = self._cookie_settings()
        settings["max_age"] = 0
        auth_key = self.get_auth_cookie_key()
        role_key = self.get_role_cookie_key()

        return {
            auth_key: {
                "key": auth_key,
                "value": "",
                **settings,
            },
            role_key: {
                "key": role_key,
                "value": "",
                **settings,
            }
        }

    @staticmethod
    def validate_credentials(username, password):
        """Validate username/password against Config."""
        user_ok = hmac.compare_digest(username, SessionDev._get_expected_user())
        pass_ok = hmac.compare_digest(password, SessionDev._get_expected_password())
        return user_ok and pass_ok

    # === Rate limiting ===

    @staticmethod
    def _login_rate_limited(client_ip):
        now = int(time.time())
        entries = SessionDev._LOGIN_ATTEMPTS.get(client_ip, [])
        entries = [ts for ts in entries if now - ts <= SessionDev._LOGIN_WINDOW_SECONDS]
        SessionDev._LOGIN_ATTEMPTS[client_ip] = entries
        return len(entries) >= SessionDev._LOGIN_MAX_ATTEMPTS

    @staticmethod
    def _register_login_failure(client_ip):
        now = int(time.time())
        entries = SessionDev._LOGIN_ATTEMPTS.get(client_ip, [])
        entries = [ts for ts in entries if now - ts <= SessionDev._LOGIN_WINDOW_SECONDS]
        entries.append(now)
        SessionDev._LOGIN_ATTEMPTS[client_ip] = entries

    @staticmethod
    def _clear_login_failures(client_ip):
        SessionDev._LOGIN_ATTEMPTS.pop(client_ip, None)
