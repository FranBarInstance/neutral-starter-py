# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Module for handling user operations"""

import random
from datetime import datetime, timezone
import time
import json
import regex
import bcrypt
from constants import (
    USER_EXISTS,
    UNCONFIRMED,
    UNVALIDATED,
    PIN_TARGET_REMINDER,
    RBAC_DEFAULT_ROLES,
)
from utils.sbase64url import sbase64url_sha256, sbase64url_token
from app.config import Config
from .model import Model
# import pprint

USERNAME_REGEX = regex.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
RESERVED_USERNAMES = (
    "about", "abuse", "account", "accounts", "admin", "administrator", "amazon",
    "anonymous", "api", "app", "assets", "auth", "avatar", "avatars", "bot",
    "config", "contact", "create", "dashboard", "default", "delete", "demo",
    "edit", "example", "facebook", "feedback", "google", "guest", "help",
    "home", "image", "images", "index", "instagram", "install", "login",
    "logout", "media", "meta", "microsoft", "mod", "moderator", "my",
    "netflix", "new", "null", "official", "profile", "public", "private",
    "register", "report", "root", "sample", "settings", "setup", "signup",
    "staff", "static", "support", "system", "team", "test", "twitter",
    "undefined", "update", "upgrade", "upload", "uploads", "user", "users",
    "whatsapp",
)


