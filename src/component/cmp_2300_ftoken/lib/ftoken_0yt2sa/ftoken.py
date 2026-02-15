"""
Module for generating and managing form tokens (ftokens) used for CSRF protection.
"""

import hashlib
import time

from app.config import Config
from utils.sbase64url import sbase64url_sha256


def ftoken_create(key, fetch_id, form_id, user_token) -> dict:
    """
    Create a form token for CSRF protection.
    Returns dictionary with token data and metadata.
    """
    now = int(time.time())
    expire = now + Config.FTOKEN_EXPIRES_SECONDS
    data = str(key) + str(expire) + str(Config.SECRET_KEY) + str(user_token)
    b64_hash = sbase64url_sha256(data)
    return {
        "name": "ftoken." + str(expire),
        "value": b64_hash,
        "fetch_id": fetch_id,
        "form_id": form_id
    }


def ftoken_check(field_key_name, data, user_token) -> bool:
    """
    Validate form token to prevent CSRF attacks.
    Returns True if token is valid and not expired.
    """
    now = int(time.time())
    field_key = data.get(field_key_name) or None
    expire = None
    token_name = None
    token_value = None

    for k, v in data.items():
        if k.startswith('ftoken.'):
            token_name = k
            token_value = v
            token_split = k.split('.')
            expire = token_split[1]

    if not field_key or not expire or not token_name or not token_value:
        return False

    if now > int(expire):
        return False

    key = hashlib.sha256(field_key.encode()).hexdigest()
    hash_string = str(key) + str(expire) + str(Config.SECRET_KEY) + str(user_token)
    b64_hash = sbase64url_sha256(hash_string)

    if token_value == b64_hash:
        return True

    return False
