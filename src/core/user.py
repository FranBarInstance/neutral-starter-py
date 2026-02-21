# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Module for handling user operations"""

import random
from datetime import datetime, timezone
import time
# import json
import bcrypt
from constants import USER_EXISTS, UNCONFIRMED, UNVALIDATED, PIN_TARGET_REMINDER
from utils.sbase64url import sbase64url_sha256, sbase64url_token
from app.config import Config
from .model import Model
# import pprint


class User:
    """User creation and authentication handler"""
    RBAC_DEFAULT_ROLES = (
        ("role_dev", "dev", "Developer", "Development role"),
        ("role_admin", "admin", "Administrator", "Administrative role"),
        ("role_moderator", "moderator", "Moderator", "Moderation role"),
        ("role_editor", "editor", "Editor", "Content editing role"),
    )
    _RBAC_BOOTSTRAPPED = set()

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
        roles = {row.get("role.code") for row in user_rows if row.get("role.code")}
        return sorted(roles)

    def _setup_rbac(self) -> None:
        cache_key = (self._db_url, self._db_type)
        if not self._is_memory_sqlite() and cache_key in self._RBAC_BOOTSTRAPPED:
            return

        self.model.exec("user", "setup-rbac")
        if self.model.has_error:
            return

        for role_id, code, name, description in self.RBAC_DEFAULT_ROLES:
            self.model.exec(
                "user",
                "insert-role-if-missing",
                {
                    "roleId": role_id,
                    "code": code,
                    "name": name,
                    "description": description,
                    "created": self.now,
                    "modified": self.now,
                },
            )
            if self.model.has_error:
                return

        if not self._is_memory_sqlite():
            self._RBAC_BOOTSTRAPPED.add(cache_key)

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
        return {
            "profileId": profile_id,
            "userId": user_id,
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

    def _build_user_pin_params(self, target, user_id):
        return {
            "target": target,
            "userId": user_id,
            "pin": random.randint(Config.PIN_MIN, Config.PIN_MAX),
            "token": sbase64url_token(Config.TOKEN_LENGTH),
            "created": self.now,
            "expires": self.now + Config.PIN_EXPIRES_SECONDS
        }

    def create(self, data) -> dict:
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
        user_data = {
            'userId': user_data_list[0]['userId'],
            'birthdate': (
                user_data_list[0]['birthdate'].decode('utf-8')
                if isinstance(user_data_list[0]['birthdate'], (bytes, bytearray))
                else user_data_list[0]['birthdate']
            ),
            'created': user_data_list[0]['created'],
            'lasttime': user_data_list[0]['lasttime'],
            'modified': user_data_list[0]['modified'],
            'alias': user_data_list[0].get('user_profile.alias') or "",
            'locale': user_data_list[0].get('user_profile.locale') or "",
            "user_disabled": {},
            "roles": self._extract_roles(user_data_list),
        }

        for row in user_data_list:
            if row.get('user_disabled.reason'):
                key = str(row['user_disabled.reason'])
                user_data['user_disabled'][Config.DISABLED_KEY[key]] = key
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
                        self.model.exec('user', 'delete-pin', {"target": target, "userId": user_data_list[0]['userId'], "pin": pin})
                        user_data['user_disabled'].pop(Config.DISABLED_KEY[key])

        return user_data

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
                'alias': user_row.get('user_profile.alias', ''),
                'email': login,
                'userId': user_row.get('userId'),
                'profileId': user_row.get('user_profile.profileId', ''),
                'locale': user_row.get('user_profile.locale', ''),
                'roles': self.get_roles(user_row.get('userId')),
            }
        }

    def get_roles(self, user_id) -> list[str]:
        """Get all role codes assigned to a user."""
        if not user_id:
            return []
        result = self.model.exec("user", "get-roles-by-userid", {"userId": user_id})
        if not result or not result.get("rows"):
            return []
        return sorted({str(row[0]) for row in result["rows"] if row and row[0]})

    def has_role(self, user_id, role_code: str) -> bool:
        """Check if a user has a role."""
        code = self._normalize_role_code(role_code)
        if not user_id or not code:
            return False
        result = self.model.exec("user", "has-role", {"userId": user_id, "code": code})
        if self.model.has_error or not result or not result.get("rows") or not result["rows"][0]:
            return False
        return bool(result["rows"][0][0])

    def assign_role(self, user_id, role_code: str) -> bool:
        """Assign a role to a user. Idempotent."""
        code = self._normalize_role_code(role_code)
        if not user_id or not code:
            return False
        result = self.model.exec(
            "user",
            "assign-role-by-code",
            {"userId": user_id, "code": code, "created": self.now},
        )
        if self.model.has_error:
            return False
        if result and result.get("rowcount", 0) > 0:
            return True
        return self.has_role(user_id, code)

    def remove_role(self, user_id, role_code: str) -> bool:
        """Remove a role from a user. Idempotent."""
        code = self._normalize_role_code(role_code)
        if not user_id or not code:
            return False
        result = self.model.exec(
            "user",
            "remove-role-by-code",
            {"userId": user_id, "code": code},
        )
        if self.model.has_error:
            return False
        if result and result.get("rowcount", 0) > 0:
            return True
        return not self.has_role(user_id, code)

    def build_session_user_data(self, user_id) -> dict:
        """Build a minimal session payload with current user roles."""
        return {
            "userId": user_id,
            "user_disabled": {},
            "roles": self.get_roles(user_id),
        }

    @staticmethod
    def _rows_to_dicts(result) -> list[dict]:
        if not result or not result.get("rows"):
            return []
        columns = list(dict.fromkeys(result["columns"]))
        return [dict(zip(columns, row)) for row in result["rows"]]

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
        role_code="",
        disabled_reason="",
        limit=100,
        offset=0,
    ) -> list[dict]:
        """List users for admin views with roles and disabled flags."""
        operation_map = {
            "created": "admin-list-by-created",
            "modified": "admin-list-by-modified",
            "role_date": "admin-list-by-role-date",
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
                "role_code": self._normalize_role_code(role_code),
                "disabled_reason": normalized_disabled_reason,
                "limit": int(limit),
                "offset": int(offset),
            },
        )
        if self.model.has_error:
            return []

        users = self._rows_to_dicts(result)
        for user_row in users:
            for key, value in list(user_row.items()):
                if isinstance(value, (bytes, bytearray)):
                    user_row[key] = value.decode("utf-8", errors="ignore")
            user_row["created_human"] = self._format_unix_timestamp(user_row.get("created"))
            user_row["modified_human"] = self._format_unix_timestamp(user_row.get("modified"))
            user_row["lasttime_human"] = self._format_unix_timestamp(user_row.get("lasttime"))
            user_id = user_row.get("userId")
            user_row["roles"] = self.get_roles(user_id)
            disabled_result = self.model.exec("user", "admin-get-disabled-by-userid", {"userId": user_id})
            if self.model.has_error:
                user_row["disabled"] = []
                self.model.clear_error()
                continue
            user_row["disabled"] = self._rows_to_dicts(disabled_result)
            for disabled_row in user_row["disabled"]:
                disabled_row["created_human"] = self._format_unix_timestamp(disabled_row.get("created"))
                disabled_row["modified_human"] = self._format_unix_timestamp(disabled_row.get("modified"))

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
