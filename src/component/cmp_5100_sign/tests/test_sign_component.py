# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Tests for the sign component."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import bcrypt

from app.config import Config
import core.dispatcher as core_dispatcher_module
import dispatcher_form_sign as sign_dispatcher_module  # pylint: disable=import-error
from dispatcher_form_sign import DispatcherFormSignPin  # pylint: disable=import-error
from constants import PIN_TARGET_REMINDER, UNCONFIRMED
from core.user import User

_TEST_DIR = Path(__file__).resolve().parent
_COMP_DIR = _TEST_DIR.parent
_COMP_NAME = _COMP_DIR.name
_BP_NAME = f"bp_{_COMP_NAME}"


def _methods_for_rule(flask_app, rule_path: str) -> set[str]:
    methods = set()
    for rule in flask_app.url_map.iter_rules():
        if rule.rule == rule_path:
            methods.update(rule.methods)
    return methods


def _build_user_for_unit(model):
    user = User.__new__(User)
    user.model = model
    user.now = 1700000000
    user.hash_login = lambda email: email  # type: ignore[assignment]
    return user


def _route_prefix(flask_app) -> str:
    return flask_app.blueprints[_BP_NAME].url_prefix or ""


def _route(flask_app, suffix: str) -> str:
    return f"{_route_prefix(flask_app)}{suffix}"


def test_sign_blueprint_and_routes_registered(flask_app):
    """Sign component routes should be mounted with expected methods."""
    assert _BP_NAME in flask_app.blueprints

    methods = _methods_for_rule(flask_app, _route(flask_app, "/in"))
    assert "GET" in methods

    methods = _methods_for_rule(flask_app, _route(flask_app, "/in/form/<ltoken>"))
    assert {"GET", "POST"}.issubset(methods)

    methods = _methods_for_rule(flask_app, _route(flask_app, "/reminder"))
    assert "GET" in methods

    methods = _methods_for_rule(flask_app, _route(flask_app, "/reminder/form/<ltoken>"))
    assert {"GET", "POST"}.issubset(methods)

    methods = _methods_for_rule(flask_app, _route(flask_app, "/pin/<pin_token>"))
    assert "GET" in methods and "POST" not in methods

    methods = _methods_for_rule(flask_app, _route(flask_app, "/pin/form/<pin_token>/<ltoken>"))
    assert {"GET", "POST"}.issubset(methods)


def test_sign_schema_includes_pin_form_definition():
    """schema.json must include the dedicated sign_pin_form."""
    schema_path = _COMP_DIR / "schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    sign_pin_form = schema["data"]["core"]["forms"]["sign_pin_form"]

    assert sign_pin_form["rules"]["pin"]["required"] is True
    assert sign_pin_form["rules"]["pin"]["regex"] == "^[A-Za-z0-9]{4,10}$"
    assert "ftoken.*" in sign_pin_form["validation"]["allow_fields"]


def test_pin_container_renders_ajax_form_route(client):
    """PIN container should render tokenized pin flow scaffolding."""
    token = "abcTOKEN123"
    response = client.get(_route(client.application, f"/pin/{token}"))

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert token in body
    assert "form-wrapper-pin" in body
    assert "sign_pin_token" in body


def test_reminder_form_post_requires_ajax_header(client):
    """Reminder POST endpoint should reject non-AJAX requests."""
    response = client.post(_route(client.application, "/reminder/form/test-ltoken"))
    assert response.status_code == 403


def test_pin_form_post_requires_ajax_header(client):
    """PIN POST endpoint should reject non-AJAX requests."""
    response = client.post(_route(client.application, "/pin/form/test-token/test-ltoken"))
    assert response.status_code == 403


def _pin_post_data(pin="123456"):
    return {
        "pin": pin,
        "notrobot": "human",
        "ftoken.test": "token",
    }


def _runtime_pin_dispatcher_class(client):
    endpoint = f"{_BP_NAME}.sign_pin_form_post"
    module_name = client.application.view_functions[endpoint].__module__
    module = sys.modules[module_name]
    return module.DispatcherFormSignPin


