# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Tests for aichat API hardening behavior."""

import importlib
from unittest.mock import patch


def _endpoint_for_rule(flask_app, rule_path: str, method: str) -> str:
    """Get endpoint name for a URL rule and HTTP method."""
    method_upper = method.upper()
    for rule in flask_app.url_map.iter_rules():
        if rule.rule == rule_path and method_upper in rule.methods:
            return rule.endpoint
    raise AssertionError(f"Endpoint not found for {method_upper} {rule_path}")


def test_chat_api_requires_session(client):
    """POST /aichat/api/chat must require an active session."""
    response = client.post("/aichat/api/chat", json={"message": "hello"})

    assert response.status_code == 401
    assert response.get_json() == {
        "success": False,
        "error": "Authentication required",
    }


def test_profiles_api_requires_session(client):
    """GET /aichat/api/profiles must require an active session."""
    response = client.get("/aichat/api/profiles")

    assert response.status_code == 401
    assert response.get_json() == {
        "success": False,
        "error": "Authentication required",
    }


def test_chat_api_internal_error_is_generic(flask_app, client):
    """POST /aichat/api/chat should not leak exception details in HTTP 500."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/chat", "POST")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    with patch.object(module, "_require_session", return_value=None), patch.object(
        module.DispatcherAichat,
        "prompt_chat",
        side_effect=RuntimeError("secret-db-details"),
    ):
        response = client.post(
            "/aichat/api/chat",
            json={"message": "hello", "history": [], "profile": "ollama_local"},
        )

    body = response.get_data(as_text=True)
    assert response.status_code == 500
    assert response.get_json() == {"success": False, "error": "Internal server error"}
    assert "secret-db-details" not in body


def test_profiles_api_internal_error_is_generic(flask_app, client):
    """GET /aichat/api/profiles should not leak exception details in HTTP 500."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/profiles", "GET")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    with patch.object(module, "_require_session", return_value=None), patch.object(
        module.DispatcherAichat,
        "get_profiles",
        side_effect=RuntimeError("secret-provider-config"),
    ):
        response = client.get("/aichat/api/profiles")

    body = response.get_data(as_text=True)
    assert response.status_code == 500
    assert response.get_json() == {"success": False, "error": "Internal server error"}
    assert "secret-provider-config" not in body


def test_chat_api_returns_400_without_json(flask_app, client):
    """POST /aichat/api/chat should reject requests without JSON body."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/chat", "POST")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    with patch.object(module, "_require_session", return_value=None):
        response = client.post(
            "/aichat/api/chat",
            data="not-json",
            content_type="text/plain",
        )

    assert response.status_code == 400
    assert response.get_json() == {"error": "No JSON data provided"}


def test_chat_api_returns_400_for_empty_message(flask_app, client):
    """POST /aichat/api/chat should reject empty messages."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/chat", "POST")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    with patch.object(module, "_require_session", return_value=None):
        response = client.post("/aichat/api/chat", json={"message": "   "})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Message is required"}


def test_chat_api_returns_400_for_invalid_history(flask_app, client):
    """POST /aichat/api/chat should reject non-list history values."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/chat", "POST")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    with patch.object(module, "_require_session", return_value=None):
        response = client.post(
            "/aichat/api/chat",
            json={"message": "hello", "history": "invalid"},
        )

    assert response.status_code == 400
    assert response.get_json() == {"error": "History must be a list"}


def test_chat_api_value_error_is_generic(flask_app, client):
    """POST /aichat/api/chat should return generic message for ValueError."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/chat", "POST")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    with patch.object(module, "_require_session", return_value=None), patch.object(
        module.DispatcherAichat,
        "prompt_chat",
        side_effect=ValueError("secret-provider-details"),
    ):
        response = client.post(
            "/aichat/api/chat",
            json={"message": "hello", "history": [], "profile": "ollama_local"},
        )

    body = response.get_data(as_text=True)
    assert response.status_code == 400
    assert response.get_json() == {"success": False, "error": "Invalid chat request"}
    assert "secret-provider-details" not in body


def test_chat_api_rate_limit_returns_429(flask_app, client):
    """POST /aichat/api/chat should enforce configured rate limit."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/chat", "POST")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    last_response = None
    with patch.object(module, "_require_session", return_value=None), patch.object(
        module.DispatcherAichat,
        "prompt_chat",
        return_value="ok",
    ):
        for _ in range(50):
            last_response = client.post(
                "/aichat/api/chat",
                json={"message": "hello", "history": [], "profile": "ollama_local"},
                environ_base={"REMOTE_ADDR": "203.0.113.10"},
            )
            if last_response.status_code == 429:
                break

    assert last_response is not None
    assert last_response.status_code == 429
    assert "Too many requests. Please try again later." in last_response.get_data(as_text=True)


def test_profiles_api_rate_limit_returns_429(flask_app, client):
    """GET /aichat/api/profiles should enforce configured rate limit."""
    endpoint = _endpoint_for_rule(flask_app, "/aichat/api/profiles", "GET")
    module = importlib.import_module(flask_app.view_functions[endpoint].__module__)

    last_response = None
    with patch.object(module, "_require_session", return_value=None), patch.object(
        module.DispatcherAichat,
        "get_profiles",
        return_value=["ollama_local"],
    ):
        for _ in range(100):
            last_response = client.get(
                "/aichat/api/profiles",
                environ_base={"REMOTE_ADDR": "203.0.113.11"},
            )
            if last_response.status_code == 429:
                break

    assert last_response is not None
    assert last_response.status_code == 429
    assert "Too many requests. Please try again later." in last_response.get_data(as_text=True)
