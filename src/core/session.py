"""Session management module."""

import json
import secrets
from app.config import Config
from constants import * # pylint: disable=wildcard-import,unused-wildcard-import
from .model import Model


class Session:
    """session"""

    def __init__(self, session_id, db_url=Config.DB_SAFE, db_type=Config.DB_SAFE_TYPE):
        """session"""
        self.model = Model(db_url, db_type)
        self._session_id = session_id

    def get(self) -> tuple[str | None, dict]:
        """get session"""
        if not self._session_id:
            return None, {}

        result = self.model.exec('session', 'get', {
            "sessionId": self._session_id,
            "open": Config.SESSION_OPEN['true'],
            "now": NOW
        })

        if not result.get('rows') or not result['rows'][0]:
            return None, {}

        modified = result['rows'][0][4]
        expire = result['rows'][0][5]

        # Update session if modified more than 15 minutes ago
        if (NOW - modified) > (SECONDS_MINUTE * 15):
            session_cookie = self.update(self._session_id)
            return self._session_id, session_cookie

        return self._session_id, self.create_session_cookie(self._session_id, expire)

    def close(self) -> dict:
        """close session"""
        if self._session_id:
            result = self.model.exec('session', 'get', {
                "sessionId": self._session_id,
                "open": Config.SESSION_OPEN['true'],
                "now": NOW
            })

            if result['success']:
                self.model.exec('session', 'close', {
                    "sessionId": self._session_id,
                    "open": Config.SESSION_OPEN['false'],
                    "modified": NOW,
                    "now": NOW
                })

        return self.delete_session_cookie()

    def create(self, user_id, ua, session_data) -> dict:
        """create_session"""
        session_token = secrets.token_urlsafe(Config.SESSION_TOKEN_LENGTH)
        expire = NOW + Config.SESSION_IDLE_EXPIRES_SECONDS

        self.model.exec('session', 'create', {
            "sessionId": session_token,
            "userId": user_id,
            "open": Config.SESSION_OPEN['true'],
            "ua": ua,
            "properties": json.dumps(session_data),
            "modified": NOW,
            "created": NOW,
            "expire": expire,
        })

        if self.model.has_error:
            return self.delete_session_cookie()

        return self.create_session_cookie(session_token, expire)

    def update(self, session_token) -> dict:
        """update session"""
        expire = NOW + Config.SESSION_IDLE_EXPIRES_SECONDS

        self.model.exec('session', 'update', {
            "sessionId": session_token,
            "modified": NOW,
            "expire": expire
        })

        if self.model.has_error:
            return self.delete_session_cookie()

        return self.create_session_cookie(session_token, expire)

    def create_session_cookie(self, session_token, expire) -> dict:
        """create_session_cookie"""
        return {
            Config.SESSION_KEY: {
                "key": Config.SESSION_KEY,
                "value": session_token,
                "max_age": expire,
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
