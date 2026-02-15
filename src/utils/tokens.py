"""Token utility functions."""

import secrets
import time

import regex as re

from app.config import Config

from .sbase64url import sbase64url_sha256


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

    updated = int(time.time())

    # New token if expires
    if updated > int(created) + Config.UTOKEN_IDLE_EXPIRES_SECONDS:
        return utoken_create()

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


def ltoken_create(token, secret=Config.SECRET_KEY) -> str:
    """
    Create a link token using SHA-256 hash.
    Returns base64url encoded token string.
    """
    str_token = str(token) + str(secret)
    return sbase64url_sha256(str_token)


def ltoken_check(ltoken, token, secret=Config.SECRET_KEY) -> bool:
    """
    Validate link token.
    Returns True if provided token matches expected hash.
    """
    str_token = str(token) + str(secret)
    route_token = sbase64url_sha256(str_token)
    if route_token == ltoken:
        return True
    return False
