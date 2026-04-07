"""Tests for username generation and profile username updates."""

from __future__ import annotations

import sqlite3

from app.bootstrap_db import bootstrap_databases
from app.config import Config
from core.user import User


def _bootstrap_user(tmp_path):
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
    return User(f"sqlite:///{pwa_db}", "sqlite"), pwa_db


def test_bootstrap_seeds_reserved_username_blacklist(tmp_path):
    """Reserved usernames should be present right after bootstrap."""
    _, pwa_db = _bootstrap_user(tmp_path)

    with sqlite3.connect(str(pwa_db)) as conn:
        row = conn.execute(
            "SELECT reason, expires_at FROM username_blacklist WHERE username = ?",
            ("admin",),
        ).fetchone()

    assert row == ("reserved", None)


def test_create_allows_empty_username_and_exposes_empty_runtime_value(tmp_path):
    """New accounts can be created without username and keep it empty."""
    user, _ = _bootstrap_user(tmp_path)

    result = user.create(
        {
            "alias": "Test User",
            "email": "user@example.com",
            "password": "password123",
            "birthdate": "2000-01-01",
            "locale": "en",
        }
    )

    assert result["success"] is True
    assert result["username"] == ""

    runtime_user = user.get_runtime_user(result["userId"])
    assert runtime_user["profile"]["username"] == ""
    assert runtime_user["profile"]["username_changed_at"] == ""


def test_update_profile_changes_username_and_releases_old_one(tmp_path, monkeypatch):
    """Changing username should reserve the previous one in the blacklist."""
    monkeypatch.setattr(Config, "USERNAME_CHANGE_COOLDOWN", 0)
    monkeypatch.setattr(Config, "USERNAME_RELEASED_TTL", 3600)
    user, pwa_db = _bootstrap_user(tmp_path)

    created = user.create(
        {
            "username": "old-name-123",
            "alias": "Profile Owner",
            "email": "owner@example.com",
            "password": "password123",
            "birthdate": "2000-01-01",
            "locale": "en",
        }
    )
    old_username = created["username"]

    updated = user.update_profile(
        created["profileId"],
        {
            "username": "fresh-name-123",
            "alias": "Profile Owner",
            "locale": "en",
            "region": "",
            "properties": {},
        },
    )

    assert updated is True
    runtime_user = user.get_runtime_user(created["userId"])
    assert runtime_user["profile"]["username"] == "fresh-name-123"

    with sqlite3.connect(str(pwa_db)) as conn:
        row = conn.execute(
            "SELECT reason, expires_at FROM username_blacklist WHERE username = ?",
            (old_username,),
        ).fetchone()

    assert row[0] == "released"
    assert row[1] is not None


def test_update_profile_allows_clearing_username(tmp_path, monkeypatch):
    """Clearing username should be allowed and persist an empty runtime value."""
    monkeypatch.setattr(Config, "USERNAME_CHANGE_COOLDOWN", 3600)
    monkeypatch.setattr(Config, "USERNAME_RELEASED_TTL", 3600)
    user, pwa_db = _bootstrap_user(tmp_path)

    created = user.create(
        {
            "username": "clear-me-123",
            "alias": "Profile Owner",
            "email": "owner2@example.com",
            "password": "password123",
            "birthdate": "2000-01-01",
            "locale": "en",
        }
    )

    updated = user.update_profile(
        created["profileId"],
        {
            "username": "",
            "alias": "Profile Owner",
            "locale": "en",
            "region": "",
            "properties": {},
        },
    )

    assert updated is True
    runtime_user = user.get_runtime_user(created["userId"])
    assert runtime_user["profile"]["username"] == ""
    assert runtime_user["profile"]["username_changed_at"] == ""

    with sqlite3.connect(str(pwa_db)) as conn:
        row = conn.execute(
            "SELECT reason, expires_at FROM username_blacklist WHERE username = ?",
            ("clear-me-123",),
        ).fetchone()

    assert row[0] == "released"
    assert row[1] is not None


def test_validate_username_change_rejects_taken_and_blacklisted_usernames(tmp_path, monkeypatch):
    """Username validation should block reserved and already assigned values."""
    monkeypatch.setattr(Config, "USERNAME_CHANGE_COOLDOWN", 0)
    user, _ = _bootstrap_user(tmp_path)

    first = user.create(
        {
            "username": "first-user-123",
            "alias": "First User",
            "email": "first@example.com",
            "password": "password123",
            "birthdate": "2000-01-01",
            "locale": "en",
        }
    )
    second = user.create(
        {
            "alias": "Second User",
            "email": "second@example.com",
            "password": "password123",
            "birthdate": "2000-01-01",
            "locale": "en",
        }
    )

    taken = user.validate_username_change(second["profileId"], first["username"])
    blacklisted = user.validate_username_change(second["profileId"], "admin")

    assert taken["success"] is False
    assert taken["error"] == "TAKEN"
    assert blacklisted["success"] is False
    assert blacklisted["error"] == "BLACKLISTED"
