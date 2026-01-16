"""Core dispatcher module."""

from app.config import Config
from utils.tokens import (
    utoken_extract,
    utoken_update,
    # ftoken_create,
    ltoken_create,
    # ltoken_check
)
from utils.sbase64url import sbase64url_md5
from .schema import Schema
from .session import Session
from .user import User
from .template import Template


class Dispatcher:
    """Main request dispatcher class."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None, ftoken_field_name=None):
        """Initialize dispatcher with request, route and optional tokens."""
        self.req = req
        self._comp_route = f'{Config.COMP_ROUTE_ROOT}/{comp_route}'.strip("/")
        self._neutral_route = neutral_route
        self._ltoken = ltoken
        self._ftoken_name = ftoken_field_name
        self.schema = Schema(self.req)
        self.schema_data = self.schema.properties['data']
        self.schema_local_data = self.schema.properties['inherit']['data']
        self.ajax_request = self.schema_data['CONTEXT']['HEADERS'].get("Requested-With-Ajax") or False
        self.session = Session(self.schema_data['CONTEXT']['SESSION'])
        self.user = User()
        self.view = Template(self.schema)
        self._set_current_comp()
        self.common()

    def _set_current_comp(self) -> None:
        self.schema_data['CURRENT_COMP_ROUTE'] = self._comp_route
        self.schema_data['CURRENT_COMP_ROUTE_SANITIZED'] = self._comp_route.replace("/", ":")
        self.schema_data['CURRENT_NEUTRAL_ROUTE'] = self._neutral_route or self.schema_data['CURRENT_NEUTRAL_ROUTE']
        name, uuid = self.extract_comp_from_path(self.schema_data['CURRENT_NEUTRAL_ROUTE'])
        self.schema_data['CURRENT_COMP_NAME'] = name
        self.schema_data['CURRENT_COMP_UUID'] = uuid

    def common(self) -> None:
        """Perform common initialization tasks for all requests."""
        session_id, session_cookie = self.session.get()
        self.schema_data['CONTEXT']['SESSION'] = session_id
        self.schema_data['HAS_SESSION'] = "true" if session_id else None
        self.parse_utoken()
        self.schema_data['script_container_hash'] = sbase64url_md5(self.schema_data['CONTEXT']['UTOKEN'])
        self.schema_data['LTOKEN'] = ltoken_create(self.schema_data['CONTEXT']['UTOKEN'])
        if not self.ajax_request:
            self.cookie_tab_changes()
            self.view.add_cookie({
                **session_cookie,
                Config.THEME_KEY: {
                    "key": Config.THEME_KEY,
                    "value":  self.schema_local_data['current']['theme']['theme'],
                },
                Config.THEME_COLOR_KEY: {
                    "key": Config.THEME_COLOR_KEY,
                    "value":  self.schema_local_data['current']['theme']['color'],
                },
                Config.LANG_KEY: {
                    "key": Config.LANG_KEY,
                    "value": self.schema.properties['inherit']['locale']['current'],
                }
            })

    def cookie_tab_changes(self) -> None:
        """Detect when user opens new tabs/windows using token hashing."""
        # Create unique fingerprint of current session state
        detect = "start"
        detect += self.schema_data['CONTEXT'].get("UTOKEN") or "none"
        detect += self.schema_data['CONTEXT'].get("SESSION") or "none"
        self.view.add_cookie({
            Config.TAB_CHANGES_KEY: {
                "key": Config.TAB_CHANGES_KEY,
                "value": sbase64url_md5(detect),
            }
        })

    def parse_utoken(self) -> None:
        """Handle user token operations based on request type.
           It is not updated if you are in the middle of a process, such as a form.
        """
        # Only update token if request is GET and not an AJAX request
        if self.req.method == 'GET' and not self.ajax_request:
            utoken_token, utoken_cookie = utoken_update(self.req.cookies.get(Config.UTOKEN_KEY))
        else:
            utoken_token, utoken_cookie = utoken_extract(self.req.cookies.get(Config.UTOKEN_KEY))

        self.schema_data['CONTEXT']['UTOKEN'] = utoken_token

        if not self.ajax_request:
            self.view.add_cookie({**utoken_cookie})

    def extract_comp_from_path(self, path) -> tuple[str | None, str | None]:
        """Extract component name and UUID from path."""

        if "/component/cmp_" in path:
            part = path.split("component/cmp_")[1]
            name = 'cmp_' + part.split('/')[0]
        else:
            return None, None

        return name, self.schema_data['COMPONENTS_MAP_BY_NAME'][name]
