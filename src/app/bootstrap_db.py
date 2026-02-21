"""Database bootstrap helpers for clean installations and integration tests."""

from __future__ import annotations

from core.model import Model


DEFAULT_ROLES = (
    ("role_dev", "dev", "Developer", "Development role"),
    ("role_admin", "admin", "Administrator", "Administrative role"),
    ("role_moderator", "moderator", "Moderator", "Moderation role"),
    ("role_editor", "editor", "Editor", "Content editing role"),
)


def _run_operation(model, model_name: str, operation: str, data=None) -> None:
    model.exec(model_name, operation, data)
    if model.has_error:
        detail = model.last_error or model.user_error or "Unknown database error"
        raise RuntimeError(f"{model_name}.{operation} failed: {detail}")


def bootstrap_databases(
    db_pwa_url: str,
    db_pwa_type: str,
    db_safe_url: str,
    db_safe_type: str,
    db_files_url: str,
    db_files_type: str,
) -> None:
    """Create/upgrade core schema in pwa/safe/files databases."""
    pwa_model = Model(db_pwa_url, db_pwa_type.lower())
    safe_model = Model(db_safe_url, db_safe_type.lower())
    files_model = Model(db_files_url, db_files_type.lower())

    _run_operation(pwa_model, "app", "setup-base")
    _run_operation(pwa_model, "user", "setup-base")
    _run_operation(pwa_model, "user", "setup-rbac")

    for role_id, code, name, description in DEFAULT_ROLES:
        _run_operation(
            pwa_model,
            "user",
            "insert-role-if-missing",
            {
                "roleId": role_id,
                "code": code,
                "name": name,
                "description": description,
                "created": 0,
                "modified": 0,
            },
        )

    _run_operation(safe_model, "session", "setup-base")

    # For files DB there is currently no schema in the project.
    _run_operation(files_model, "app", "sentence-example")