def test_pin_form_post_invalid_token_returns_controlled_response(client, monkeypatch):
    """Invalid token in PIN POST should return controlled response (no 500)."""
    runtime_cls = _runtime_pin_dispatcher_class(client)
    monkeypatch.setattr(
        runtime_cls,
        "validate_pin_post",
        lambda _self, _error_prefix: True,
    )
    monkeypatch.setattr(
        runtime_cls,
        "_get_pin_data_by_token",
        lambda _self, _token: None,
    )

    response = client.post(
        _route(client.application, "/pin/form/bad-token/ok-ltoken"),
        data=_pin_post_data(),
        headers={"Requested-With-Ajax": "true"},
    )

    assert response.status_code == 200
    assert "Invalid or expired confirmation link." in response.get_data(as_text=True)


def test_pin_form_post_invalid_pin_returns_validation_error(client, monkeypatch):
    """Wrong PIN should not create session and must return validation feedback."""
    runtime_cls = _runtime_pin_dispatcher_class(client)
    monkeypatch.setattr(
        runtime_cls,
        "validate_pin_post",
        lambda _self, _error_prefix: True,
    )
    monkeypatch.setattr(
        runtime_cls,
        "_get_pin_data_by_token",
        lambda _self, _token: {"target": PIN_TARGET_REMINDER, "userId": "42", "pin": "999999"},
    )

    response = client.post(
        _route(client.application, "/pin/form/good-token/ok-ltoken"),
        data=_pin_post_data(pin="111111"),
        headers={"Requested-With-Ajax": "true"},
    )

    assert response.status_code == 200
    assert "Invalid PIN." in response.get_data(as_text=True)


def test_pin_form_post_valid_token_and_pin_redirects_home(client, monkeypatch):
    """Valid token + PIN should create session and render home redirect snippet."""
    runtime_cls = _runtime_pin_dispatcher_class(client)
    monkeypatch.setattr(
        runtime_cls,
        "validate_pin_post",
        lambda _self, _error_prefix: True,
    )
    monkeypatch.setattr(
        runtime_cls,
        "_get_pin_data_by_token",
        lambda _self, _token: {"target": PIN_TARGET_REMINDER, "userId": "42", "pin": "123456"},
    )

    class _FakeUser:
        def __init__(self):
            self.model = SimpleNamespace(exec=lambda *_args, **_kwargs: {"success": True})

        def build_session_user_data(self, user_id):
            return {"userId": user_id, "user_disabled": {}, "roles": []}

    monkeypatch.setattr(core_dispatcher_module, "User", _FakeUser)

    def _fake_create_session(self, _user_data):
        self.schema_data["CONTEXT"]["SESSION"] = "session-test"
        return True

    monkeypatch.setattr(
        runtime_cls,
        "create_session",
        _fake_create_session,
    )

    response = client.post(
        _route(client.application, "/pin/form/good-token/ok-ltoken"),
        data=_pin_post_data(pin="123456"),
        headers={"Requested-With-Ajax": "true"},
    )

    assert response.status_code == 200
    assert "util-reload-page-home" in response.get_data(as_text=True)


def test_user_check_login_with_unconfirmed_pin_clears_state(monkeypatch):
    """Valid PIN login must remove UNCONFIRMED and consume the PIN."""

    class FakeModel:
        def __init__(self):
            self.has_error = False
            self.calls = []

        def exec(self, domain, operation, params):  # pylint: disable=unused-argument
            self.calls.append((operation, params))
            if operation == "get-by-login":
                columns = [
                    "userId",
                    "password",
                    "birthdate",
                    "lasttime",
                    "created",
                    "modified",
                    "user_disabled.reason",
                    "user_disabled.description",
                    "user_profile.profileId",
                    "user_profile.alias",
                    "user_profile.locale",
                    "role.code",
                ]
                return {
                    "columns": columns,
                    "rows": [
                        [42, b"hash", "birth", 1, 2, 3, Config.DISABLED[UNCONFIRMED], "", 100, "alias", "en", "admin"]
                    ],
                }
            if operation == "get-pin":
                return {"columns": ["pin"], "rows": [[params["pin"]]]}
            return {"success": True}

    fake_model = FakeModel()
    user = _build_user_for_unit(fake_model)
    monkeypatch.setattr(bcrypt, "checkpw", lambda *_args, **_kwargs: True)

    user_data = user.check_login("user@example.com", "password123", "123456")

    assert user_data is not None
    assert UNCONFIRMED not in user_data["user_disabled"]
    assert user_data["roles"] == ["admin"]
    assert ("get-pin", {"target": str(Config.DISABLED[UNCONFIRMED]), "userId": 42, "pin": "123456", "now": user.now}) in fake_model.calls
    assert any(op == "delete-disabled" for op, _ in fake_model.calls)
    assert any(op == "delete-pin" for op, _ in fake_model.calls)


