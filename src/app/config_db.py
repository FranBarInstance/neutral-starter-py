"""SQLite-backed configuration store."""

import json
import os
import sqlite3
import time


def ensure_config_db(db_path, debug=False):
    """Create config DB and custom override table if missing."""
    try:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS custom (
                    comp_uuid TEXT NOT NULL PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_custom_enabled
                ON custom(enabled)
                """
            )
        return True
    except sqlite3.Error as exc:
        if debug:
            print(f"✗ config.db setup failed: {exc}")
        return False


def get_component_custom_override(db_path, component_uuid, debug=False):
    """Read component custom override from dedicated custom table."""
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                """
                SELECT value_json
                FROM custom
                WHERE comp_uuid = ?
                  AND enabled = 1
                LIMIT 1
                """,
                (component_uuid,),
            ).fetchone()
    except sqlite3.Error as exc:
        if debug:
            print(f"✗ config.db read failed for {component_uuid}: {exc}")
        return {}

    if not row:
        return {}

    try:
        payload = json.loads(row[0])
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        if debug:
            print(f"✗ config.db JSON parse failed for {component_uuid}: {exc}")
        return {}

    if not isinstance(payload, dict):
        if debug:
            print(f"✗ config.db override for {component_uuid} must be a JSON object")
        return {}

    return payload


def get_component_custom_raw(db_path, component_uuid, debug=False):
    """Read raw custom JSON text for a component UUID."""
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                """
                SELECT value_json
                FROM custom
                WHERE comp_uuid = ?
                LIMIT 1
                """,
                (component_uuid,),
            ).fetchone()
    except sqlite3.Error as exc:
        if debug:
            print(f"✗ config.db raw read failed for {component_uuid}: {exc}")
        return None

    if not row:
        return None
    return row[0]


def get_component_custom_entry(db_path, component_uuid, debug=False):
    """Read raw custom entry for a component UUID, including enabled state."""
    try:
        with sqlite3.connect(db_path) as conn:
            row = conn.execute(
                """
                SELECT comp_uuid, value_json, enabled, updated_at
                FROM custom
                WHERE comp_uuid = ?
                LIMIT 1
                """,
                (component_uuid,),
            ).fetchone()
    except sqlite3.Error as exc:
        if debug:
            print(f"✗ config.db entry read failed for {component_uuid}: {exc}")
        return None

    if not row:
        return None

    return {
        "comp_uuid": row[0],
        "value_json": row[1],
        "enabled": row[2],
        "updated_at": row[3],
    }


def list_component_custom_entries(db_path, debug=False):
    """List all component custom entries with metadata."""
    try:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                """
                SELECT comp_uuid, enabled, updated_at
                FROM custom
                ORDER BY comp_uuid ASC
                """
            ).fetchall()
    except sqlite3.Error as exc:
        if debug:
            print(f"✗ config.db list failed: {exc}")
        return []

    return [
        {
            "comp_uuid": row[0],
            "enabled": row[1],
            "updated_at": row[2],
        }
        for row in rows
    ]


def upsert_component_custom_override(db_path, component_uuid, override, enabled=True):
    """Insert or update component custom override in custom table."""
    payload = json.dumps(override, ensure_ascii=False, separators=(",", ":"))
    now = int(time.time())
    enabled_value = 1 if enabled else 0

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO custom(comp_uuid, value_json, enabled, updated_at)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(comp_uuid)
            DO UPDATE SET
                value_json = excluded.value_json,
                enabled = excluded.enabled,
                updated_at = excluded.updated_at
            """,
            (component_uuid, payload, enabled_value, now),
        )


def delete_component_custom_override(db_path, component_uuid, debug=False):
    """Delete component custom override from custom table."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                "DELETE FROM custom WHERE comp_uuid = ?",
                (component_uuid,),
            )
        return True
    except sqlite3.Error as exc:
        if debug:
            print(f"✗ config.db delete failed for {component_uuid}: {exc}")
        return False
