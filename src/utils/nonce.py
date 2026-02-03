"""Nonce utility for CSP."""

import secrets

from flask import g


def generate_nonce() -> str:
    """
    Generate a cryptographically secure nonce for CSP.

    Returns:
        str: Base64-encoded nonce string
    """
    return secrets.token_urlsafe(16)


def get_nonce() -> str:
    """
    Get or create nonce for current request.
    Stores nonce in Flask.g for request-scoped access.

    Returns:
        str: Nonce string for current request
    """
    if 'csp_nonce' not in g:
        g.csp_nonce = generate_nonce()
    return g.csp_nonce


def set_nonce_in_context(context: dict) -> dict:
    """
    Add nonce to template context.

    Args:
        context: Template context dictionary

    Returns:
        dict: Updated context with nonce
    """
    context['CSP_NONCE'] = get_nonce()
    return context
