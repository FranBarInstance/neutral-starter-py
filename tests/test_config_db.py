"""Tests for SQLite-backed config overrides."""

import json
import sqlite3
import sys

from app import create_app
from app.config import Config
from app.config_db import ensure_config_db, get_component_custom_override


def _cleanup_component_modules():
    """Remove component modules to force reload in next test."""
    for module in list(sys.modules.keys()):
        if module.startswith("component."):
            del sys.modules[module]


def test_ensure_config_db_creates_file(tmp_path):
    """ensure_config_db must create config.db and schema."""
    db_path = tmp_path / "config.db"
    assert ensure_config_db(str(db_path), debug=True) is True
    assert db_path.exists()


def test_get_component_custom_override_returns_empty_when_missing(tmp_path):
    """Missing component entry must return empty dict."""
    db_path = tmp_path / "config.db"
    ensure_config_db(str(db_path))
    payload = get_component_custom_override(str(db_path), "unknown_uuid")
    assert payload == {}


def test_get_component_custom_override_reads_json_object(tmp_path):
    """DB entry should return parsed JSON object."""
    db_path = tmp_path / "config.db"
    ensure_config_db(str(db_path))

    override = {"manifest": {"route": "/db-route"}}
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO custom(comp_uuid, value_json, enabled, updated_at)
            VALUES(?, ?, 1, 0)
            """,
            ("example_uuid", json.dumps(override)),
        )

    payload = get_component_custom_override(str(db_path), "example_uuid")
    assert payload == override


def test_db_override_has_priority_over_custom_json(tmp_path):
    """DB override must be merged after custom.json and win conflicts."""
    db_path = tmp_path / "config.db"
    ensure_config_db(str(db_path))

    override = {
        "manifest": {
            "config": {
                "profiles": {
                    "ollama_local": {
                        "ollama": {
                            "model": "db-selected-model"
                        }
                    }
                }
            }
        }
    }
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO custom(comp_uuid, value_json, enabled, updated_at)
            VALUES(?, ?, 1, 0)
            """,
            ("ai_backend_0yt2sa", json.dumps(override)),
        )

    class _DbConfig(Config):  # pylint: disable=too-few-public-methods
        TESTING = True
        SECRET_KEY = "test_secret_key"
        DB_PWA = "sqlite:///:memory:"
        DB_SAFE = "sqlite:///:memory:"
        DB_IMAGE = "sqlite:///:memory:"
        MAIL_METHOD = "dummy"
        CONFIG_DB_PATH = str(db_path)

    try:
        app = create_app(_DbConfig, debug=True)

        comp = app.components.collection["ai_backend_0yt2sa"]

        # The active AI backend component has custom.json config; DB must win conflicts.
        assert (
            comp["manifest"]["config"]["profiles"]["ollama_local"]["ollama"]["model"]
            == "db-selected-model"
        )
    finally:
        # Cleanup component modules to avoid affecting other tests
        _cleanup_component_modules()
