"""Core dispatcher module."""

from app.config import Config
from constants import DELETED, MODERATED, SPAM, UNCONFIRMED, UNVALIDATED
from utils.tokens import (
    utoken_extract,
    utoken_update,
    ltoken_create,
)
from utils.sbase64url import sbase64url_md5
from utils.nonce import get_nonce
from .schema import Schema
from .session import Session
from .user import User
from .template import Template


class Dispatcher: # pylint: disable=too-many-instance-attributes
    """Main request dispatcher class."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None):
        """Initialize dispatcher with request, route and optional tokens."""
        self.req = req
        self._comp_route = f'{Config.COMP_ROUTE_ROOT}/{comp_route}'.strip("/")
        self._neutral_route = neutral_route
        self._ltoken = ltoken
        self.schema = Schema(self.req)
        self.schema_data = self.schema.properties['data']
        self.schema_local_data = self.schema.properties['inherit']['data']
        self.ajax_request = self.schema_data['CONTEXT']['HEADERS'].get("Requested-With-Ajax") or False  # pylint: disable=line-too-long
        self.session = Session(self.schema_data['CONTEXT']['SESSION'])
        self.user = User()
        self.view = Template(self.schema)
        self._set_current_comp()
        self.common()

    def _set_current_comp(self) -> None:
        self.schema_data['CURRENT_COMP_ROUTE'] = self._comp_route
        self.schema_data['CURRENT_COMP_ROUTE_SANITIZED'] = self._comp_route.replace("/", ":")
        self.schema_data['CURRENT_NEUTRAL_ROUTE'] = self._neutral_route or self.schema_data['CURRENT_NEUTRAL_ROUTE']  # pylint: disable=line-too-long
        name, uuid = self.extract_comp_from_path(self.schema_data['CURRENT_NEUTRAL_ROUTE'])
        self.schema_data['CURRENT_COMP_NAME'] = name
        self.schema_data['CURRENT_COMP_UUID'] = uuid

    def common(self) -> None:
        """Perform common initialization tasks for all requests."""
        session_id, session_cookie = self.session.get()
        self.schema_data['CONTEXT']['SESSION'] = session_id
        session_data = self.session.get_session_properties() if session_id else {}
        self.schema_data['CONTEXT']['SESSION_DATA'] = session_data if isinstance(session_data, dict) else {}
        self.schema_data['CURRENT_USER'] = self._build_current_user(self.schema_data['CONTEXT']['SESSION_DATA'])
        self.schema_data['HAS_SESSION'] = "true" if session_id else None
        self.schema_data['HAS_SESSION_STR'] = "true" if session_id else "false"
        self.schema_data['CSP_NONCE'] = get_nonce()
        self.parse_utoken()
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

    def _build_current_user(self, session_data: dict) -> dict:
        """Build template-safe current user view from session data.

        Important for templates:
        - `CURRENT_USER.roles` is a sparse map that only includes roles the user has.
          Example:
          {
              "role_admin": "role_admin",
              "role_dev": "role_dev"
          }
        - Missing roles are omitted completely. Do not emit keys with boolean false.
          This must NOT be produced:
          {
              "role_admin": false,
              "role_dev": false
          }
        """
        current_user = {
            "auth": False,
            "id": "",
            "roles": {},
            "status": {
                DELETED: False,
                UNCONFIRMED: False,
                UNVALIDATED: False,
                MODERATED: False,
                SPAM: False,
            },
            "profile": {
                "alias": "",
                "locale": "",
            },
        }

        if not isinstance(session_data, dict):
            return current_user

        user_data = session_data.get("user_data", {})
        if not isinstance(user_data, dict):
            return current_user

        user_id = str(user_data.get("userId") or "")
        if not user_id:
            return current_user

        current_user["auth"] = True
        current_user["id"] = user_id

        roles = user_data.get("roles", [])
        if user_id:
            db_roles = self.user.get_roles(user_id)
            if db_roles:
                roles = db_roles

        role_map = {}
        for role in roles:
            role_code = str(role).strip().lower()
            if role_code:
                # Sparse role map: only assigned roles are present as keys.
                role_key = f"role_{role_code}"
                role_map[role_key] = role_key
        current_user["roles"] = role_map

        user_disabled = user_data.get("user_disabled", {})
        if isinstance(user_disabled, dict):
            for key in current_user["status"]:
                current_user["status"][key] = bool(user_disabled.get(key))

        current_user["profile"]["alias"] = str(user_data.get("alias") or "")
        current_user["profile"]["locale"] = str(user_data.get("locale") or "")

        return current_user

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
