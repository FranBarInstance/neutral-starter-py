"""Tests for database bootstrap helper."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from app.bootstrap_db import bootstrap_databases


def _table_names(db_path: Path) -> list[str]:
    with sqlite3.connect(str(db_path)) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
        ).fetchall()
    return [row[0] for row in rows]


def test_bootstrap_databases_creates_required_schema(tmp_path):
    """Bootstrap must create pwa/safe/image DBs with required tables."""
    pwa_db = tmp_path / "pwa.db"
    safe_db = tmp_path / "safe.db"
    image_db = tmp_path / "image.db"

    bootstrap_databases(
        db_pwa_url=f"sqlite:///{pwa_db}",
        db_pwa_type="sqlite",
        db_safe_url=f"sqlite:///{safe_db}",
        db_safe_type="sqlite",
        db_image_url=f"sqlite:///{image_db}",
        db_image_type="sqlite",
    )

    assert pwa_db.exists()
    assert safe_db.exists()
    assert image_db.exists()

    pwa_tables = _table_names(pwa_db)
    safe_tables = _table_names(safe_db)
    image_tables = _table_names(image_db)

    for required in (
        "uid",
        "user",
        "user_profile",
        "username_blacklist",
        "user_email",
        "user_disabled",
        "pin",
        "profile_role",
    ):
        assert required in pwa_tables
    assert "session" in safe_tables
    assert "image" in image_tables


def test_bootstrap_databases_is_idempotent(tmp_path):
    """Bootstrap can run multiple times without duplicating role seed rows."""
    pwa_db = tmp_path / "pwa.db"
    safe_db = tmp_path / "safe.db"
    image_db = tmp_path / "image.db"
    kwargs = {
        "db_pwa_url": f"sqlite:///{pwa_db}",
        "db_pwa_type": "sqlite",
        "db_safe_url": f"sqlite:///{safe_db}",
        "db_safe_type": "sqlite",
        "db_image_url": f"sqlite:///{image_db}",
        "db_image_type": "sqlite",
    }

    bootstrap_databases(**kwargs)
    bootstrap_databases(**kwargs)

    with sqlite3.connect(str(pwa_db)) as conn:
        rows = conn.execute(
            "SELECT code, COUNT(*) FROM profile_role GROUP BY code ORDER BY code"
        ).fetchall()

    # profile_role table exists but is empty (roles now managed via constants)
    assert rows == []
