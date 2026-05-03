"""Fill the schema with default values"""

import os
from functools import lru_cache

import orjson
import woothee
from flask import current_app

from app.config import Config
from constants import TMP_DIR, RBAC_DEFAULT_ROLES
from utils.utils import get_ip, merge_dict
from utils.network import normalize_host, is_allowed_host
from .session_dev import SessionDev


@lru_cache(maxsize=128)
def _parse_ua_cached(ua_string: str) -> dict:
    """Cache woothee UA parsing results."""
    return woothee.parse(ua_string)


class Schema:
    """Schema"""

    def __init__(self, req):
        self.req = req
        self.context = {}
        self.headers = req.headers
        self.properties = {}
        self.data = {}
        self.local_data = {}
        self._default()
        self._general_data()
        self._session()
        self._session_dev()
        self._populate_context()
        self._negotiate_language()
        self.set_theme()

    def _default(self) -> None:
        self.properties = orjson.loads(current_app.schema_json)  # pylint: disable=no-member
        self.data = self.properties['data']
        self.local_data = self.properties['inherit']['data']
        self.properties['config']['cache_disable'] = Config.NEUTRAL_CACHE_DISABLE
        self.properties['config']['cache_dir'] = TMP_DIR

        # Debug
        if current_app.debug:
            debug_expire = Config.DEBUG_EXPIRE if Config.DEBUG_EXPIRE > 0 else ""
            self.properties['config']['debug_expire'] = debug_expire
            self.properties['config']['debug_file'] = Config.DEBUG_FILE

        # The neutral-ipc process has a different user, therefore different permissions
        if Config.NEUTRAL_IPC:
            self.properties['config']['cache_prefix'] += "-ipc"

    def _general_data(self) -> None:
        template_dir = self.data['current']['template']['dir']
        self.data['BASE_DIR'] = Config.BASE_DIR
        self.data['VENV_DIR'] = Config.VENV_DIR
        self.data['TEMPLATE_LAYOUT'] = os.path.join(template_dir, 'layout', Config.TEMPLATE_NAME)
        self.data['TEMPLATE_ERROR'] = os.path.join(template_dir, 'layout', Config.TEMPLATE_NAME_ERROR)  # pylint: disable=line-too-long
        
        # Mail template layout
        if 'mail_template' in self.data['current']:
            mail_template_dir = self.data['current']['mail_template']['dir']
            self.data['MAIL_TEMPLATE_LAYOUT'] = os.path.join(
                mail_template_dir, 'layout', Config.MAIL_TEMPLATE_NAME
            )

        self.data['TEMPLATE_MAIL'] = Config.TEMPLATE_MAIL
        self.data['FTOKEN_EXPIRES_SECONDS'] = Config.FTOKEN_EXPIRES_SECONDS
        self.data['LANG_KEY'] = Config.LANG_KEY
        self.data['THEME_KEY'] = Config.THEME_KEY
        self.data['THEME_COLOR_KEY'] = Config.THEME_COLOR_KEY
        self.data['UTOKEN_KEY'] = Config.UTOKEN_KEY
        self.data['TAB_CHANGES_KEY'] = Config.TAB_CHANGES_KEY
        self.data['DISABLED'] = Config.DISABLED
        self.data['DISABLED_KEY'] = Config.DISABLED_KEY
        self.data['COMPONENT_DIR'] = Config.COMPONENT_DIR
        self.data['RBAC_DEFAULT_ROLES'] = {
            item[0]: {
                "name": item[1],
                "description": item[2],
            }
            for item in RBAC_DEFAULT_ROLES
        }
        self.data['dispatch_result'] = False

    def _session(self) -> None:
        self.data['CONTEXT']['SESSION_DATA'] = {}
        self.data['CONTEXT']['SESSION'] = self.req.cookies.get(Config.SESSION_KEY, None)

    def _session_dev(self) -> None:
        session_dev = SessionDev()
        dev_session_ok = session_dev.check_session()
        self.data['SESSION_DEV_DATA'] = session_dev.get_session_data()
        self.data['HAS_SESSION_DEV'] = "true" if dev_session_ok else None
        self.data['HAS_SESSION_DEV_STR'] = "true" if dev_session_ok else "false"

    def _populate_context(self) -> None:
        self.data['CONTEXT']['METHOD'] = self.req.method
        self.data['CONTEXT']['REMOTE_ADDR'] = get_ip()
        self.data['CONTEXT']['PATH'] = self.req.path

        ua_string = self.req.headers.get('User-Agent', '')
        self.data['CONTEXT']['UA'] = _parse_ua_cached(ua_string)

        self.data['CONTEXT']['GET'].update(self.req.args)

        if self.req.method == "POST":
            self.data['CONTEXT']['POST'].update(self.req.form)
            for field_name in self.req.files.keys():
                self.data['CONTEXT']['FILES'][field_name] = self.req.files.getlist(field_name)

        self.data['CONTEXT']['HEADERS'].update(self.req.headers)

        # Use Flask's pre-parsed cookies instead of redundant SimpleCookie
        self.data['CONTEXT']['COOKIES'].update(self.req.cookies)

        raw_host = (self.req.host or self.req.headers.get('Host') or '').strip().lower()
        normalized_host = normalize_host(raw_host)

        if normalized_host and is_allowed_host(normalized_host, Config.ALLOWED_HOSTS):
            self.data['current']['site']['host'] = raw_host
            self.data['current']['site']['url'] = self.req.scheme + "://" + raw_host
        else:
            self.data['current']['site']['host'] = Config.SITE_DOMAIN
            self.data['current']['site']['url'] = Config.SITE_URL


    def _negotiate_language(self) -> None:
        languages = self.data['current']['site']['languages']
        self.properties['inherit']['locale']['current'] = (
            self.data['CONTEXT']['GET'].get(Config.LANG_KEY)
            or self.data['CONTEXT']['COOKIES'].get(Config.LANG_KEY)
            or self.req.accept_languages.best_match(languages)
            or ""
        )

        if self.properties['inherit']['locale']['current'] not in languages:
            self.properties['inherit']['locale']['current'] = languages[0]

        self.data['CONTEXT']['LANGUAGE'] = self.properties['inherit']['locale'][
            'current'
        ]

    def set_theme(self, theme=None, color=None) -> None:
        """Set current theme and color"""

        new_theme = (
            theme
            or self.data['CONTEXT']['GET'].get(Config.THEME_KEY)
            or self.data['CONTEXT']['COOKIES'].get(Config.THEME_KEY)
            or self.data['current']['theme']['theme']
        )

        new_theme_color = (
            color
            or self.data['CONTEXT']['GET'].get(Config.THEME_COLOR_KEY)
            or self.data['CONTEXT']['COOKIES'].get(Config.THEME_COLOR_KEY)
            or self.data['current']['theme']['color']
        )

        if new_theme in self.data['current']['theme']['allow_themes']:
            self.data['current']['theme']['theme'] = new_theme

        if new_theme_color in self.data['current']['theme']['allow_colors']:
            self.data['current']['theme']['color'] = new_theme_color

    def merge(self, new_dict):
        """Merge a new dictionary recursively into self.properties"""
        merge_dict(self.properties, new_dict)
