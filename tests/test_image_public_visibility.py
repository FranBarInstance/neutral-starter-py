"""Tests for public image visibility rules."""

from __future__ import annotations

import io

from PIL import Image as PilImage

from app.bootstrap_db import bootstrap_databases
from app.config import Config
from constants import MODERATED, UNCONFIRMED, UNVALIDATED
from core.image import Image
from core.user import User


class _UploadFile:
    """Minimal upload file stub for image helper tests."""

    def __init__(self, data: bytes, filename: str = "test.png", mimetype: str = "image/png"):
        self.stream = io.BytesIO(data)
        self.filename = filename
        self.mimetype = mimetype

    def read(self) -> bytes:
        """Read the full file content."""
        return self.stream.read()


def _png_bytes() -> bytes:
    """Build a small in-memory PNG image."""
    image = PilImage.new("RGB", (16, 16), color=(10, 20, 30))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _bootstrap_helpers(tmp_path, monkeypatch):
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
    monkeypatch.setattr(Config, "DB_PWA", f"sqlite:///{pwa_db}")
    monkeypatch.setattr(Config, "DB_PWA_TYPE", "sqlite")
    monkeypatch.setattr(Config, "DB_IMAGE", f"sqlite:///{image_db}")
    monkeypatch.setattr(Config, "DB_IMAGE_TYPE", "sqlite")
    return User(f"sqlite:///{pwa_db}", "sqlite"), Image(f"sqlite:///{image_db}", "sqlite")


def _activate_user(user: User, user_id) -> None:
    """Remove signup disabled flags so the profile becomes public."""
    user.delete_user_disabled(user_id, Config.DISABLED[UNCONFIRMED])
    user.delete_user_disabled(user_id, Config.DISABLED[UNVALIDATED])


def _create_image_owner(user: User, image_helper: Image) -> tuple[dict, str]:
    """Create one active user and upload one image."""
    created = user.create(
        {
            "username": "image-public-123",
            "alias": "Image Public",
            "email": "image-public@example.com",
            "password": "password123",
            "birthdate": "2000-01-01",
            "locale": "en",
        }
    )
    _activate_user(user, created["userId"])
    uploaded = image_helper.upload_images([_UploadFile(_png_bytes())], str(created["profileId"]), "gallery")
    return created, uploaded[0]["imageId"]


def test_public_variant_is_available_for_active_profile(tmp_path, monkeypatch):
    """Public variants should be available for active user and profile."""
    user, image_helper = _bootstrap_helpers(tmp_path, monkeypatch)
    _created, image_id = _create_image_owner(user, image_helper)

    variant = image_helper.get_public_variant(image_id, "thumb")

    assert variant is not None
    assert variant.width > 0
    assert variant.height > 0
    assert variant.data


def test_public_variant_is_hidden_for_disabled_user(tmp_path, monkeypatch):
    """Public variants must not be served when the owner user is disabled."""
    user, image_helper = _bootstrap_helpers(tmp_path, monkeypatch)
    created, image_id = _create_image_owner(user, image_helper)

    assert user.set_user_disabled(created["userId"], Config.DISABLED[MODERATED], "hidden") is True

    assert image_helper.get_public_variant(image_id, "thumb") is None


def test_public_variant_is_hidden_for_disabled_profile(tmp_path, monkeypatch):
    """Public variants must not be served when the owner profile is disabled."""
    user, image_helper = _bootstrap_helpers(tmp_path, monkeypatch)
    created, image_id = _create_image_owner(user, image_helper)

    assert user.set_profile_disabled(created["profileId"], Config.DISABLED[MODERATED], "hidden") is True

    assert image_helper.get_public_variant(image_id, "thumb") is None
