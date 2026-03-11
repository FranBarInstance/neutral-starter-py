"""Request handlers for user profile management."""

from core.request_handler import RequestHandler
from core.request_handler_form import FormRequestHandler


class UserRequestHandler(RequestHandler):
    """Base handler for user profile routes.

    Loads current user data from request context.
    The user ID is always obtained from USER, never from URL parameters.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, prepared_request, comp_route="", neutral_route=None):
        super().__init__(prepared_request, comp_route, neutral_route)
        self.schema_data["dispatch_result"] = True

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _get_current_profile_id(self):
        """Get the current user profile ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("profile", {}).get("id")


class UserProfileFormHandler(FormRequestHandler):
    """Handler for user profile edit form."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_profile",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _get_current_profile_id(self):
        """Get the current user profile ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("profile", {}).get("id")

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_profile(self) -> bool:
        """Validate POST tokens and form fields for profile form."""
        if not self.valid_form_tokens_post():
            return False
        if not self.valid_form_validation():
            return False
        if self.any_error_form_fields("ref:user_profile_form_error"):
            return False
        return True

    def _save_profile(self, profile_id) -> bool:
        """Save profile data using the User core helper."""

        alias = (self.schema_data["CONTEXT"]["POST"].get("alias") or "").strip()
        locale = (self.schema_data["CONTEXT"]["POST"].get("locale") or "").strip()
        region = (self.schema_data["CONTEXT"]["POST"].get("region") or "").strip()

        # Build properties with theme configurations
        properties = {}

        theme = (self.schema_data["CONTEXT"]["POST"].get("theme") or "").strip()
        color = (self.schema_data["CONTEXT"]["POST"].get("color") or "").strip()
        dark_mode = (self.schema_data["CONTEXT"]["POST"].get("dark_mode") or "").strip()

        properties["theme"] = theme
        properties["color"] = color
        properties["dark_mode"] = dark_mode

        data = {
            "alias": alias,
            "region": region,
            "locale": locale,
            "properties": properties
        }

        # Use new core helper avoiding direct DB calls
        if not self.user.update_profile(profile_id, data):
            self.schema_data["form_result"] = {
                "status": "fail",
                "message": "ref:user_profile_form_error_save"
            }
            return False

        if isinstance(self.schema_data.get("USER"), dict) and "profile" in self.schema_data["USER"]:
            self.schema_data["USER"]["profile"]["alias"] = alias
            self.schema_data["USER"]["profile"]["locale"] = locale
            self.schema_data["USER"]["profile"]["region"] = region or ""
            # Load current existing dict then merge our changes so session doesn't wipe previous items
            current_props = self.schema_data["USER"]["profile"].get("properties", {})
            if not isinstance(current_props, dict):
                current_props = {}
            current_props.update(properties)
            self.schema_data["USER"]["profile"]["properties"] = current_props

        self.schema_data["form_result"] = {
            "status": "success",
            "message": "ref:user_profile_form_success"
        }
        return True

    def post(self) -> bool:
        """Handle POST request — validate and update user profile."""
        if not self._validate_post_profile():
            return False

        user_id = self._get_current_user_id()
        profile_id = self._get_current_profile_id()
        if not user_id or not profile_id:
            return False

        return self._save_profile(profile_id)
