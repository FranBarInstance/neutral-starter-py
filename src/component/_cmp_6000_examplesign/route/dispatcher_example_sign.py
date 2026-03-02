"""Dispatcher for example sign-related forms."""

from ftoken_0yt2sa import ftoken_check
from core.dispatcher_form import DispatcherForm


# sign-in fake data
# DO NOT DO THIS IN A REAL CASE
EMAIL = 'email@example.com'
PASSWORD = '12345678'


class DispatcherFormExampleSign(DispatcherForm):
    """Base class for handling authentication form validation logic."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        req,
        comp_route,
        neutral_route=None,
        ltoken=None,
        form_name="_unused_form",
        ftoken_field_name=None,
    ):
        super().__init__(req, comp_route, neutral_route, ltoken, form_name)
        self._ftoken_field_name = ftoken_field_name
        self.error["form"]["ftoken"] = None
        self.schema_data["dispatch_result"] = True
        self.schema_data["FAKE_SESSION"] = self.get_session()

    def form_get(self) -> bool:
        """Validate GET request for authentication forms."""
        return self.validate_get()

    def validate_get(self) -> bool:
        """Validate GET request parameters and session state."""

        if not self.valid_form_tokens_get():
            return False

        return True

    def validate_post(self, error_prefix) -> bool:
        """Validate POST request for authentication forms."""

        if not self.valid_form_tokens_post():
            return False

        if not self.valid_form_validation():
            return False

        if self.any_error_form_fields(error_prefix):
            return False

        return True

    def validate_post_ftoken(self) -> bool:
        """Validate POST request for authentication forms."""

        # ftoken field error
        if not ftoken_check(
            self._ftoken_field_name,
            self.schema_data["CONTEXT"]["POST"],
            self.schema_data["CONTEXT"]["UTOKEN"],
        ):
            self.error["form"]["ftoken"] = "true"
            return False

        return True

    def get_session(self) -> bool | str:
        """Get the session from cookie."""
        return self.req.cookies.get("fake-login-session")

    def create_session(self) -> bool:
        """Create a new user session after successful authentication."""

        self.view.add_cookie({
            "fake-login-session": {
                "key": "fake-login-session",
                "value":  "true",
                "path": "/"
            }
        })

        return True

    def close_session(self) -> bool:
        """Close the user session."""

        self.view.add_cookie({
            "fake-login-session": {
                "key": "fake-login-session",
                "value":  "",
                "path": "/",
                "expires": 0
            }
        })

        return True


# Login
class DispatcherFormExampleSignIn(DispatcherFormExampleSign):
    """Handles sign-in form processing and user authentication."""

    def get(self) -> bool:
        """Process sign-in form submission and authenticate user."""

        if not self.validate_get():
            return False

        return True

    def post(self) -> bool:
        """Process sign-in form submission and authenticate user."""

        # ref:fake_login_form_error is the prefix for error types
        # e.g. ref:fake_login_form_error_regex for error in regex
        # Add translations for each error type
        if not self.validate_post("ref:fake_login_form_error"):
            return False

        if not self.validate_post_ftoken():
            return False

        email = self.schema_data["CONTEXT"]["POST"].get("email") or None
        password = self.schema_data["CONTEXT"]["POST"].get("password") or None

        # FAKE email validation
        if not email == EMAIL:
            self.error["form"]["email"] = "true"
            self.error["field"]["email"] = "ref:fake_login_form_error_email_not_match"
            return False

        # FAKE password validation
        if not password == PASSWORD:
            self.error["form"]["password"] = "true"
            self.error["field"]["password"] = "ref:fake_login_form_error_password_not_match"
            return False

        if self.create_session():
            self.schema_data["FAKE_SESSION"] = True
            return True

        return False


# Logout
class DispatcherFormExampleSignOut(DispatcherFormExampleSign):
    """Handles user sign-out and session termination."""

    def get(self) -> bool:
        """logout"""

        if not self.validate_get():
            return False

        return True

    def post(self) -> bool:
        """logout"""

        # ref:fake_login_form_error is the prefix for error types
        # e.g. ref:fake_login_form_error_regex for error in regex
        # Add translations for each error type
        if not self.validate_post("ref:fake_login_form_error"):
            return False

        if self.close_session():
            self.schema_data["FAKE_SESSION"] = False
            return True

        return False
