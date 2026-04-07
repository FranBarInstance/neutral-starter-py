"""Database bootstrap helpers for clean installations and integration tests."""

from __future__ import annotations

from core.model import Model
from core.user import RESERVED_USERNAMES




def _run_operation(model, model_name: str, operation: str, data=None) -> None:
    model.exec(model_name, operation, data)
    if model.has_error:
        detail = model.last_error or model.user_error or "Unknown database error"
        raise RuntimeError(f"{model_name}.{operation} failed: {detail}")


def _seed_reserved_usernames(model) -> None:
    """Insert the built-in reserved usernames into the blacklist."""
    for username in RESERVED_USERNAMES:
        _run_operation(
            model,
            "user",
            "upsert-username-blacklist",
            {
                "username": username,
                "reason": "reserved",
                "expires_at": None,
                "created": 0,
            },
        )


def bootstrap_databases(
    db_pwa_url: str,
    db_pwa_type: str,
    db_safe_url: str,
    db_safe_type: str,
    db_image_url: str,
    db_image_type: str,
) -> None:
    """Create/upgrade core schema in pwa/safe/image databases."""
    pwa_model = Model(db_pwa_url, db_pwa_type.lower())
    safe_model = Model(db_safe_url, db_safe_type.lower())
    image_model = Model(db_image_url, db_image_type.lower())

    _run_operation(pwa_model, "app", "setup-base")
    _run_operation(pwa_model, "user", "setup-base")
    _run_operation(pwa_model, "user", "setup-rbac")
    _seed_reserved_usernames(pwa_model)

    _run_operation(safe_model, "session", "setup-base")
    _run_operation(image_model, "image", "setup-base")
