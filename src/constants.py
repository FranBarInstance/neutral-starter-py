# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""constants"""

import os

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(SRC_DIR, '..', '.venv')
TMP_DIR = os.path.join(SRC_DIR, '..', 'tmp')
APP_CONFIG_FILE = os.getenv('APP_CONFIG_FILE', os.path.join(SRC_DIR, '..', 'config', '.env'))

SECONDS_MINUTE = 60
SECONDS_HOUR = 3600
SECONDS_DAY = 86400
SECONDS_WEEK = 604800
SECONDS_MONTH = 2592000

UUID_MIN_LEN = 10
UUID_MAX_LEN = 50

DELETED = 'deleted'
UNCONFIRMED = 'unconfirmed'
UNVALIDATED = 'unvalidated'
MODERATED = 'moderated'
PIN_TARGET_REMINDER = "reminder"
USER_EXISTS = "USER_EXISTS"

SPAM = 'spam'
