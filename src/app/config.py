"""Application configuration."""

import os
from pathlib import Path
from dotenv import dotenv_values
from constants import * # pylint: disable=wildcard-import,unused-wildcard-import

config = dotenv_values(APP_CONFIG_FILE)

class Config: # pylint: disable=too-few-public-methods
    """Configuration class."""

    BASE_DIR = SRC_DIR
    VENV_DIR = VENV_DIR

    COMP_ROUTE_ROOT = "root"

    DEBUG_EXPIRE = int(config.get('DEBUG_EXPIRE'))
    DEBUG_FILE = config.get('DEBUG_FILE')

    SECRET_KEY = config.get('SECRET_KEY')
    SITE_DOMAIN = config.get('SITE_DOMAIN')
    SITE_URL = config.get('SITE_URL')
    NEUTRAL_IPC=config.get('NEUTRAL_IPC', 'False').lower() == 'true'
    NEUTRAL_CACHE_DISABLE=config.get('NEUTRAL_CACHE_DISABLE', 'False').lower() == 'true'
    DEFAULT_SCHEMA = os.path.join(BASE_DIR, "app", "schema.json")
    TEMPLATE_NAME = config.get('TEMPLATE_NAME', 'index.ntpl')
    TEMPLATE_NAME_ERROR = config.get('TEMPLATE_NAME_ERROR', 'error.ntpl')
    TEMPLATE_HTML_MINIFY = config.get('TEMPLATE_HTML_MINIFY', 'False').lower() == 'true'
    TEMPLATE_MAIL = os.path.join(BASE_DIR, "neutral", "mail")
    MODEL_DIR = os.path.join(BASE_DIR, "model")
    COMPONENT_DIR = os.path.join(BASE_DIR, "component")

    STATIC_FOLDER = os.path.join(BASE_DIR, "..", "public")
    STATIC_CACHE_CONTROL = config.get('STATIC_CACHE_CONTROL', "max-age=14400")

    DEFAULT_LIMITS = config.get('DEFAULT_LIMITS', "3600/hour")
    STATIC_LIMITS = config.get('STATIC_LIMITS', "7200/hour")
    SIGNIN_LIMITS = config.get('SIGNIN_LIMITS', "3 per 30 minutes")
    SIGNUP_LIMITS = config.get('SIGNUP_LIMITS', "5 per 30 minutes")
    SIGNREMINDER_LIMITS = config.get('SIGNREMINDER_LIMITS', "5 per 30 minutes")
    SIGNT_LIMITS = config.get('SIGNT_LIMITS', "5 per 30 minutes")

    VALIDATE_SIGNUP = config.get('VALIDATE_SIGNUP', 'True').lower() == 'true'

    LANG_KEY = "lang"
    THEME_KEY = "theme"
    THEME_COLOR_KEY = "theme_color"
    TAB_CHANGES_KEY = "tabstatus"

    SESSION_KEY = "SESSION"
    SESSION_TOKEN_LENGTH = int(config.get('SESSION_TOKEN_LENGTH', 32))
    SESSION_IDLE_EXPIRES_SECONDS = int(config.get('SESSION_IDLE_EXPIRES_SECONDS', 2592000))
    UTOKEN_KEY = "USER_SECURITY"
    UTOKEN_IDLE_EXPIRES_SECONDS = int(config.get('UTOKEN_IDLE_EXPIRES_SECONDS', 14400))
    FTOKEN_EXPIRES_SECONDS = int(config.get('FTOKEN_EXPIRES_SECONDS', 240))
    PIN_EXPIRES_SECONDS = int(config.get('PIN_EXPIRES_SECONDS', 86400))
    TOKEN_LENGTH = int(config.get('TOKEN_LENGTH', 32))
    PIN_MIN = int(config.get('PIN_MIN', 100000))
    PIN_MAX = int(config.get('PIN_MAX', 999999))

    UUID_MIN = int(config.get('UUID_MIN', 1000000000000))
    UUID_MAX = int(config.get('UUID_MAX', 9999999999999))

    MAIL_METHOD = config.get('MAIL_METHOD', 'smtp')
    MAIL_TO_FILE = config.get('MAIL_TO_FILE', '/tmp/test_mail.html')
    MAIL_SERVER = config.get('MAIL_SERVER', '')
    MAIL_PORT = config.get('MAIL_PORT', 587)
    MAIL_USE_TLS = config.get('MAIL_USE_TLS', False)
    MAIL_USERNAME = config.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = config.get('MAIL_PASSWORD', '')
    MAIL_SENDER = config.get('MAIL_SENDER', '')
    MAIL_RETURN_PATH = config.get('MAIL_RETURN_PATH', '')

    # Lower number, higher priority
    DISABLED = {
        DELETED: 10,
        UNCONFIRMED: 100,
        UNVALIDATED: 200,
        SPAM: 500
    }

    DISABLED_KEY = {str(v): k for k, v in DISABLED.items()}

    MAIN_EMAIL = {
        'true': 1,
        'false': 0
    }

    SESSION_OPEN = {
        'true': 1,
        'false': 0
    }

    # Database
    DB_PWA_TYPE = config.get('DB_PWA_TYPE', 'sqlite').lower()
    DB_PWA_NAME = config.get('DB_PWA_NAME', 'pwa.db')
    DB_PWA_USER = config.get('DB_PWA_USER', '')
    DB_PWA_PASSWORD = config.get('DB_PWA_PASSWORD', '')
    DB_PWA_HOST = config.get('DB_PWA_HOST', 'localhost')
    DB_PWA_PORT = config.get('DB_PWA_PORT', '')
    DB_PWA_PATH = config.get('DB_PWA_PATH', '') or os.path.join(BASE_DIR, "..", 'storage')  # SQLite
    DB_SAFE_TYPE = config.get('DB_SAFE_TYPE', 'sqlite').lower()
    DB_SAFE_NAME = config.get('DB_SAFE_NAME', 'safe.db')
    DB_SAFE_USER = config.get('DB_SAFE_USER', '')
    DB_SAFE_PASSWORD = config.get('DB_SAFE_PASSWORD', '')
    DB_SAFE_HOST = config.get('DB_SAFE_HOST', 'localhost')
    DB_SAFE_PORT = config.get('DB_SAFE_PORT', '')
    DB_SAFE_PATH = config.get('DB_SAFE_PATH', '') or os.path.join(BASE_DIR, "..", 'storage')  # SQLite
    DB_FILES_TYPE = config.get('DB_FILES_TYPE', 'sqlite').lower()
    DB_FILES_NAME = config.get('DB_FILES_NAME', 'files.db')
    DB_FILES_USER = config.get('DB_FILES_USER', '')
    DB_FILES_PASSWORD = config.get('DB_FILES_PASSWORD', '')
    DB_FILES_HOST = config.get('DB_FILES_HOST', 'localhost')
    DB_FILES_PORT = config.get('DB_FILES_PORT', '')
    DB_FILES_PATH = config.get('DB_FILES_PATH', '') or os.path.join(BASE_DIR, "..", 'storage')  # SQLite

    if DB_PWA_TYPE == 'sqlite':
        DB_PWA = f"sqlite:///{Path(DB_PWA_PATH).joinpath(f'{DB_PWA_NAME}')}"
    else:
        DB_PWA = f"{DB_PWA_TYPE}://{DB_PWA_USER}:{DB_PWA_PASSWORD}@{DB_PWA_HOST}:{DB_PWA_PORT}/{DB_PWA_NAME}"

    if DB_SAFE_TYPE == 'sqlite':
        DB_SAFE = f"sqlite:///{Path(DB_SAFE_PATH).joinpath(f'{DB_SAFE_NAME}')}"
    else:
        DB_SAFE = f"{DB_SAFE_TYPE}://{DB_SAFE_USER}:{DB_SAFE_PASSWORD}@{DB_SAFE_HOST}:{DB_SAFE_PORT}/{DB_SAFE_NAME}"

    if DB_FILES_TYPE == 'sqlite':
        DB_FILES = f"sqlite:///{Path(DB_FILES_PATH).joinpath(f'{DB_FILES_NAME}')}"
    else:
        DB_FILES = f"{DB_FILES_TYPE}://{DB_FILES_USER}:{DB_FILES_PASSWORD}@{DB_FILES_HOST}:{DB_FILES_PORT}/{DB_FILES_NAME}"
