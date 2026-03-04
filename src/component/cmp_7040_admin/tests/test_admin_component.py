"""Tests for admin component."""

from __future__ import annotations

import sys

from app.config import Config
from constants import MODERATED, SPAM, UNVALIDATED
from core.user import User

_TEST_COMPONENT = "cmp_7040_admin"
_BP_NAME = f"bp_{_TEST_COMPONENT}"


def _route_prefix(flask_app) -> str:
    return flask_app.blueprints[_BP_NAME].url_prefix or ""


def _route(flask_app, suffix: str) -> str:
    return f"{_route_prefix(flask_app)}{suffix}"


def _methods_for_rule(flask_app, rule_path: str) -> set[str]:
    methods = set()
    for rule in flask_app.url_map.iter_rules():
        if rule.rule == rule_path:
            methods.update(rule.methods)
    return methods


def _runtime_admin_routes_module(client):
    endpoint = f"{_BP_NAME}.index"
    module_name = client.application.view_functions[endpoint].__module__
    return sys.modules[module_name]


def test_admin_blueprint_and_routes_registered(flask_app):
    """Admin component routes should be mounted."""
    assert _BP_NAME in flask_app.blueprints

    methods = _methods_for_rule(flask_app, _route(flask_app, "/"))
    assert "GET" in methods

    methods = _methods_for_rule(flask_app, _route(flask_app, "/<path:route>"))
    assert {"GET", "POST"}.issubset(methods)


def test_admin_requires_role(client):
    """Admin should reject access when session has no valid role."""
    response = client.get(_route(client.application, "/"))
    assert response.status_code == 403


def test_admin_user_accepts_moderator_role(client, monkeypatch):
    """Moderator role should be able to open /admin/user."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"moderator"}))

    response = client.get(_route(client.application, "/user"))
    assert response.status_code == 200


def test_admin_user_accepts_admin_role_and_post_action(client, monkeypatch):
    """Admin role should be able to POST action endpoint."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"admin"}))

    # Runtime route module sets ltoken in Dispatcher; we fetch a page first to get a valid token.
    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "assign-role",
            "user_id": "42",
            "role_code": "editor",
            "order": "created",
            "search": "",
        },
    )
    assert response.status_code == 200


def test_admin_delete_user_requires_confirmation(client, monkeypatch):
    """Delete user must require explicit DELETE confirmation."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"admin"}))

    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "delete-user",
            "user_id": "24",
            "order": "created",
            "search": "",
            "delete_confirm": "",
        },
    )
    assert response.status_code == 200
    assert "Delete confirmation failed" in response.get_data(as_text=True)


def test_admin_cannot_delete_self_user(client, monkeypatch):
    """Admin should not be able to delete their own user account."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"admin"}))

    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "delete-user",
            "user_id": "42",
            "order": "created",
            "search": "",
            "delete_confirm": "DELETE",
        },
    )
    assert response.status_code == 200
    assert "Deleting your own user is not allowed." in response.get_data(as_text=True)


def test_admin_cannot_remove_own_admin_or_dev_role(client, monkeypatch):
    """Admin should not be able to remove own privileged role."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"admin"}))
    remove_calls = []

    def fake_remove_role(_self, _user_id, _role_code):
        remove_calls.append(True)
        return True

    monkeypatch.setattr(User, "remove_role", fake_remove_role)

    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "remove-role",
            "user_id": "42",
            "role_code": "admin",
            "order": "created",
            "search": "",
        },
    )
    assert response.status_code == 200
    assert remove_calls == []


def test_admin_rejects_invalid_role_code(client, monkeypatch):
    """Role assignment should reject role codes outside allowed list."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"admin"}))

    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "assign-role",
            "user_id": "42",
            "role_code": "superadmin",
            "order": "created",
            "search": "",
        },
    )
    assert response.status_code == 200
    assert "Invalid role code." in response.get_data(as_text=True)


def test_moderator_can_remove_unvalidated(client, monkeypatch):
    """Moderator should be allowed to remove unvalidated status."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"moderator"}))

    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "remove-disabled",
            "user_id": "42",
            "reason": "200",
            "order": "created",
            "search": "",
        },
    )
    assert response.status_code == 200
    assert "Action not allowed for moderator role." not in response.get_data(as_text=True)


def test_moderator_can_set_moderated_with_description(client, monkeypatch):
    """Moderator should be allowed to set moderated when description is provided."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"moderator"}))

    page = client.get(_route(client.application, "/user"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    response = client.post(
        _route(client.application, "/user"),
        data={
            "ltoken": ltoken,
            "action": "set-disabled",
            "user_id": "42",
            "reason": "300",
            "description": "review required",
            "order": "created",
            "search": "",
        },
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Action not allowed for moderator role." not in text
    assert "Moderators can only set unvalidated or moderated." not in text


def test_profile_reasons_restricted_to_moderated_and_spam(client, monkeypatch):
    """Profile admin should only accept moderated/spam disabled reasons."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"admin"}))
    called_reasons = []

    def fake_set_profile_disabled(_self, _profile_id, reason, _description=""):
        called_reasons.append(reason)
        return True

    monkeypatch.setattr(User, "set_profile_disabled", fake_set_profile_disabled)

    page = client.get(_route(client.application, "/profile"))
    assert page.status_code == 200
    body = page.get_data(as_text=True)

    marker = 'name="ltoken" value="'
    start = body.find(marker)
    assert start != -1
    start += len(marker)
    end = body.find('"', start)
    ltoken = body[start:end]

    profile_marker = 'name="profile_id" value="'
    p_start = body.find(profile_marker)
    assert p_start != -1
    p_start += len(profile_marker)
    p_end = body.find('"', p_start)
    profile_id = body[p_start:p_end]

    user_marker = 'name="user_id" value="'
    u_start = body.find(user_marker)
    assert u_start != -1
    u_start += len(user_marker)
    u_end = body.find('"', u_start)
    user_id = body[u_start:u_end]

    response = client.post(
        _route(client.application, "/profile"),
        data={
            "ltoken": ltoken,
            "action": "set-profile-disabled",
            "user_id": user_id,
            "profile_id": profile_id,
            "reason": str(Config.DISABLED[UNVALIDATED]),
            "description": "invalid",
            "order": "created",
            "search": "",
        },
    )
    assert response.status_code == 200
    assert called_reasons == []

    ok_response = client.post(
        _route(client.application, "/profile"),
        data={
            "ltoken": ltoken,
            "action": "set-profile-disabled",
            "user_id": user_id,
            "profile_id": profile_id,
            "reason": str(Config.DISABLED[SPAM]),
            "description": "spam content",
            "order": "created",
            "search": "",
        },
    )
    assert ok_response.status_code == 200
    assert called_reasons == [Config.DISABLED[SPAM]]


def test_profile_moderator_ui_shows_spam_and_moderated_only(client, monkeypatch):
    """Moderator profile UI should not expose unvalidated reason."""
    admin_routes = _runtime_admin_routes_module(client)
    monkeypatch.setattr(admin_routes.DispatcherAdmin, "_resolve_current_roles", lambda _self: ("42", {"moderator"}))

    response = client.get(_route(client.application, "/profile"))
    assert response.status_code == 200
    body = response.get_data(as_text=True)

    assert f'value="{Config.DISABLED[MODERATED]}"' in body
    assert f'value="{Config.DISABLED[SPAM]}"' in body
    assert f'value="{Config.DISABLED[UNVALIDATED]}"' not in body
