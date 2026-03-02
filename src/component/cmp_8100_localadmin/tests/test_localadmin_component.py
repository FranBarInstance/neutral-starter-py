"""Tests for localadmin component."""

_BP_NAME = "bp_cmp_8100_localadmin"


def _route_prefix(flask_app) -> str:
    return flask_app.blueprints[_BP_NAME].url_prefix or ""


def _route(flask_app, suffix: str) -> str:
    return f"{_route_prefix(flask_app)}{suffix}"


def _extract_csrf(html: str) -> str:
    marker = 'name="csrf_token" value="'
    start = html.find(marker)
    assert start != -1
    start += len(marker)
    end = html.find('"', start)
    assert end != -1
    return html[start:end]


def test_localadmin_blueprint_registered(flask_app):
    """Component blueprint should be registered."""
    assert _BP_NAME in flask_app.blueprints


def test_localadmin_root_message(client):
    """Main route should show future message."""
    response = client.get(_route(client.application, "/"), environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert response.status_code == 200
    assert b"future development tools" in response.data
    assert b"/local-admin/login/ajax" in response.data


def test_localadmin_login_and_role_variable(client):
    """Valid login should activate isolated session and role variable."""
    client.application.config["DEV_ADMIN_USER"] = "admin"
    client.application.config["DEV_ADMIN_PASSWORD"] = "secret"

    page = client.get(_route(client.application, "/login"), environ_base={"REMOTE_ADDR": "127.0.0.1"})
    assert page.status_code == 200

    ajax_form = client.get(
        _route(client.application, "/login/ajax"),
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert ajax_form.status_code == 200
    csrf = _extract_csrf(ajax_form.get_data(as_text=True))

    response = client.post(
        _route(client.application, "/login"),
        data={
            "action": "login",
            "username": "admin",
            "password": "secret",
            "csrf_token": csrf,
        },
        environ_base={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest-agent"},
    )
    assert response.status_code == 200
    assert b"dev_admin_role=true" in response.data

    set_cookie_headers = response.headers.getlist("Set-Cookie")
    assert any("DEV_ADMIN_SESSION=" in item for item in set_cookie_headers)
    assert any("dev_admin_role=true" in item for item in set_cookie_headers)


def test_localadmin_rejects_invalid_csrf(client):
    """POST login must reject invalid CSRF token."""
    client.application.config["DEV_ADMIN_USER"] = "admin"
    client.application.config["DEV_ADMIN_PASSWORD"] = "secret"

    response = client.post(
        _route(client.application, "/login"),
        data={
            "action": "login",
            "username": "admin",
            "password": "secret",
            "csrf_token": "bad-token",
        },
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert response.status_code == 200
    assert b"Invalid CSRF token." in response.data


def test_localadmin_login_form_allows_direct_and_ajax(client):
    """Login form endpoint should support direct and AJAX access."""
    client.application.config["DEV_ADMIN_USER"] = "admin"
    client.application.config["DEV_ADMIN_PASSWORD"] = "secret"

    direct = client.get(
        _route(client.application, "/login/ajax"),
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert direct.status_code == 200

    allowed = client.get(
        _route(client.application, "/login/ajax"),
        headers={"Requested-With-Ajax": "fetch"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert allowed.status_code == 200
    assert b"localadmin-login-form" in allowed.data


def test_localadmin_logout_ajax_requires_header_and_clears_cookie(client):
    """Logout AJAX should require header and close isolated session."""
    client.application.config["DEV_ADMIN_USER"] = "admin"
    client.application.config["DEV_ADMIN_PASSWORD"] = "secret"

    login_form = client.get(
        _route(client.application, "/login/ajax"),
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    csrf = _extract_csrf(login_form.get_data(as_text=True))

    logged = client.post(
        _route(client.application, "/login/ajax"),
        data={
            "action": "login",
            "username": "admin",
            "password": "secret",
            "csrf_token": csrf,
        },
        environ_base={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest-agent"},
    )
    assert logged.status_code == 200

    forbidden = client.post(
        _route(client.application, "/logout/ajax"),
        data={"csrf_token": csrf},
        environ_base={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest-agent"},
    )
    assert forbidden.status_code == 403

    allowed = client.post(
        _route(client.application, "/logout/ajax"),
        data={"csrf_token": csrf},
        headers={"Requested-With-Ajax": "fetch"},
        environ_base={"REMOTE_ADDR": "127.0.0.1", "HTTP_USER_AGENT": "pytest-agent"},
    )
    assert allowed.status_code == 200
    assert b"Session closed." in allowed.data
    assert b"localadmin-login-form" in allowed.data

    set_cookie_headers = allowed.headers.getlist("Set-Cookie")
    assert any("DEV_ADMIN_SESSION=" in item and "Max-Age=0" in item for item in set_cookie_headers)