class User:  # pylint: disable=too-many-public-methods
    """User creation and authentication handler.

    This class intentionally has many public methods as it serves as the primary
    interface for all user-related operations including authentication,
    profile management, role assignment, and administrative functions.
    The high method count reflects the comprehensive nature of user management.
    """

    def __init__(self, db_url=Config.DB_PWA, db_type=Config.DB_PWA_TYPE):
        """Initialize the User class with a database connection."""
        self._db_url = db_url
        self._db_type = db_type
        self.model = Model(db_url, db_type)
        self.now = int(time.time())
        self._setup_rbac()

    def _is_memory_sqlite(self) -> bool:
        return self._db_type == "sqlite" and ":memory:" in str(self._db_url)

    @staticmethod
    def _normalize_role_code(role_code: str) -> str:
        return (role_code or "").strip().lower()

    @staticmethod
    def _extract_roles(user_rows: list[dict]) -> list[str]:
        roles = {row.get("profile_role.code") for row in user_rows if row.get("profile_role.code")}
        return sorted(roles)

    @staticmethod
    def _default_runtime_user() -> dict:
        return {
            "auth": False,
            "id": "",
            "userId": "",
            "profile_roles": {},
            "user_disabled": {},
            "profile_disabled": {},
            "profile": {
                "id": "",
                "userId": "",
                "username": "",
                "username_changed_at": "",
                "imageId": "",
                "alias": "",
                "locale": "",
                "region": "",
                "properties": {},
                "lasttime": "",
                "created": "",
                "modified": "",
            },
        }

    def _build_runtime_user_data(self, user_rows: list[dict]) -> dict:
        user_data = self._default_runtime_user()
        if not user_rows:
            return user_data

        first_row = user_rows[0]
        user_id = str(first_row.get("userId") or "").strip()
        if not user_id:
            return user_data

        properties_raw = first_row.get("user_profile.properties") or "{}"
        try:
            if isinstance(properties_raw, dict):
                properties = properties_raw
            else:
                properties = json.loads(properties_raw)
        except (json.JSONDecodeError, TypeError):
            properties = {}

        user_data.update(
            {
                "auth": True,
                "id": user_id,
                "userId": user_id,
                "created": first_row.get("created") or "",
                "lasttime": first_row.get("lasttime") or "",
                "modified": first_row.get("modified") or "",
                "profile_roles": {
                    role: role for role in self._extract_roles(user_rows)
                },
                "profile": {
                    "id": first_row.get("user_profile.profileId") or "",
                    "userId": user_id,
                    "username": first_row.get("user_profile.username") or "",
                    "username_changed_at": first_row.get("user_profile.username_changed_at") or "",
                    "imageId": first_row.get("user_profile.imageId") or "",
                    "alias": first_row.get("user_profile.alias") or "",
                    "locale": first_row.get("user_profile.locale") or "",
                    "region": first_row.get("user_profile.region") or "",
                    "properties": properties,
                    "lasttime": first_row.get("user_profile.lasttime") or "",
                    "created": first_row.get("user_profile.created") or "",
                    "modified": first_row.get("user_profile.modified") or "",
                },
            }
        )

        for row in user_rows:
            if row.get("user_disabled.reason"):
                key = str(row["user_disabled.reason"])
                user_data["user_disabled"][Config.DISABLED_KEY.get(key, key)] = key
            if row.get("profile_disabled.reason"):
                key = str(row["profile_disabled.reason"])
                user_data["profile_disabled"][Config.DISABLED_KEY.get(key, key)] = key

        return user_data

    def _setup_rbac(self) -> None:
        """Create RBAC tables but do not insert roles (now managed via constants)."""
        self.model.exec("user", "setup-rbac")

    def _build_user_params(self, user_id, login, data):
        return {
            "userId": user_id,
            "login": login,
            "password": self.hash_password(data['password']),
            "birthdate": self.hash_birthdate(data['birthdate']),
            "lasttime": self.now,
            "created": self.now,
            "modified": self.now
        }

    def _build_user_profile_params(self, profile_id, user_id, data):
        username = self.normalize_username(data.get("username")) or None
        return {
            "profileId": profile_id,
            "userId": user_id,
            "username": username,
            "username_changed_at": self.now if username else None,
            "imageId": data.get("imageId"),
            "region": data['region'].strip() if 'region' in data else None,
            "locale": data['locale'],
            "alias": data['alias'].strip(),
            "properties": data['properties'].strip() if 'properties' in data else "{}",
            "lasttime": self.now,
            "created": self.now,
            "modified": self.now
        }

    def _build_user_email_params(self, user_id, data):
        return {
            "email": data['email'].strip(),
            "userId": user_id,
            "main": Config.MAIN_EMAIL['true'],
            "created": self.now
        }

    def _build_user_disabled_params(self, user_id, reason):
        return {
            "userId": user_id,
            "reason": reason,
            "created": self.now,
            "modified": self.now
        }

    def _build_user_pin_params(self, target, user_id, expires_seconds=None):
        return {
            "target": target,
            "userId": user_id,
            "pin": random.randint(Config.PIN_MIN, Config.PIN_MAX),
            "token": sbase64url_token(Config.TOKEN_LENGTH),
            "created": self.now,
            "expires": self.now + int(expires_seconds or Config.PIN_EXPIRES_SECONDS)
        }

    @staticmethod
    def normalize_username(username: str | None) -> str:
        """Normalize external username input before validation."""
        return (username or "").strip().lower()

    @staticmethod
    def username_pattern() -> str:
        """Expose the canonical username regex pattern."""
        return USERNAME_REGEX.pattern

    def is_valid_username(self, username: str | None) -> bool:
        """Validate username against length, ASCII and regex rules."""
        normalized = self.normalize_username(username)
        if not normalized:
            return False
        if not normalized.isascii():
            return False
        if len(normalized) < Config.USERNAME_MIN_LENGTH:
            return False
        if len(normalized) > Config.USERNAME_MAX_LENGTH:
            return False
        return bool(USERNAME_REGEX.fullmatch(normalized))

    def username_exists(self, username: str, exclude_profile_id: str = "") -> bool:
        """Check whether a username is already assigned to another profile."""
        normalized = self.normalize_username(username)
        if not normalized:
            return False
        result = self.model.exec("user", "check-username-exists", {"username": normalized})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return False
        owner_profile_id = str(result["rows"][0][0] or "")
        return bool(owner_profile_id and owner_profile_id != str(exclude_profile_id or "").strip())

    def get_blacklisted_username(self, username: str, now: int | None = None) -> dict:
        """Return blacklist data for an active username reservation."""
        normalized = self.normalize_username(username)
        if not normalized:
            return {}
        result = self.model.exec(
            "user",
            "get-blacklisted-username",
            {"username": normalized, "now": int(now or time.time())},
        )
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return {}
        row = result["rows"][0]
        return {
            "username": row[0] or "",
            "reason": row[1] or "",
            "expires_at": row[2],
        }

    def is_username_available(self, username: str, exclude_profile_id: str = "") -> bool:
        """Check if a username can be assigned right now."""
        normalized = self.normalize_username(username)
        if not normalized:
            return True
        if not self.is_valid_username(normalized):
            return False
        if self.username_exists(normalized, exclude_profile_id=exclude_profile_id):
            return False
        return not bool(self.get_blacklisted_username(normalized))

    def reserve_released_username(self, username: str) -> bool:
        """Blacklist a released username according to installation TTL."""
        normalized = self.normalize_username(username)
        if not normalized:
            return True
        ttl = int(Config.USERNAME_RELEASED_TTL)
        expires_at = None if ttl <= 0 else int(time.time()) + ttl
        result = self.model.exec(
            "user",
            "upsert-username-blacklist",
            {
                "username": normalized,
                "reason": "released",
                "expires_at": expires_at,
                "created": int(time.time()),
            },
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def validate_username_change(  # pylint: disable=too-many-return-statements
        self,
        profile_id: str,
        username: str,
    ) -> dict:
        """Validate a username update against cooldown, uniqueness and blacklist."""
        profile_id = str(profile_id or "").strip()
        result = self.model.exec("user", "get-profile-by-profileid", {"profileId": profile_id})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return {"success": False, "error": "PROFILE_NOT_FOUND"}

        row = result["rows"][0]
        current_username = self.normalize_username(row[2] if len(row) > 2 else "")
        username_changed_at = row[3] if len(row) > 3 else None
        normalized = self.normalize_username(username)

        if normalized == current_username:
            return {
                "success": True,
                "changed": False,
                "username": current_username,
                "current_username": current_username,
            }

        if normalized and not self.is_valid_username(normalized):
            return {"success": False, "error": "INVALID"}

        cooldown = int(Config.USERNAME_CHANGE_COOLDOWN)
        if normalized and cooldown > 0 and username_changed_at:
            try:
                elapsed = int(time.time()) - int(username_changed_at)
            except (TypeError, ValueError):
                elapsed = cooldown
            if elapsed < cooldown:
                return {
                    "success": False,
                    "error": "COOLDOWN",
                    "available_in": cooldown - elapsed,
                }

        if normalized and self.username_exists(normalized, exclude_profile_id=profile_id):
            return {"success": False, "error": "TAKEN"}

        blacklist_entry = self.get_blacklisted_username(normalized) if normalized else {}
        if blacklist_entry:
            return {
                "success": False,
                "error": "BLACKLISTED",
                "reason": blacklist_entry.get("reason", ""),
            }

        return {
            "success": True,
            "changed": True,
            "username": normalized,
            "current_username": current_username,
        }

    def get_profile_by_username(self, username: str) -> dict:
        """Return one profile row resolved by exact username."""
        normalized = self.normalize_username(username)
        if not normalized:
            return {}

        result = self.model.exec("user", "get-profile-by-username", {"username": normalized})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return {}

        row = result["rows"][0]
        return {
            "profileId": row[0] or "",
            "userId": row[1] or "",
            "username": row[2] or "",
            "username_changed_at": row[3] or "",
            "imageId": row[4] or "",
            "alias": row[5] or "",
            "locale": row[6] or "",
            "region": row[7] or "",
            "properties": row[8] or "",
            "lasttime": row[9] or "",
            "created": row[10] or "",
            "modified": row[11] or "",
        }

    def create(self, data) -> dict:  # pylint: disable=too-many-return-statements
        """Create a new user with the provided data."""

        # Required fields validation
        required = ['email', 'password', 'birthdate', 'locale', 'alias']
        if not all(field in data for field in required):
            missing = [field for field in required if field not in data]
            return {
                'success': False,
                'error': 'MISSING_FIELDS',
                'message': f'Missing required fields: {", ".join(missing)}'
            }

        login = self.hash_login(data['email'].strip())

        # Check if user already exists
        exists = self.model.exec('user', 'check-exists', {"login": login})
        if self.model.has_error:
            return self.model.get_last_error()
        if exists['rows'][0][0]:
            return {
                'success': False,
                'error': USER_EXISTS,
                'message': 'User already exists'
            }

        # Create user and profile IDs
        user_id = self.model.create_uid('user')
        if self.model.has_error:
            return self.model.get_last_error()
        profile_id = self.model.create_uid('user_profile')
        if self.model.has_error:
            return self.model.get_last_error()

        target = str(Config.DISABLED[UNCONFIRMED])
        pin_params = self._build_user_pin_params(target, user_id)
        username = self.normalize_username(data.get("username"))
        if username and not self.is_username_available(username, exclude_profile_id=profile_id):
            return {
                'success': False,
                'error': 'USERNAME_NOT_AVAILABLE',
                'message': 'Username is not available'
            }
        data["username"] = username

        # Create user, profile, email, disabled and disabled_unvalidated records
        result = self.model.exec('user', 'create', [
            self._build_user_params(user_id, login, data),
            self._build_user_profile_params(profile_id, user_id, data),
            self._build_user_email_params(user_id, data),
            self._build_user_disabled_params(user_id, Config.DISABLED[UNCONFIRMED]),
            self._build_user_disabled_params(user_id, Config.DISABLED[UNVALIDATED]),
            pin_params
        ])

        if self.model.has_error:
            return self.model.get_last_error()

        if not result or not all(r.get('success') for r in result):
            return {
                'success': False,
                'error': 'CREATION_INCOMPLETE',
                'message': 'Failed to create user. Please contact administrator.'
            }

        if not Config.VALIDATE_SIGNUP:
            self.model.exec('user', 'delete-disabled', {"reason": Config.DISABLED[UNVALIDATED], "userId": user_id})

        return {
            'success': True,
            'alias': data['alias'],
            'username': data['username'],
            'userId': user_id,
            'profileId': profile_id,
            'token': pin_params['token'],
            'pin': pin_params['pin']
        }

    def hash_login(self, email) -> str:
        """Converts email to base64url SHA-256 hash"""
        return sbase64url_sha256(email)

    def hash_password(self, password: str) -> bytes:
        """Hash the password using bcrypt."""
        return bcrypt.hashpw(password.strip().encode('utf-8'), bcrypt.gensalt())

    def hash_birthdate(self, birthdate: str) -> str:
        """Hash normalized birthdate timestamp using bcrypt."""
        dt = datetime.fromisoformat(birthdate).replace(tzinfo=timezone.utc)
        ts = dt.timestamp()
        return bcrypt.hashpw(str(ts).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_login(self, login, password, pin) -> dict | None:
        """Validates user credentials and returns user data if valid"""

        # Blank login or password
        if not login or not password:
            return None

        login_b64 = self.hash_login(login)
        result = self.model.exec('user', 'get-by-login', {"login": login_b64})

        # The user does not exist in the database
        if not (result and result['rows'] and result['rows'][0] and result['rows'][0][2]):
            return None

        columns = list(dict.fromkeys(result['columns']))
        user_data_list = [dict(zip(columns, row)) for row in result['rows']]

        # Check user password
        if not bcrypt.checkpw(password.encode('utf-8'), user_data_list[0]['password']):
            return None

        unconfirmed = Config.DISABLED[UNCONFIRMED]
        user_data = self._build_runtime_user_data(user_data_list)

        for row in user_data_list:
            if row.get('user_disabled.reason'):
                key = str(row['user_disabled.reason'])
                if pin and row['user_disabled.reason'] == unconfirmed:
                    target = str(unconfirmed)
                    result_pin = self.model.exec('user', 'get-pin', {
                        "target": target,
                        "userId": user_data_list[0]['userId'],
                        "pin": pin,
                        "now": self.now
                    })
                    if result_pin and result_pin['rows'] and result_pin['rows'][0] and result_pin['rows'][0][0]:
                        self.model.exec('user', 'delete-disabled', {
                            "reason": unconfirmed, "userId": user_data_list[0]['userId']
                        })
                        self.model.exec(
                            'user',
                            'delete-pin',
                            {
                                "target": target,
                                "userId": user_data_list[0]['userId'],
                                "pin": pin,
                            },
                        )
                        user_data['user_disabled'].pop(Config.DISABLED_KEY.get(key, key))

        return user_data

    def get_runtime_user(self, user_id: str) -> dict:
        """Load the current authenticated user from DB for request context."""
        user_id = str(user_id or "").strip()
        if not user_id:
            return self._default_runtime_user()

        result = self.model.exec("user", "get-by-userid", {"userId": user_id})
        if self.model.has_error or not result or not result.get("rows"):
            self.model.clear_error()
            return self._default_runtime_user()

        columns = list(dict.fromkeys(result["columns"]))
        user_rows = [dict(zip(columns, row)) for row in result["rows"]]
        return self._build_runtime_user_data(user_rows)

    def get_user(self, login):
        """Retrieve user data based on login."""
        login_b64 = self.hash_login(login)
        result = self.model.exec('user', 'get-by-login', {"login": login_b64})

        if self.model.has_error:
            return self.model.get_last_error()

        if not result or not result['rows'] or not result['rows'][0] or not result['rows'][0][0]:
            return {
                'success': False,
                'error': 'USER_NOT_FOUND',
                'message': 'User not found',
                'user_data': {}
            }

        columns = list(dict.fromkeys(result['columns']))
        row = result['rows'][0]
        user_row = dict(zip(columns, row))

        return {
            'success': True,
            'error': '',
            'message': '',
            'user_data': {
                'email': login,
                'userId': user_row.get('userId'),
                'profile_roles': self.get_roles_by_profile(
                    user_row.get('user_profile.profileId', '')
                ),
                'profile': {
                    'id': user_row.get('user_profile.profileId', ''),
                    'userId': user_row.get('userId'),
                    'username': user_row.get('user_profile.username', ''),
                    'username_changed_at': user_row.get('user_profile.username_changed_at', ''),
                    'imageId': user_row.get('user_profile.imageId', ''),
                    'alias': user_row.get('user_profile.alias', ''),
                    'locale': user_row.get('user_profile.locale', ''),
                    'region': user_row.get('user_profile.region', ''),
                    'properties': user_row.get('user_profile.properties', '{}'),
                    'lasttime': user_row.get('user_profile.lasttime', ''),
                    'created': user_row.get('user_profile.created', ''),
                    'modified': user_row.get('user_profile.modified', ''),
                },
            }
        }

    def get_roles(self, user_id) -> list[str]:
        """Get all role codes assigned to a user (via any of their profiles)."""
        if not user_id:
            return []
        result = self.model.exec("user", "get-roles-by-userid", {"userId": user_id})
        if not result or not result.get("rows"):
            return []
        return sorted({str(row[0]) for row in result["rows"] if row and row[0]})

    def get_roles_by_profile(self, profile_id) -> list[str]:
        """Get all role codes assigned to a specific profile."""
        if not profile_id:
            return []
        result = self.model.exec("user", "get-roles-by-profileid", {"profileId": profile_id})
        if not result or not result.get("rows"):
            return []
        return sorted({str(row[0]) for row in result["rows"] if row and row[0]})

    def get_main_email(self, user_id: str) -> str:
        """Get the main email for a user."""
        if not user_id:
            return ""
        result = self.model.exec("user", "get-email-by-userid", {"userId": user_id})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            return ""
        return result["rows"][0][0] or ""

    def get_user_emails(self, user_id: str) -> list[dict]:
        """Get all emails for a user ordered by main then created."""
        user_id = str(user_id or "").strip()
        if not user_id:
            return []
        result = self.model.exec("user", "get-emails-by-userid", {"userId": user_id})
        if self.model.has_error or not result or not result.get("rows"):
            self.model.clear_error()
            return []
        emails = []
        for row in result["rows"]:
            if not row:
                continue
            emails.append(
                {
                    "email": row[0] or "",
                    "main": int(row[1] or 0),
                    "created": row[2] or "",
                }
            )
        return emails

    def count_user_emails(self, user_id: str) -> int:
        """Count emails for a user."""
        user_id = str(user_id or "").strip()
        if not user_id:
            return 0
        result = self.model.exec("user", "count-emails-by-userid", {"userId": user_id})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return 0
        return int(result["rows"][0][0] or 0)

    def get_userid_by_email(self, email: str) -> str:
        """Get userId that owns a given email (if any)."""
        email = (email or "").strip().lower()
        if not email:
            return ""
        result = self.model.exec("user", "get-userid-by-email", {"email": email})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return ""
        return str(result["rows"][0][0] or "")

    def login_exists(self, login: str) -> bool:
        """Check whether a login (email) already exists."""
        login = (login or "").strip()
        if not login:
            return False
        login_b64 = self.hash_login(login)
        result = self.model.exec("user", "check-exists", {"login": login_b64})
        if self.model.has_error or not result or not result.get("rows"):
            self.model.clear_error()
            return False
        return bool(result["rows"][0][0])

    def verify_user_password(self, user_id: str, raw_password: str) -> bool:
        """Validate the current password for a user."""
        user_id = str(user_id or "").strip()
        raw_password = raw_password or ""
        if not user_id or not raw_password:
            return False
        result = self.model.exec("user", "get-password-by-userid", {"userId": user_id})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return False
        stored_hash = result["rows"][0][0]
        if not stored_hash:
            return False
        return bcrypt.checkpw(raw_password.encode("utf-8"), stored_hash)

    def verify_login_email(self, user_id: str, email: str) -> bool:
        """Validate that a provided email matches the login for user."""
        user_id = str(user_id or "").strip()
        email = (email or "").strip()
        if not user_id or not email:
            return False
        result = self.model.exec("user", "get-login-by-userid", {"userId": user_id})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return False
        login_hash = result["rows"][0][0]
        if not login_hash:
            return False
        return login_hash == self.hash_login(email)

    def add_user_email(self, user_id: str, email: str, main: bool = False) -> bool:
        """Add an email to a user."""
        user_id = str(user_id or "").strip()
        email = (email or "").strip().lower()
        if not user_id or not email:
            return False
        params = {
            "email": email,
            "userId": user_id,
            "main": Config.MAIN_EMAIL["true"] if main else Config.MAIN_EMAIL["false"],
            "created": self.now,
        }
        result = self.model.exec("user", "insert-user-email", params)
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def delete_user_email(self, user_id: str, email: str) -> bool:
        """Delete a user email."""
        user_id = str(user_id or "").strip()
        email = (email or "").strip().lower()
        if not user_id or not email:
            return False
        result = self.model.exec("user", "delete-user-email", {"userId": user_id, "email": email})
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def set_user_email_main(self, user_id: str, email: str, main: bool = True) -> bool:
        """Set or unset an email as main for a user."""
        user_id = str(user_id or "").strip()
        email = (email or "").strip().lower()
        if not user_id or not email:
            return False
        result = self.model.exec(
            "user",
            "set-user-email-main",
            {
                "userId": user_id,
                "email": email,
                "main": Config.MAIN_EMAIL["true"] if main else Config.MAIN_EMAIL["false"],
            },
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def create_email_pin(self, email: str, user_id: str) -> dict | None:
        """Create or update a PIN for a specific email target."""
        email = (email or "").strip().lower()
        user_id = str(user_id or "").strip()
        if not email or not user_id:
            return None
        pin_params = self._build_user_pin_params(
            email,
            user_id,
            Config.PIN_ACCOUNT_EXPIRES_SECONDS,
        )
        result = self.model.exec("user", "insert-pin", pin_params)
        if self.model.has_error:
            return None
        if not result or not all(r.get("success", True) for r in (result if isinstance(result, list) else [result])):
            return None
        return pin_params

    def create_account_pin(self, target: str, user_id: str) -> dict | None:
        """Create or update a PIN for account actions."""
        target = (target or "").strip()
        user_id = str(user_id or "").strip()
        if not target or not user_id:
            return None
        pin_params = self._build_user_pin_params(
            target,
            user_id,
            Config.PIN_ACCOUNT_EXPIRES_SECONDS,
        )
        result = self.model.exec("user", "insert-pin", pin_params)
        if self.model.has_error:
            return None
        if not result or not all(r.get("success", True) for r in (result if isinstance(result, list) else [result])):
            return None
        return pin_params

    def verify_user_pin(self, target: str, user_id: str, pin: str) -> bool:
        """Validate a PIN for a target and user."""
        target = (target or "").strip()
        user_id = str(user_id or "").strip()
        pin = str(pin or "").strip()
        if not target or not user_id or not pin:
            return False
        result = self.model.exec(
            "user",
            "get-pin",
            {"target": target, "userId": user_id, "pin": pin, "now": int(time.time())},
        )
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            self.model.clear_error()
            return False
        return bool(result["rows"][0][0])

    def delete_user_pin(self, target: str, user_id: str, pin: str) -> bool:
        """Delete a PIN for a target and user."""
        target = (target or "").strip()
        user_id = str(user_id or "").strip()
        pin = str(pin or "").strip()
        if not target or not user_id or not pin:
            return False
        result = self.model.exec(
            "user",
            "delete-pin",
            {"target": target, "userId": user_id, "pin": pin},
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def has_role(self, user_id, role_code: str) -> bool:
        """Check if a user has a role in any of their profiles."""
        code = self._normalize_role_code(role_code)
        if not user_id or not code:
            return False
        result = self.model.exec("user", "has-role", {"userId": user_id, "code": code})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            return False
        return bool(result["rows"][0][0])

    def has_role_by_profile(self, profile_id, role_code: str) -> bool:
        """Check if a specific profile has a role."""
        code = self._normalize_role_code(role_code)
        if not profile_id or not code:
            return False
        result = self.model.exec("user", "has-role-by-profileid", {"profileId": profile_id, "code": code})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            return False
        return bool(result["rows"][0][0])

    def assign_role(self, user_id, role_code: str) -> bool:
        """Assign a role to a user.

        The role storage is profile-based, so this method resolves the user's first
        profile by exact `userId` and applies the role there.
        """
        code = self._normalize_role_code(role_code)
        if not user_id or not code:
            return False

        result = self.model.exec(
            "user",
            "admin-get-profiles-by-userid",
            {"userId": user_id},
        )
        if not result or not result.get("rows"):
            return False

        columns = list(result["columns"])
        try:
            profile_col = columns.index("profileId")
        except ValueError:
            return False
        profile_id = result["rows"][0][profile_col]
        return self.assign_role_to_profile(profile_id, code)

    def assign_role_to_profile(self, profile_id, role_code: str) -> bool:
        """Assign a role to a specific profile. Idempotent."""
        code = self._normalize_role_code(role_code)
        if not profile_id or not code:
            return False

        # Validate that the role exists in RBAC_DEFAULT_ROLES
        valid_roles = {role[0] for role in RBAC_DEFAULT_ROLES}
        if code not in valid_roles:
            return False

        result = self.model.exec(
            "user",
            "assign-role-by-code",
            {"profileId": profile_id, "code": code, "created": self.now},
        )
        if self.model.has_error:
            return False
        if result and result.get("rowcount", 0) > 0:
            return True
        return self.has_role_by_profile(profile_id, code)

    def remove_role(self, user_id, role_code: str) -> bool:
        """Remove a role from a user.

        The role storage is profile-based, so this method resolves the user's first
        profile by exact `userId` and removes the role there.
        """
        code = self._normalize_role_code(role_code)
        if not user_id or not code:
            return False

        result = self.model.exec(
            "user",
            "admin-get-profiles-by-userid",
            {"userId": user_id},
        )
        if not result or not result.get("rows"):
            return False

        columns = list(result["columns"])
        try:
            profile_col = columns.index("profileId")
        except ValueError:
            return False
        profile_id = result["rows"][0][profile_col]
        return self.remove_role_from_profile(profile_id, code)

    def remove_role_from_profile(self, profile_id, role_code: str) -> bool:
        """Remove a role from a specific profile. Idempotent."""
        code = self._normalize_role_code(role_code)
        if not profile_id or not code:
            return False
        result = self.model.exec(
            "user",
            "remove-role-by-code",
            {"profileId": profile_id, "code": code},
        )
        if self.model.has_error:
            return False
        if result and result.get("rowcount", 0) > 0:
            return True
        return not self.has_role_by_profile(profile_id, code)

    def build_session_user_data(self, user_id) -> dict:
        """Build the minimal persistent session payload."""
        return {"userId": str(user_id or "").strip()}

    @staticmethod
    def _rows_to_dicts(result) -> list[dict]:
        if not result or not result.get("rows"):
            return []

        cols = result["columns"]
        rows = result["rows"]
        res = []

        for row in rows:
            d = {}
            for i, col in enumerate(cols):
                val = row[i]
                if "." in col:
                    parts = col.split(".")
                    curr = d
                    for part in parts[:-1]:
                        if part not in curr or not isinstance(curr[part], dict):
                            curr[part] = {}
                        curr = curr[part]
                    curr[parts[-1]] = val
                else:
                    d[col] = val
            res.append(d)
        return res

    @staticmethod
    def _format_unix_timestamp(value) -> str:
        """Format unix timestamp to UTC datetime string for template display."""
        try:
            ts = int(value)
            if ts <= 0:
                return ""
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        except (TypeError, ValueError, OSError):
            return ""

    def admin_list_users(
        self,
        order_by="created",
        search="",
        code="",
        disabled_reason="",
        limit=100,
        offset=0,
    ) -> list[dict]:
        """List users for admin views with roles and disabled flags."""
        operation_map = {
            "created": "admin-list-by-created",
            "modified": "admin-list-by-modified",
            "assigned_date": "admin-list-by-assigned-date",
            "disabled_created_date": "admin-list-by-disabled-created-date",
            "disabled_modified_date": "admin-list-by-disabled-modified-date",
            # Backward compatibility with previous single disabled ordering key
            "disabled_date": "admin-list-by-disabled-modified-date",
        }
        operation = operation_map.get(order_by, "admin-list-by-created")

        normalized_disabled_reason = ""
        if str(disabled_reason).strip():
            try:
                normalized_disabled_reason = int(disabled_reason)
            except (TypeError, ValueError):
                normalized_disabled_reason = ""

        result = self.model.exec(
            "user",
            operation,
            {
                "search": (search or "").strip(),
                "code": self._normalize_role_code(code),
                "disabled_reason": normalized_disabled_reason,
                "limit": int(limit),
                "offset": int(offset),
            },
        )
        if self.model.has_error:
            return []

        # Helper to recursively decode bytes
        def decode_dict(target):
            for k, v in list(target.items()):
                if isinstance(v, (bytes, bytearray)):
                    target[k] = v.decode("utf-8", errors="ignore")
                elif isinstance(v, dict):
                    decode_dict(v)

        users = self._rows_to_dicts(result)
        for user_row in users:
            decode_dict(user_row)
            user_row["created_human"] = self._format_unix_timestamp(user_row.get("created"))
            user_row["modified_human"] = self._format_unix_timestamp(user_row.get("modified"))
            user_row["lasttime_human"] = self._format_unix_timestamp(user_row.get("lasttime"))
            user_id = user_row.get("userId")

            # Fetch all profiles for this user
            p_res = self.model.exec("user", "admin-get-profiles-by-userid", {"userId": user_id})
            if self.model.has_error:
                user_row["profiles"] = []
                self.model.clear_error()
            else:
                user_row["profiles"] = self._rows_to_dicts(p_res)

            # Keep compatibility for existing templates/logic that might look at user-level roles
            # We use roles from any of the user's profiles
            user_row["roles"] = self.get_roles(user_id)

            disabled_result = self.model.exec("user", "admin-get-disabled-by-userid", {"userId": user_id})
            if self.model.has_error:
                user_row["disabled"] = []
                self.model.clear_error()
            else:
                user_row["disabled"] = self._rows_to_dicts(disabled_result)
            for disabled_row in user_row["disabled"]:
                disabled_row["created_human"] = self._format_unix_timestamp(disabled_row.get("created"))
                disabled_row["modified_human"] = self._format_unix_timestamp(disabled_row.get("modified"))

            # Per-profile disabled info for all profiles
            user_row["profile_disabled"] = []
            for profile in user_row["profiles"]:
                p_id = profile.get("profileId")
                p_disabled_result = self.model.exec("user", "admin-get-profile-disabled-by-profileid", {"profileId": p_id})
                if self.model.has_error:
                    self.model.clear_error()
                else:
                    p_disabled = self._rows_to_dicts(p_disabled_result)
                    for p_row in p_disabled:
                        p_row["profileId"] = p_id
                        p_row["created_human"] = self._format_unix_timestamp(p_row.get("created"))
                        p_row["modified_human"] = self._format_unix_timestamp(p_row.get("modified"))
                    user_row["profile_disabled"].extend(p_disabled)

        return users

    def set_user_disabled(self, user_id, reason, description="") -> bool:
        """Add or update a disabled reason for a user."""
        result = self.model.exec(
            "user",
            "upsert-disabled",
            {
                "reason": reason,
                "userId": user_id,
                "description": (description or "").strip() or None,
                "created": self.now,
                "modified": self.now,
            },
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def set_profile_disabled(self, profile_id, reason, description="") -> bool:
        """Add or update a disabled reason for a profile."""
        result = self.model.exec(
            "user",
            "upsert-profile-disabled",
            {
                "reason": reason,
                "profileId": profile_id,
                "description": (description or "").strip() or None,
                "created": self.now,
                "modified": self.now,
            },
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def delete_profile_disabled(self, profile_id, reason) -> bool:
        """Remove a disabled reason for a profile."""
        result = self.model.exec(
            "user",
            "delete-profile-disabled",
            {
                "reason": reason,
                "profileId": profile_id,
            },
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def delete_user_disabled(self, user_id, reason) -> bool:
        """Remove a disabled reason for a user."""
        result = self.model.exec(
            "user",
            "delete-disabled",
            {
                "reason": reason,
                "userId": user_id,
            },
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def delete_user(self, user_id) -> bool:
        """Delete user and all cascaded dependent records."""
        result = self.model.exec("user", "admin-delete-user", {"userId": user_id})
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def user_reminder(self, user_data):
        """Get user reminder token and pin."""
        if not user_data:
            return {
                'success': False,
                'error': 'USER_NOT_FOUND',
                'message': 'User not found',
                'reminder_data': {}
            }

        user_id = user_data['userId']
        target = PIN_TARGET_REMINDER
        pin_params = self._build_user_pin_params(target, user_id)

        result = self.model.exec('user', 'insert-pin', pin_params)

        if self.model.has_error:
            return self.model.get_last_error()

        if not result or not all(r.get('success', True) for r in (result if isinstance(result, list) else [result])):
            return {
                'success': False,
                'error': 'REMINDER_INSERT_FAILED',
                'message': 'Could not generate reminder token and pin',
                'reminder_data': {}
            }
        return {
            'success': True,
            'error': '',
            'message': '',
            'reminder_data': {
                'alias': user_data.get('alias', ''),
                'email': user_data.get('email', ''),
                'userId': user_id,
                'profileId': user_data.get('profileId'),
                'locale': user_data.get('locale', ''),
                'token': pin_params['token'],
                'pin': pin_params['pin']
            }
        }

    def admin_list_profiles(
        self,
        order_by="created",
        search="",
        code="",
        disabled_reason="",
        limit=100,
        offset=0,
    ) -> list[dict]:
        """List profiles for admin views with roles and disabled flags."""
        operation_map = {
            "created": "admin-profile-list-by-created",
            "modified": "admin-profile-list-by-modified",
        }
        operation = operation_map.get(order_by, "admin-profile-list-by-created")

        normalized_disabled_reason = ""
        if str(disabled_reason).strip():
            try:
                normalized_disabled_reason = int(disabled_reason)
            except (TypeError, ValueError):
                normalized_disabled_reason = ""

        result = self.model.exec(
            "user",
            operation,
            {
                "search": (search or "").strip(),
                "code": self._normalize_role_code(code),
                "disabled_reason": normalized_disabled_reason,
                "limit": int(limit),
                "offset": int(offset),
            },
        )
        if self.model.has_error:
            return []

        # Helper to recursively decode bytes
        def decode_dict(target):
            for k, v in list(target.items()):
                if isinstance(v, (bytes, bytearray)):
                    target[k] = v.decode("utf-8", errors="ignore")
                elif isinstance(v, dict):
                    decode_dict(v)

        profiles = self._rows_to_dicts(result)
        for profile_row in profiles:
            decode_dict(profile_row)
            profile_row["created_human"] = self._format_unix_timestamp(profile_row.get("created"))
            profile_row["modified_human"] = self._format_unix_timestamp(profile_row.get("modified"))
            profile_row["lasttime_human"] = self._format_unix_timestamp(profile_row.get("lasttime"))

            profile_id = profile_row.get("user_profile", {}).get("profileId")

            profile_row["roles"] = self.get_roles_by_profile(profile_id)

            p_disabled_result = self.model.exec("user", "admin-get-profile-disabled-by-profileid", {"profileId": profile_id})
            if self.model.has_error:
                profile_row["profile_disabled"] = []
                self.model.clear_error()
            else:
                profile_row["profile_disabled"] = self._rows_to_dicts(p_disabled_result)
                for p_row in profile_row["profile_disabled"]:
                    p_row["created_human"] = self._format_unix_timestamp(p_row.get("created"))
                    p_row["modified_human"] = self._format_unix_timestamp(p_row.get("modified"))

        return profiles

    def set_login(self, user_id, new_email) -> bool:
        """Update user login."""
        login_b64 = self.hash_login(new_email.strip())
        result = self.model.exec(
            "user",
            "set-login",
            {"userId": user_id, "login": login_b64, "modified": self.now}
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def set_password(self, user_id, raw_password) -> bool:
        """Update user password."""
        hashed_pwd = self.hash_password(raw_password)
        result = self.model.exec(
            "user",
            "set-password",
            {"userId": user_id, "password": hashed_pwd, "modified": self.now}
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def set_birthdate(self, user_id, raw_birthdate) -> bool:
        """Update user birthdate."""
        hashed_birthdate = self.hash_birthdate(raw_birthdate)
        result = self.model.exec(
            "user",
            "set-birthdate",
            {"userId": user_id, "birthdate": hashed_birthdate, "modified": self.now}
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))

    def update_profile(self, profile_id, data: dict) -> bool:
        """Update user profile combining existing properties with new ones."""
        result_props = self.model.exec(
            "user",
            "get-profile-properties",
            {"profileId": profile_id}
        )
        if self.model.has_error or not result_props or not result_props.get("rows"):
            return False

        db_properties_str = result_props["rows"][0][0]
        current_image_id = result_props["rows"][0][1] if len(result_props["rows"][0]) > 1 else None
        current_username = self.normalize_username(
            result_props["rows"][0][2] if len(result_props["rows"][0]) > 2 else ""
        )
        current_username_changed_at = result_props["rows"][0][3] if len(result_props["rows"][0]) > 3 else None
        try:
            current_properties = json.loads(db_properties_str) if db_properties_str else {}
        except json.JSONDecodeError:
            current_properties = {}

        if not isinstance(current_properties, dict):
            current_properties = {}

        new_properties = data.get("properties")
        if new_properties and isinstance(new_properties, dict):
            current_properties.update(new_properties)

        merged_properties = json.dumps(current_properties)
        image_id = current_image_id
        if "imageId" in data:
            image_id = (data.get("imageId") or "").strip() or None

        username = current_username
        username_changed_at = current_username_changed_at
        if "username" in data:
            username_validation = self.validate_username_change(profile_id, data.get("username"))
            if not username_validation.get("success"):
                return False
            username = username_validation.get("username", current_username)
            if username_validation.get("changed"):
                if not self.reserve_released_username(current_username):
                    return False
                username_changed_at = self.now if username else None

        params = {
            "profileId": profile_id,
            "username": username or None,
            "username_changed_at": username_changed_at,
            "imageId": image_id,
            "alias": data.get("alias"),
            "region": data.get("region"),
            "locale": data.get("locale"),
            "properties": merged_properties,
            "modified": self.now
        }

        result = self.model.exec(
            "user",
            "update-profile",
            params
        )
        if self.model.has_error:
            return False
        return bool(result and result.get("success"))
