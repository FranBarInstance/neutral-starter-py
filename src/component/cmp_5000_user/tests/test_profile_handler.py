"""Unit tests for user profile image handling."""

import importlib
import json
from pathlib import Path
COMPONENT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = COMPONENT_ROOT.name
MANIFEST = json.loads((COMPONENT_ROOT / "manifest.json").read_text(encoding="utf-8"))


def _user_handler_module():
    """Import the user handler module using the current component package name."""
    return importlib.import_module(f"component.{PACKAGE_NAME}.route.user_handler")


def _build_handler():
    """Create a minimal handler instance for focused unit testing."""
    module = _user_handler_module()
    handler = module.UserProfileFormHandler.__new__(module.UserProfileFormHandler)
    handler.schema_data = {
        "CONTEXT": {
            "POST": {},
        },
        "USER": {
            "profile": {
                "id": "profile-1",
                "username": "demo",
                "alias": "Demo",
                "locale": "en",
                "region": "",
                "imageId": "",
                "properties": {},
            }
        },
        "current": {
            "site": {
                "image_link": "/img",
                "image_link_profile": "/img/p",
                "image_link_variant": "/img/v",
            }
        }
    }
    handler.error = {"form": {}, "field": {}}
    return handler


class _DummyUser:
    """Simple user service stub for profile handler tests."""

    now = 1234567890

    @staticmethod
    def normalize_username(value):
        """Return a normalized username for tests."""
        return (value or "").strip().lower()

    @staticmethod
    def validate_username_change(_profile_id, username):
        """Accept username changes for focused tests."""
        return {"success": True, "username": username, "changed": False}


def test_validate_post_profile_rejects_imageid_from_other_profile(monkeypatch):
    """Profile image id must belong to the current profile when present."""
    module = _user_handler_module()
    handler = _build_handler()
    handler.user = _DummyUser()
    handler.schema_data["CONTEXT"]["POST"] = {
        "imageid": "11111111-1111-1111-1111-111111111111",
        "username": "demo",
    }
    handler.valid_form_tokens_post = lambda: True
    handler.valid_form_validation = lambda: True
    handler.any_error_form_fields = lambda _prefix: False
    handler._get_current_profile_id = lambda: "profile-1"

    class _StubImage:
        @staticmethod
        def get_meta(_image_id):
            return {"profileId": "profile-2"}

    monkeypatch.setattr(module, "Image", lambda: _StubImage())

    assert handler._validate_post_profile() is False
    assert handler.error["field"]["imageid"] == "ref:user_profile_form_error_value"


def test_save_profile_persists_empty_imageid_and_updates_session():
    """Empty profile image id is allowed and stored through update_profile."""
    handler = _build_handler()
    captured = {}

    class _SaveUser(_DummyUser):
        @staticmethod
        def update_profile(profile_id, data):
            captured["profile_id"] = profile_id
            captured["data"] = data
            return True

    handler.user = _SaveUser()
    handler.schema_data["CONTEXT"]["POST"] = {
        "username": "demo",
        "alias": "Demo User",
        "locale": "en",
        "region": "",
        "imageid": "",
        "theme": "ocean",
        "color": "blue",
        "dark_mode": "off",
    }

    assert handler._save_profile("profile-1") is True
    assert captured["profile_id"] == "profile-1"
    assert captured["data"]["imageId"] == ""
    assert handler.schema_data["USER"]["profile"]["imageId"] == ""
