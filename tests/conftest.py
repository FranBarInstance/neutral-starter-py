"""
Pytest configuration and fixtures.
"""

import sys

import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    """
    Configuration for testing purposes.
    Uses in-memory databases and dummy mail settings.
    """

    TESTING = True
    SECRET_KEY = "test_secret_key"
    # Use memory databases for isolation
    DB_PWA = "sqlite:///:memory:"
    DB_SAFE = "sqlite:///:memory:"
    DB_IMAGE = "sqlite:///:memory:"
    # Disable features that might require external services
    MAIL_METHOD = "dummy"


@pytest.fixture(name="flask_app")
def fixture_flask_app():
    """
    Create and configure a new Flask app instance for each test.
    """
    # Setup
    app = create_app(TestConfig, debug=True)

    # In a real scenario we might need to initialize the DB here if the app doesn't do it
    # automatically on request or startup.
    # Given the 'neutral' framework likely handles it, we assume create_app does enough
    # for basic tests.

    yield app

    # Teardown: Remove component modules to force reload in next test
    # (fixing blueprint route registration)
    for module in list(sys.modules.keys()):
        if module.startswith("component."):
            del sys.modules[module]


@pytest.fixture
def client(flask_app):
    """
    A test client for the app.
    """
    return flask_app.test_client()


@pytest.fixture
def runner(flask_app):
    """
    A test CLI runner for the app.
    """
    return flask_app.test_cli_runner()
