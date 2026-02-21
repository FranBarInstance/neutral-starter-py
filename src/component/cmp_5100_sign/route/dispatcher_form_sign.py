"""Dispatcher for sign-related forms (sign-in, sign-up, sign-out, etc.)."""

import time

from ftoken_0yt2sa import ftoken_check

from app.config import Config
from constants import PIN_TARGET_REMINDER, UNCONFIRMED, UNVALIDATED, USER_EXISTS
from core.dispatcher_form import DispatcherForm
from core.mail import Mail
from utils.utils import format_ua


class DispatcherFormSign(DispatcherForm):
    """Base class for handling authentication form validation logic."""

    def __init__(
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

    def form_get(self) -> bool:
        """Validate GET request for authentication forms."""
        return self.validate_get()

    def validate_get(self) -> bool:
        """Validate GET request parameters and session state."""

        # Do not login while logged in.
        if self.schema_data["CONTEXT"]["SESSION"]:
            self.error["form"]["already_session"] = "true"
            return False

        if not self.valid_form_tokens_get():
            return False

        return True

    def validate_post(self, error_prefix) -> bool:
        """Validate POST request for authentication forms."""

        # Do not reminder while logged in.
        if self.schema_data["CONTEXT"]["SESSION"]:
            self.error["form"]["already_session"] = "true"
            return False

        # ftoken field error
        if not ftoken_check(
            self._ftoken_field_name,
            self.schema_data["CONTEXT"]["POST"],
            self.schema_data["CONTEXT"]["UTOKEN"],
        ):
            self.error["form"]["ftoken"] = "true"
            return False

        if not self.valid_form_tokens_post():
            return False

        if not self.valid_form_validation():
            return False

        if self.any_error_form_fields(error_prefix):
            return False

        return True

    def send_reminder(self, email) -> bool:
        """Send a reminder email to the user."""

        user_result = self.user.get_user(email)

        if (
            not user_result
            or not user_result.get("success")
            or not user_result.get("user_data")
        ):
            return False


        reminder_data = self.user.user_reminder(user_result.get("user_data"))
        if (
            not reminder_data
            or not reminder_data.get("success")
            or not reminder_data.get("reminder_data")
        ):
            return False

        mail = Mail(self.schema.properties)
        mail.send("reminder", reminder_data.get("reminder_data"))

        return True

    def create_session(self, user_data) -> bool:
        """Create a new user session after successful authentication."""
        session_data = {
            "PATH": self.schema_data["CONTEXT"]["PATH"],
            "METHOD": self.schema_data["CONTEXT"]["METHOD"],
            "HEADERS": self.schema_data["CONTEXT"]["HEADERS"],
            "UA": self.schema_data["CONTEXT"]["UA"],
            "user_data": user_data,
        }

        ua = self.schema_data["CONTEXT"].get("UA", "")
        session_ua = format_ua(ua) if ua else "none"

        session_cookie = self.session.create(user_data["userId"], session_ua, session_data)
        self.schema_data["CONTEXT"]["SESSION"] = session_cookie[Config.SESSION_KEY]["value"]
        self.view.add_cookie(session_cookie)

        return True


# In
class DispatcherFormSignIn(DispatcherFormSign):
    """Handles sign-in form processing and user authentication."""

    def form_post(self) -> bool:
        """Process sign-in form submission and authenticate user."""
        if not self.validate_post("ref:sign_in_form_error"):
            return False

        # Get user if exists
        user_data = self.user.check_login(
            self.schema_data["CONTEXT"]["POST"].get("email") or None,
            self.schema_data["CONTEXT"]["POST"].get("password") or None,
            self.schema_data["CONTEXT"]["POST"].get("pin") or None,
        )

        # user_data is set when user exists and password is ok
        if not user_data:
            self.error["login"] = "true"
            return False

        unconfirmed = user_data["user_disabled"].get(UNCONFIRMED, None)
        unvalidated = user_data["user_disabled"].get(UNVALIDATED, None)

        if unconfirmed:
            self.schema_data["user_disabled_unconfirmed"] = Config.DISABLED[UNCONFIRMED]
            return False

        if unvalidated:
            self.schema_data["user_disabled_unvalidated"] = Config.DISABLED[UNVALIDATED]
            return False

        return self.create_session(user_data)

# Up
class DispatcherFormSignUp(DispatcherFormSign):
    """Handles user registration form processing."""

    def form_post(self) -> bool:
        """
        Process sign-up form submission.

        Returns:
            bool: True if registration successful, False otherwise

        Actions:
            - Validates registration form
            - Creates new user account
        """
        if not self.validate_post("ref:sign_up_form_error"):
            return False

        user_result = self.create_user()

        if user_result["success"] != "true":
            # If the user already exists, send reminder.
            # Avoid disclosing whether the user exists or not.
            if user_result["error"] == USER_EXISTS:
                self.send_reminder(user_result["user_data"]["email"])
                return True

            return False

        mail = Mail(self.schema.properties)
        mail.send("register", user_result['user_data'])

        return True

    def create_user(self) -> dict:
        """
        Create a new user account with form data.

        Actions:
            - Collects user data from form fields
            - Creates user record with provided information
            - Sets default locale based on context
        """
        user_data = {
            "alias": self.schema_data["CONTEXT"]["POST"].get("alias"),
            "email": self.schema_data["CONTEXT"]["POST"].get("email"),
            "password": self.schema_data["CONTEXT"]["POST"].get("password"),
            "birthdate": self.schema_data["CONTEXT"]["POST"].get("birthdate"),
            "locale": self.schema_data["CONTEXT"]["LANGUAGE"],
        }

        result = self.user.create(user_data)
        if not result.get("success"):
            self.form_submit["result"] = {
                "success": "false",
                "error": result.get("error", "REGISTRATION_FAILED"),
                "message": result.get("message", "Failed to create user"),
                "user_data": user_data,
            }
            return self.form_submit["result"]

        self.schema_data["new_user"] = {
            "userId": result.get("userId"),
            "profileId": result.get("profileId"),
            "alias": user_data["alias"],
            "email": user_data["email"],
            "locale": user_data["locale"],
            "token": result.get("token"),
            "pin": result.get("pin"),
        }

        self.form_submit["result"] = {
            "success": "true",
            "error": None,
            "message": None,
            "user_data": self.schema_data["new_user"],
        }

        return self.form_submit["result"]


# Out
class DispatcherFormSignOut(DispatcherFormSign):
    """Handles user sign-out and session termination."""

    def logout(self) -> bool:
        """logout"""
        if not self.valid_form_tokens_get():
            return False

        if self.schema_data["CONTEXT"]["SESSION"]:
            session_cookie = self.session.close()
            self.view.add_cookie(session_cookie)
            return True

        return False


# Reminder
class DispatcherFormSignReminder(DispatcherFormSign):
    """Handles password reminder form processing."""

    def form_post(self) -> bool:
        """Send a reminder email to the user."""
        if not self.validate_post("ref:sign_reminder_form_error"):
            return False

        # Always return success to avoid revealing user existence
        self.form_submit["result"] = {
            "success": "true",
            "error": None,
            "message": None,
        }

        self.send_reminder(self.schema_data["CONTEXT"]["POST"].get("email"))

        return True


# PIN
class DispatcherFormSignPin(DispatcherFormSign):
    """Handles PIN-based authentication or verification."""

    def _get_pin_data_by_token(self, pin_token: str) -> dict | None:
        """Resolve pin token to database row."""
        result = self.user.model.exec(
            "user",
            "get-pin-by-token",
            {"token": pin_token, "now": int(time.time())},
        )
        if not result or not result.get("rows") or not result["rows"][0]:
            return None
        row = result["rows"][0]
        return {
            "target": str(row[0]),
            "userId": str(row[1]),
            "pin": str(row[2]),
        }

    def _get_pin_target_kind(self, target: str) -> str | None:
        """Classify supported PIN token targets."""
        if target == str(Config.DISABLED[UNCONFIRMED]):
            return "signup"
        if target == PIN_TARGET_REMINDER:
            return "reminder"
        return None

    def form_get(self, pin_token) -> bool:
        """Validate token and prepare PIN page."""
        if not self.valid_form_tokens_get():
            return False

        self.schema_data["sign_pin_token"] = pin_token
        pin_data = self._get_pin_data_by_token(pin_token)
        target_kind = self._get_pin_target_kind(pin_data["target"]) if pin_data else None
        if not pin_data or not target_kind:
            self.schema_data["sign_pin_token_invalid"] = "true"
            return False

        self.schema_data["sign_pin_token_invalid"] = None
        self.schema_data["sign_pin_token_valid"] = "true"
        self.schema_data["sign_pin_target_kind"] = target_kind
        return True

    def validate_pin_post(self, error_prefix) -> bool:
        """Validate POST request for token-based PIN confirmation."""

        # Do not process while already logged in.
        if self.schema_data["CONTEXT"]["SESSION"]:
            self.error["form"]["already_session"] = "true"
            return False

        if not ftoken_check(
            self._ftoken_field_name,
            self.schema_data["CONTEXT"]["POST"],
            self.schema_data["CONTEXT"]["UTOKEN"],
        ):
            self.error["form"]["ftoken"] = "true"
            return False

        if not self.valid_form_tokens_post():
            return False

        if not self.valid_form_validation():
            return False

        if self.any_error_form_fields(error_prefix):
            return False

        return True

    def form_post(self, pin_token) -> bool:
        """Validate token+PIN, confirm user, and create session."""
        self.schema_data["sign_pin_token"] = pin_token
        if not self.validate_pin_post("ref:sign_pin_form_error"):
            return False

        pin_data = self._get_pin_data_by_token(pin_token)
        target_kind = self._get_pin_target_kind(pin_data["target"]) if pin_data else None
        if not pin_data or not target_kind:
            self.schema_data["sign_pin_token_invalid"] = "true"
            return False

        submitted_pin = str(self.schema_data["CONTEXT"]["POST"].get("pin") or "")
        if submitted_pin != pin_data["pin"]:
            self.error["field"]["pin"] = "Invalid PIN."
            return False

        user_id = pin_data["userId"]

        if target_kind == "signup":
            unconfirmed = Config.DISABLED[UNCONFIRMED]
            self.user.model.exec(
                "user",
                "delete-disabled",
                {"reason": unconfirmed, "userId": user_id},
            )

        self.user.model.exec(
            "user",
            "delete-pin",
            {"target": pin_data["target"], "userId": user_id, "pin": pin_data["pin"]},
        )

        self.form_submit["result"] = {
            "success": "true",
            "error": None,
            "message": None,
        }

        return self.create_session(self.user.build_session_user_data(user_id))
