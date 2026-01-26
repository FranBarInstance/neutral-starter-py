# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Base64URL encoding/decoding with MD5 hash support."""

import base64
import hashlib
import secrets
import zlib


def sbase64url_encode(text):
    """Encode text to Base64URL format."""
    text_bytes = text.encode('utf-8')
    base64_str = base64.b64encode(text_bytes).decode('utf-8')
    b64url = base64_str.replace('+', '-').replace('/', '_').rstrip('=')
    return b64url


def sbase64url_decode(b64url):
    """Decode Base64URL encoded text."""
    padding = 4 - (len(b64url) % 4)
    if padding < 4:
        b64url += '=' * padding
    b64url = b64url.replace('-', '+').replace('_', '/')
    decoded_bytes = base64.urlsafe_b64decode(b64url)
    return decoded_bytes.decode('utf-8')


def sbase64url_sha256(data):
    """Generate SHA256 hash and encode to Base64URL."""
    digest = hashlib.sha256(data.encode('utf-8')).digest()
    b64 = base64.b64encode(digest).decode('utf-8')
    b64url = b64.replace('+', '-').replace('/', '_').rstrip('=')
    return b64url


def sbase64url_sha512(data):
    """Generate SHA512 hash and encode to Base64URL."""
    digest = hashlib.sha512(data.encode('utf-8')).digest()
    b64 = base64.b64encode(digest).decode('utf-8')
    b64url = b64.replace('+', '-').replace('/', '_').rstrip('=')
    return b64url


def sbase64url_md5(data):
    """Generate MD5 hash and encode to Base64URL."""
    digest = hashlib.md5(data.encode('utf-8')).digest()
    b64 = base64.b64encode(digest).decode('utf-8')
    b64url = b64.replace('+', '-').replace('/', '_').rstrip('=')
    return b64url


def sbase64url_crc32(data):
    """Generate CRC32 hash and encode to Base64URL."""
    crc_value = zlib.crc32(data.encode('utf-8'))
    crc_bytes = crc_value.to_bytes(4, byteorder='little')
    b64 = base64.b64encode(crc_bytes).decode('utf-8')
    b64url = b64.replace('+', '-').replace('/', '_').rstrip('=')
    return b64url


def sbase64url_token(size=32):
    """Generate a random token and encode to Base64URL."""
    token_bytes = secrets.token_bytes(size)
    b64 = base64.b64encode(token_bytes).decode('utf-8')
    b64url = b64.replace('+', '-').replace('/', '_').rstrip('=')
    return b64url
