"""Tests for admin component."""

from __future__ import annotations

import sys

_TEST_COMPONENT = "cmp_7060_admin"
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
            "user_id": "42",
            "order": "created",
            "search": "",
            "delete_confirm": "",
        },
    )
    assert response.status_code == 200
    assert "Delete confirmation failed" in response.get_data(as_text=True)


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
