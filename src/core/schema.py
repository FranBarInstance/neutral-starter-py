"""Fill the schema with default values"""

import copy
from http.cookies import SimpleCookie

import woothee
from flask import current_app

from app.config import Config
from constants import *  # pylint: disable=wildcard-import,unused-wildcard-import
from utils.utils import get_ip, merge_dict


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
        self._populate_context()
        self._negotiate_language()
        self.set_theme()

    def _default(self) -> None:
        self.properties = copy.deepcopy(current_app.components.schema)
        self.data = self.properties['data']
        self.local_data = self.properties['inherit']['data']
        self.properties['config']['cache_disable'] = Config.NEUTRAL_CACHE_DISABLE
        self.properties['config']['cache_dir'] = TMP_DIR

        # Debug
        if current_app.debug:
            self.properties['config']['debug_expire'] = Config.DEBUG_EXPIRE
            self.properties['config']['debug_file'] = Config.DEBUG_FILE

        # The neutral-ipc process has a different user, therefore different permissions
        if Config.NEUTRAL_IPC:
            self.properties['config']['cache_prefix'] += "-ipc"

    def _general_data(self) -> None:
        template_dir = self.data['current']['template']['dir']
        self.data['BASE_DIR'] = Config.BASE_DIR
        self.data['VENV_DIR'] = Config.VENV_DIR
        self.data['TEMPLATE_LAYOUT'] = os.path.join(template_dir, 'layout', Config.TEMPLATE_NAME)
        self.data['TEMPLATE_ERROR'] = os.path.join(template_dir, 'layout', Config.TEMPLATE_NAME_ERROR)
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
        self.data['dispatch_result'] = False

    def _session(self) -> None:
        self.data['CONTEXT']['SESSION_DATA'] = {}
        self.data['CONTEXT']['SESSION'] = self.req.cookies.get(Config.SESSION_KEY, None)

    def _populate_context(self) -> None:
        self.data['CONTEXT']['METHOD'] = self.req.method
        self.data['CONTEXT']['REMOTE_ADDR'] = get_ip()
        self.data['CONTEXT']['PATH'] = self.req.path
        self.data['CONTEXT']['UA'] = woothee.parse(self.req.headers.get('User-Agent'))

        for key, value in self.req.args.items():
            self.data['CONTEXT']['GET'][key] = value

        if self.req.method == "POST":
            for key, value in self.req.form.items():
                self.data['CONTEXT']['POST'][key] = value

        for key, value in self.req.headers.items():
            self.data['CONTEXT']['HEADERS'][key] = value

        if self.req.headers.get('Cookie'):
            cookie = SimpleCookie(self.req.headers.get('Cookie'))
            for key, morsel in cookie.items():
                self.data['CONTEXT']['COOKIES'][key] = morsel.value

        host = self.req.headers.get('Host')
        if host:
            self.data['current']['site']['host'] = host
            self.data['current']['site']['url'] = self.req.scheme + "://" + host
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
            or self.local_data['current']['theme']['theme']
        )

        new_theme_color = (
            color
            or self.data['CONTEXT']['GET'].get(Config.THEME_COLOR_KEY)
            or self.data['CONTEXT']['COOKIES'].get(Config.THEME_COLOR_KEY)
            or self.local_data['current']['theme']['color']
        )

        if new_theme in self.local_data['current']['theme']['allow_themes']:
            self.local_data['current']['theme']['theme'] = new_theme

        if new_theme_color in self.local_data['current']['theme']['allow_colors']:
            self.local_data['current']['theme']['color'] = new_theme_color

    def merge(self, new_dict):
        """Merge a new dictionary recursively into self.properties"""
        merge_dict(self.properties, new_dict)
