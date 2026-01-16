# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Module for handling user operations"""

import random
from datetime import datetime, timezone
# import json
import bcrypt
from constants import * # pylint: disable=wildcard-import,unused-wildcard-import
from utils.sbase64url import sbase64url_sha256, sbase64url_md5, sbase64url_token
from app.config import Config
from .model import Model
# import pprint


class User:
    """User creation and authentication handler"""

    def __init__(self, db_url=Config.DB_PWA, db_type=Config.DB_PWA_TYPE):
        """Initialize the User class with a database connection."""
        self.model = Model(db_url, db_type)

    def _build_user_params(self, user_id, login, data):
        return {
            "userId": user_id,
            "login": login,
            "password": self.hash_password(data['password']),
            "birthdate": self.hash_birthdate(data['birthdate']),
            "lasttime": NOW,
            "created": NOW,
            "modified": NOW
        }

    def _build_user_profile_params(self, profile_id, user_id, data):
        return {
            "profileId": profile_id,
            "userId": user_id,
            "region": data['region'].strip() if 'region' in data else None,
            "locale": data['locale'],
            "alias": data['alias'].strip(),
            "properties": data['properties'].strip() if 'properties' in data else "{}",
            "lasttime": NOW,
            "created": NOW,
            "modified": NOW
        }

    def _build_user_email_params(self, user_id, data):
        return {
            "email": data['email'].strip(),
            "userId": user_id,
            "main": Config.MAIN_EMAIL['true'],
            "created": NOW
        }

    def _build_user_disabled_params(self, user_id, reason):
        return {
            "userId": user_id,
            "reason": reason,
            "created": NOW,
            "modified": NOW
        }

    def _build_user_pin_params(self, target, user_id):
        return {
            "target": target,
            "userId": user_id,
            "pin": random.randint(Config.PIN_MIN, Config.PIN_MAX),
            "token": sbase64url_token(Config.TOKEN_LENGTH),
            "created": NOW,
            "expires": NOW + Config.PIN_EXPIRES_SECONDS
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
        """Obfuscate the birthdate as a base64url md5 hash of its UTC timestamp."""
        dt = datetime.fromisoformat(birthdate).replace(tzinfo=timezone.utc)
        ts = dt.timestamp()
        return sbase64url_md5(str(ts))

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
            'birthdate': user_data_list[0]['birthdate'],
            'created': user_data_list[0]['created'],
            'lasttime': user_data_list[0]['lasttime'],
            'modified': user_data_list[0]['modified'],
            "user_disabled": {}
        }

        for row in user_data_list:
            if row['user_disabled.reason']:
                key = str(row['user_disabled.reason'])
                user_data['user_disabled'][Config.DISABLED_KEY[key]] = key
                if pin and row['user_disabled.reason'] == unconfirmed:
                    target = str(user_data_list[0]['userId']) + '_' + str(unconfirmed)
                    result_pin = self.model.exec('user', 'get-pin', {"target": target, "pin": pin, "now": NOW})
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
            }
        }

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
        target = 'reminder'
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
