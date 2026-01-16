"""Token utility functions."""

import time
import secrets
import regex as re
from constants import * # pylint: disable=wildcard-import,unused-wildcard-import
from app.config import Config
from .sbase64url import sbase64url_encode, sbase64url_sha256, sbase64url_md5


# Get user token or create if it does not exist.
# The expiration is ignored because it may be in the middle of a sequence,
# it is updated only on certain cases.
# So the expiration date is approximate.
def utoken_extract(utoken_str=None):
    """
    Extract or create a user token.
    Returns tuple (token, cookie) with new or existing token.
    """
    if not utoken_str:
        return utoken_create()

    try:
        created, utoken = utoken_str.split(":")
    except ValueError:
        created = None
        utoken = None

    # New token if current is invalid or None
    if not utoken or not created or not utoken_valid(utoken):
        return utoken_create()

    updated = int(time.time())
    return utoken, utoken_cookie(updated, utoken)


# Update token if expired
def utoken_update(utoken_str):
    """
    Update user token if expired.
    Returns tuple (token, cookie) with new or updated token.
    """
    if not utoken_str:
        return utoken_create()

    # New token if current is invalid
    try:
        created, utoken = utoken_str.split(":")
    except ValueError:
        return utoken_create()

    # New token if current is invalid
    if not utoken_valid(utoken):
        return utoken_create()

    # New token if expires
    if NOW > int(created) + Config.UTOKEN_IDLE_EXPIRES_SECONDS:
        return utoken_create()

    updated = int(time.time())
    return utoken, utoken_cookie(updated, utoken)


# Force create utoken
def utoken_create():
    """
    Create a new user token.
    Returns tuple (token, cookie) with fresh token.
    """
    created = int(time.time())
    utoken = secrets.token_urlsafe(24)
    cokookie = utoken_cookie(created, utoken)
    return utoken, cokookie


# Must be a session cookie so that it is updated frequently.
def utoken_cookie(created, utoken):
    """
    Create a secure session cookie for the user token.
    Returns cookie configuration dictionary.
    """
    return {
        Config.UTOKEN_KEY: {
            "key": Config.UTOKEN_KEY,
            "value": str(created) + ":" + str(utoken),
            "secure": True,
            "httponly": True,
            "samesite": "Lax",
        }
    }


# It does not matter if the user changes it as long as it has the required format and size.
def utoken_valid(utoken):
    """
    Validate user token format.
    Returns True if token matches required pattern.
    """
    return re.match(r'^[A-Za-z0-9\-\_]{22,43}$', utoken)


def ftoken_create(key, fetch_id, form_id, user_token) -> dict:
    """
    Create a form token for CSRF protection.
    Returns dictionary with token data and metadata.
    """
    timestamp = int(time.time())
    expire = timestamp + Config.FTOKEN_EXPIRES_SECONDS
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

    if NOW > int(expire):
        return False

    key = sbase64url_encode(field_key)
    hash_string = str(key) + str(expire) + str(Config.SECRET_KEY) + str(user_token)
    b64_hash = sbase64url_sha256(hash_string)

    if token_value == b64_hash:
        return True

    return False


def ltoken_create(token, secret=Config.SECRET_KEY) -> str:
    """
    Create a link token using MD5 hash.
    Returns base64url encoded token string.
    """
    str_token = str(token) + str(secret)
    return sbase64url_md5(str_token)


def ltoken_check(ltoken, token, secret=Config.SECRET_KEY) -> bool:
    """
    Validate link token.
    Returns True if provided token matches expected hash.
    """
    str_token = str(token) + str(secret)
    route_token = sbase64url_md5(str_token)
    if route_token == ltoken:
        return True
    return False
