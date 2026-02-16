"""
Basic tests for application setup and routing.
"""

from app import create_app
from app.config import Config


def test_app_is_created(flask_app):
    """Test that the app instance is created with the correct name."""
    assert flask_app.name == "app"


def test_config_is_loaded(flask_app):
    """Test that the test configuration is loaded correctly."""
    assert flask_app.config["TESTING"] is True
    assert flask_app.config["SECRET_KEY"] == "test_secret_key"


def test_index_page(client):
    """
    Test routing for index page.
    Verifies that / is accessible.
    """
    response = client.get("/")
    assert response.status_code == 200


def test_rejects_disallowed_host(client):
    """Requests with disallowed Host must return 400."""
    response = client.get("/", headers={"Host": "evil.example"})
    assert response.status_code == 400


def test_accepts_allowed_host(client):
    """Requests with allowed Host must continue normally."""
    response = client.get("/", headers={"Host": "localhost"})
    assert response.status_code == 200


def test_referrer_policy_header_default(client):
    """Referrer-Policy must be sent with the configured default value."""
    response = client.get("/")
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_permissions_policy_header_absent_by_default(client):
    """Permissions-Policy should not be sent unless explicitly configured."""
    response = client.get("/")
    assert response.headers.get("Permissions-Policy") is None


def test_permissions_policy_header_when_configured():
    """Permissions-Policy should be sent when configured in app settings."""

    class _HeaderConfig(Config):
        TESTING = True
        SECRET_KEY = "test_secret_key"
        DB_PWA = "sqlite:///:memory:"
        DB_SAFE = "sqlite:///:memory:"
        DB_FILES = "sqlite:///:memory:"
        MAIL_METHOD = "dummy"
        PERMISSIONS_POLICY = "geolocation=(), microphone=(), camera=(), payment=()"

    app = create_app(_HeaderConfig, debug=True)
    with app.test_client() as local_client:
        response = local_client.get("/")
        assert (
            response.headers.get("Permissions-Policy")
            == "geolocation=(), microphone=(), camera=(), payment=()"
        )


def test_components_loaded(flask_app):
    """Test that components are correctly identified and loaded."""
    if hasattr(flask_app, "components") and flask_app.components:
        print("\nLoaded Components:", list(flask_app.components.collection.keys()))
        assert len(flask_app.components.collection) > 0
