"""Shared pytest fixtures for component tests under src/component."""

import sys

import pytest

from app import create_app
from app.config import Config

# Ignore disabled components (directories prefixed with '_')
collect_ignore_glob = ["_*"]


class TestConfig(Config):
    """Configuration for component tests."""

    TESTING = True
    SECRET_KEY = "test_secret_key"
    DB_PWA = "sqlite:///:memory:"
    DB_SAFE = "sqlite:///:memory:"
    DB_FILES = "sqlite:///:memory:"
    MAIL_METHOD = "dummy"


@pytest.fixture(name="flask_app")
def fixture_flask_app():
    """Create a Flask app for each test."""
    app = create_app(TestConfig, debug=True)

    yield app

    for module in list(sys.modules.keys()):
        if module.startswith("component."):
            del sys.modules[module]


@pytest.fixture
def client(flask_app):  # pylint: disable=redefined-outer-name
    """Flask test client."""
    return flask_app.test_client()