def test_user_reminder_uses_constant_target():
    """Reminder flow should insert PIN using the reminder target constant."""

    class FakeModel:
        def __init__(self):
            self.has_error = False
            self.last_insert = None

        def exec(self, domain, operation, params):  # pylint: disable=unused-argument
            if operation == "insert-pin":
                self.last_insert = params
                return {"success": True}
            return {"success": True}

        def get_last_error(self):
            return {"success": False}

    fake_model = FakeModel()
    user = _build_user_for_unit(fake_model)
    user._build_user_pin_params = lambda target, user_id: {  # type: ignore[assignment]
        "target": target,
        "userId": user_id,
        "pin": "654321",
        "token": "token123",
        "created": user.now,
        "expires": user.now + 3600,
    }

    result = user.user_reminder(
        {"userId": "42", "alias": "a", "email": "u@example.com", "profileId": "p", "locale": "en"}
    )

    assert result["success"] is True
    assert fake_model.last_insert["target"] == PIN_TARGET_REMINDER
    assert result["reminder_data"]["pin"] == "654321"


def test_user_create_fails_when_required_fields_missing():
    """User.create should reject payloads missing mandatory keys."""
    user = User.__new__(User)
    user.model = SimpleNamespace()
    user.now = 1700000000

    result = User.create(user, {"email": "missing@fields.test"})

    assert result["success"] is False
    assert result["error"] == "MISSING_FIELDS"


def test_user_check_login_returns_none_on_bad_password(monkeypatch):
    """Wrong password must return None and skip PIN logic."""

    class FakeModel:
        def __init__(self):
            self.has_error = False

        def exec(self, domain, operation, params):  # pylint: disable=unused-argument
            if operation == "get-by-login":
                columns = [
                    "userId",
                    "password",
                    "birthdate",
                    "lasttime",
                    "created",
                    "modified",
                    "user_disabled.reason",
                    "user_disabled.description",
                    "user_profile.profileId",
                    "user_profile.alias",
                    "user_profile.locale",
                    "role.code",
                ]
                return {
                    "columns": columns,
                    "rows": [[42, b"hash", "birth", 1, 2, 3, None, "", 100, "alias", "en", None]],
                }
            return {"success": True}

    user = _build_user_for_unit(FakeModel())
    monkeypatch.setattr(bcrypt, "checkpw", lambda *_args, **_kwargs: False)

    assert user.check_login("user@example.com", "wrong", "123456") is None


def test_user_role_helpers_assign_and_remove():
    """Role helper methods should be idempotent and normalized."""

    class FakeModel:
        def __init__(self):
            self.has_error = False
            self.roles = {"admin", "editor"}

        def exec(self, _domain, operation, params):
            if operation == "assign-role-by-code":
                assert params["code"] == "admin"
                return {"success": True, "rowcount": 0}
            if operation == "has-role":
                return {
                    "columns": ["count"],
                    "rows": [[1 if params["code"] in self.roles else 0]],
                }
            if operation == "remove-role-by-code":
                self.roles.discard(params["code"])
                return {"success": True, "rowcount": 1}
            if operation == "get-roles-by-userid":
                return {"columns": ["code"], "rows": [[role] for role in sorted(self.roles)]}
            return {"success": True}

    user = _build_user_for_unit(FakeModel())
    assert user.assign_role("42", " AdMiN ") is True
    assert user.has_role("42", "admin") is True
    assert user.remove_role("42", "admin") is True
    assert user.get_roles("42") == ["editor"]


def _build_pin_dispatcher_for_unit(pin_data, submitted_pin="111111"):
    dispatcher = DispatcherFormSignPin.__new__(DispatcherFormSignPin)
    dispatcher._ftoken_field_name = "pin"  # pylint: disable=protected-access
    dispatcher.error = {"form": {}, "field": {}}
    dispatcher.form_submit = {}
    dispatcher.schema_data = {
        "CONTEXT": {"SESSION": None, "POST": {"pin": submitted_pin}, "UTOKEN": "u"},
    }
    dispatcher.user = SimpleNamespace(
        model=SimpleNamespace(exec=lambda *_args, **_kwargs: {"success": True}),
        build_session_user_data=lambda user_id: {"userId": user_id, "user_disabled": {}, "roles": []},
    )
    dispatcher.validate_pin_post = lambda _error_prefix: True  # type: ignore[assignment]
    dispatcher._get_pin_data_by_token = lambda _pin_token: pin_data  # type: ignore[assignment] # pylint: disable=protected-access
    dispatcher.create_session = lambda data: data["userId"] == pin_data["userId"]  # type: ignore[assignment]
    return dispatcher


