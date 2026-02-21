# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Pytest fixtures for sign component tests."""

import os
import sys
from pathlib import Path

import pytest

from app import create_app
from app.bootstrap_db import bootstrap_databases
from app.config import Config

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_COMP_DIR = os.path.dirname(_BASE_DIR)
_ROUTE_DIR = os.path.join(_COMP_DIR, "route")
_FTOKEN_LIB_DIR = os.path.join(
    os.path.dirname(_COMP_DIR),
    "cmp_2300_ftoken",
    "lib",
)

for path in (_ROUTE_DIR, _FTOKEN_LIB_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

@pytest.fixture(name="flask_app")
def fixture_flask_app(tmp_path):
    """Create a Flask app for each test."""
    pwa_db = Path(tmp_path) / "pwa_test.db"
    safe_db = Path(tmp_path) / "safe_test.db"
    files_db = Path(tmp_path) / "files_test.db"

    class TestConfig(Config):
        """Configuration for component tests."""

        TESTING = True
        SECRET_KEY = "test_secret_key"
        DB_PWA = f"sqlite:///{pwa_db}"
        DB_SAFE = f"sqlite:///{safe_db}"
        DB_FILES = f"sqlite:///{files_db}"
        MAIL_METHOD = "dummy"

    bootstrap_databases(
        db_pwa_url=TestConfig.DB_PWA,
        db_pwa_type=TestConfig.DB_PWA_TYPE,
        db_safe_url=TestConfig.DB_SAFE,
        db_safe_type=TestConfig.DB_SAFE_TYPE,
        db_files_url=TestConfig.DB_FILES,
        db_files_type=TestConfig.DB_FILES_TYPE,
    )

    app = create_app(TestConfig, debug=True)

    yield app

    for module in list(sys.modules.keys()):
        if module.startswith("component."):
            del sys.modules[module]


@pytest.fixture
def client(flask_app):  # pylint: disable=redefined-outer-name
    """Flask test client."""
    return flask_app.test_client()
