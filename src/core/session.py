"""Session management module."""

import json
import secrets
import time

from app.config import Config
from constants import SECONDS_MINUTE
from .model import Model


class Session:
    """session"""

    def __init__(self, session_id, db_url=Config.DB_SAFE, db_type=Config.DB_SAFE_TYPE):
        """session"""
        self.model = Model(db_url, db_type)
        self._session_id = session_id
        self.now = int(time.time())

    def get(self) -> tuple[str | None, dict]:
        """get session"""
        if not self._session_id:
            return None, {}

        result = self.model.exec('session', 'get', {
            "sessionId": self._session_id,
            "open": Config.SESSION_OPEN['true'],
            "now": self.now
        })

        if not result or not result.get('rows') or not result['rows'][0]:
            return None, {}

        modified = result['rows'][0][4]
        expire = result['rows'][0][5]

        # Update session if modified more than 15 minutes ago
        if (self.now - modified) > (SECONDS_MINUTE * 15):
            session_cookie = self.update(self._session_id)
            return self._session_id, session_cookie

        return self._session_id, self.create_session_cookie(self._session_id, max(0, expire - self.now))

    def get_session_properties(self) -> dict:
        """Return stored session properties for current session, if any."""
        if not self._session_id:
            return {}

        result = self.model.exec('session', 'get', {
            "sessionId": self._session_id,
            "open": Config.SESSION_OPEN['true'],
            "now": self.now
        })

        if not result or not result.get('rows') or not result['rows'][0]:
            return {}

        raw = result['rows'][0][3]
        if not raw:
            return {}

        try:
            props = json.loads(raw)
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}

        return props if isinstance(props, dict) else {}

    def close(self) -> dict:
        """close session"""
        if self._session_id:
            result = self.model.exec('session', 'get', {
                "sessionId": self._session_id,
                "open": Config.SESSION_OPEN['true'],
                "now": self.now
            })

            if result and result.get('success'):
                self.model.exec('session', 'close', {
                    "sessionId": self._session_id,
                    "open": Config.SESSION_OPEN['false'],
                    "modified": self.now,
                    "now": self.now
                })

        return self.delete_session_cookie()

    def create(self, user_id, ua, session_data) -> dict:
        """create_session"""
        session_token = secrets.token_urlsafe(Config.SESSION_TOKEN_LENGTH)
        expire = self.now + Config.SESSION_IDLE_EXPIRES_SECONDS

        self.model.exec('session', 'create', {
            "sessionId": session_token,
            "userId": user_id,
            "open": Config.SESSION_OPEN['true'],
            "ua": ua,
            "properties": json.dumps(session_data),
            "modified": self.now,
            "created": self.now,
            "expire": expire,
        })

        if self.model.has_error:
            return self.delete_session_cookie()

        return self.create_session_cookie(session_token, Config.SESSION_IDLE_EXPIRES_SECONDS)

    def update(self, session_token) -> dict:
        """update session"""
        expire = self.now + Config.SESSION_IDLE_EXPIRES_SECONDS

        self.model.exec('session', 'update', {
            "sessionId": session_token,
            "modified": self.now,
            "expire": expire
        })

        if self.model.has_error:
            return self.delete_session_cookie()

        return self.create_session_cookie(session_token, Config.SESSION_IDLE_EXPIRES_SECONDS)

    def create_session_cookie(self, session_token, max_age_seconds) -> dict:
        """create_session_cookie"""
        return {
            Config.SESSION_KEY: {
                "key": Config.SESSION_KEY,
                "value": session_token,
                "max_age": max_age_seconds,
                "httponly": True,
                "secure": True,
                "samesite": "Lax"
            }
        }

    def delete_session_cookie(self) -> dict:
        """create_session_cookie"""
        return {
            Config.SESSION_KEY: {
                "key": Config.SESSION_KEY,
                "value": "",
                "max_age": 0,
                "httponly": True,
                "secure": True,
                "samesite": "Lax"
            }
        }