def test_dispatcher_pin_post_signup_clears_unconfirmed_and_pin():
    """Signup token should clear UNCONFIRMED and delete PIN before creating session."""
    calls = []

    def fake_exec(_domain, operation, params):
        calls.append((operation, params))
        return {"success": True}

    pin_data = {"target": str(Config.DISABLED[UNCONFIRMED]), "userId": "42", "pin": "111111"}
    dispatcher = _build_pin_dispatcher_for_unit(pin_data)
    dispatcher.user.model.exec = fake_exec

    result = dispatcher.form_post("token-signup")

    assert result is True
    assert any(op == "delete-disabled" for op, _ in calls)
    assert any(op == "delete-pin" for op, _ in calls)


def test_dispatcher_pin_post_reminder_deletes_pin_only():
    """Reminder token should not clear UNCONFIRMED but must delete PIN and create session."""
    calls = []

    def fake_exec(_domain, operation, params):
        calls.append((operation, params))
        return {"success": True}

    pin_data = {"target": PIN_TARGET_REMINDER, "userId": "42", "pin": "111111"}
    dispatcher = _build_pin_dispatcher_for_unit(pin_data)
    dispatcher.user.model.exec = fake_exec

    result = dispatcher.form_post("token-reminder")

    assert result is True
    assert not any(op == "delete-disabled" for op, _ in calls)
    assert any(op == "delete-pin" for op, _ in calls)


def test_dispatcher_pin_post_rejects_invalid_pin():
    """Invalid submitted PIN must fail without deleting state."""
    calls = []

    def fake_exec(_domain, operation, params):
        calls.append((operation, params))
        return {"success": True}

    pin_data = {"target": PIN_TARGET_REMINDER, "userId": "42", "pin": "999999"}
    dispatcher = _build_pin_dispatcher_for_unit(pin_data, submitted_pin="111111")
    dispatcher.user.model.exec = fake_exec

    result = dispatcher.form_post("token-reminder")

    assert result is False
    assert dispatcher.error["field"]["pin"] == "Invalid PIN."
    assert not calls


def test_dispatcher_pin_post_rejects_unknown_target():
    """Unknown token target must be marked invalid and not mutate user state."""
    calls = []

    def fake_exec(_domain, operation, params):
        calls.append((operation, params))
        return {"success": True}

    pin_data = {"target": "unsupported-target", "userId": "42", "pin": "111111"}
    dispatcher = _build_pin_dispatcher_for_unit(pin_data)
    dispatcher.user.model.exec = fake_exec

    result = dispatcher.form_post("token-unknown")

    assert result is False
    assert dispatcher.schema_data["sign_pin_token_invalid"] == "true"
    assert not calls


def test_send_reminder_returns_false_when_user_not_found():
    """send_reminder should fail safely when user lookup fails."""
    dispatcher = sign_dispatcher_module.DispatcherFormSign.__new__(sign_dispatcher_module.DispatcherFormSign)
    dispatcher.user = SimpleNamespace(get_user=lambda _email: {"success": False, "user_data": {}})

    assert dispatcher.send_reminder("missing@example.com") is False


def test_send_reminder_success_calls_mail(monkeypatch):
    """send_reminder should call Mail.send when user and reminder data are valid."""
    dispatcher = sign_dispatcher_module.DispatcherFormSign.__new__(sign_dispatcher_module.DispatcherFormSign)
    dispatcher.schema = SimpleNamespace(properties={"dummy": True})
    dispatcher.user = SimpleNamespace(
        get_user=lambda _email: {
            "success": True,
            "user_data": {"userId": "42", "alias": "u", "email": "u@example.com", "locale": "en"},
        },
        user_reminder=lambda _user_data: {
            "success": True,
            "reminder_data": {"token": "tok", "pin": "123456", "email": "u@example.com"},
        },
    )

    sent = {}

    class FakeMail:
        def __init__(self, _schema):
            pass

        def send(self, template, payload):
            sent["template"] = template
            sent["payload"] = payload

    monkeypatch.setattr(sign_dispatcher_module, "Mail", FakeMail)

    assert dispatcher.send_reminder("u@example.com") is True
    assert sent["template"] == "reminder"
    assert sent["payload"]["pin"] == "123456"
