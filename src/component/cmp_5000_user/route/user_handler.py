"""Request handlers for user profile management."""

from app.config import Config
from core.image import Image
from core.mail import Mail
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
        self.schema_data["CONTEXT"]["POST"]["username"] = self.user.normalize_username(
            self.schema_data["CONTEXT"]["POST"].get("username")
        )
        if not self.valid_form_tokens_post():
            return False
        if not self.valid_form_validation():
            return False
        if self.any_error_form_fields("ref:user_profile_form_error"):
            return False

        image_id = (self.schema_data["CONTEXT"]["POST"].get("imageid") or "").strip()
        if image_id:
            image_meta = Image().get_meta(image_id)
            if not image_meta or image_meta.get("profileId") != self._get_current_profile_id():
                self.error["field"]["imageid"] = "ref:user_profile_form_error_value"
                return False

        validation = self.user.validate_username_change(
            self._get_current_profile_id(),
            self.schema_data["CONTEXT"]["POST"].get("username"),
        )
        if not validation.get("success"):
            error_map = {
                "COOLDOWN": "ref:user_profile_form_error_username_cooldown",
                "TAKEN": "ref:user_profile_form_error_username_taken",
                "BLACKLISTED": "ref:user_profile_form_error_username_blacklisted",
            }
            self.error["field"]["username"] = error_map.get(
                validation.get("error"),
                "ref:user_profile_form_error_regex",
            )
            return False
        return True

    def _save_profile(self, profile_id) -> bool:
        """Save profile data using the User core helper."""

        current_profile = self.schema_data.get("USER", {}).get("profile", {}) or {}
        previous_username = (current_profile.get("username") or "").strip()
        username = self.user.normalize_username(
            self.schema_data["CONTEXT"]["POST"].get("username")
        )
        alias = (self.schema_data["CONTEXT"]["POST"].get("alias") or "").strip()
        locale = (self.schema_data["CONTEXT"]["POST"].get("locale") or "").strip()
        region = (self.schema_data["CONTEXT"]["POST"].get("region") or "").strip()
        image_id = (self.schema_data["CONTEXT"]["POST"].get("imageid") or "").strip()

        # Build properties with theme configurations
        properties = {}

        theme = (self.schema_data["CONTEXT"]["POST"].get("theme") or "").strip()
        color = (self.schema_data["CONTEXT"]["POST"].get("color") or "").strip()
        dark_mode = (self.schema_data["CONTEXT"]["POST"].get("dark_mode") or "").strip()

        properties["theme"] = theme
        properties["color"] = color
        properties["dark_mode"] = dark_mode

        data = {
            "username": username,
            "imageId": image_id,
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

        self._invalidate_public_profile_username_cache(previous_username, username)

        if isinstance(self.schema_data.get("USER"), dict) and "profile" in self.schema_data["USER"]:
            self.schema_data["USER"]["profile"]["username"] = username
            self.schema_data["USER"]["profile"]["alias"] = alias
            self.schema_data["USER"]["profile"]["locale"] = locale
            self.schema_data["USER"]["profile"]["region"] = region or ""
            self.schema_data["USER"]["profile"]["imageId"] = image_id
            self.schema_data["USER"]["profile"]["username_changed_at"] = int(self.user.now) if username else ""
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

    def _invalidate_public_profile_username_cache(self, *usernames) -> None:
        """Invalidate cached public `/p/<username>` profile image responses."""
        current = self.schema_data.get("current", {}) or {}
        site = current.get("site", {}) if isinstance(current, dict) else {}
        image_link = str(site.get("image_link_profile") or site.get("image_link") or "").strip()
        if not image_link:
            return

        seen = set()
        image_helper = Image()
        for username in usernames:
            normalized = (username or "").strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            image_helper.invalidate_public_username_cache(normalized, image_link)

    def post(self) -> bool:
        """Handle POST request — validate and update user profile."""
        if not self._validate_post_profile():
            return False

        user_id = self._get_current_user_id()
        profile_id = self._get_current_profile_id()
        if not user_id or not profile_id:
            return False

        return self._save_profile(profile_id)


class UserEmailRequestHandler(RequestHandler):
    """Handler for user email management page."""

    # pylint: disable=too-few-public-methods

    def __init__(self, prepared_request, comp_route="", neutral_route=None):
        super().__init__(prepared_request, comp_route, neutral_route)
        self.schema_data["dispatch_result"] = True
        self._load_user_emails()

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _load_user_emails(self):
        """Load user emails for display."""
        user_id = self._get_current_user_id()
        emails = self.user.get_user_emails(user_id) if user_id else []
        self.schema_data["user_emails"] = emails
        self.schema_data["user_email_count"] = len(emails)
        self.schema_data["user_email_requires_one"] = bool(Config.REQUIRES_USER_EMAIL)
        self.schema_data["user_email_delete_disabled"] = bool(
            Config.REQUIRES_USER_EMAIL and len(emails) <= 1
        )


class UserEmailPinFormHandler(FormRequestHandler):
    """Handler for requesting a PIN for a new email."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_email_pin",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)
        self._load_user_emails()

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _load_user_emails(self):
        """Load user emails for display."""
        user_id = self._get_current_user_id()
        emails = self.user.get_user_emails(user_id) if user_id else []
        self.schema_data["user_emails"] = emails
        self.schema_data["user_email_count"] = len(emails)
        self.schema_data["user_email_requires_one"] = bool(Config.REQUIRES_USER_EMAIL)
        self.schema_data["user_email_delete_disabled"] = bool(
            Config.REQUIRES_USER_EMAIL and len(emails) <= 1
        )

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_pin(self) -> bool:
        """Validate POST tokens and form fields for pin request."""
        return self.validate_post("ref:user_email_pin_form_error")

    def post(self) -> bool:
        """Handle POST request — send PIN to email."""
        if not self._validate_post_pin():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        email = (self.schema_data["CONTEXT"]["POST"].get("email") or "").strip().lower()
        owner_id = self.user.get_userid_by_email(email)

        if owner_id and owner_id != user_id:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email is already in use.",
            }
            return True

        if owner_id == user_id:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email already exists.",
            }
            return True

        pin_params = self.user.create_email_pin(email, user_id)
        if not pin_params:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not generate PIN.",
            }
            return True

        profile = self.schema_data.get("USER", {}).get("profile", {}) or {}
        minutes = max(1, (Config.PIN_ACCOUNT_EXPIRES_SECONDS + 59) // 60)
        mail_data = {
            "to": email,
            "subject": "Email verification PIN",
            "alias": profile.get("alias", ""),
            "locale": profile.get("locale", "en"),
            "pin": pin_params.get("pin", ""),
            "token": pin_params.get("token", ""),
            "expires_minutes": minutes,
        }
        mail = Mail(self.schema.properties)
        mail.send("email-pin", mail_data)

        self.form_submit["result"] = {
            "success": "true",
            "message": "PIN sent to the email.",
        }
        return True


class UserEmailAddFormHandler(FormRequestHandler):
    """Handler for adding a new email."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_email_add",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)
        self._load_user_emails()

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _load_user_emails(self):
        """Load user emails for display."""
        user_id = self._get_current_user_id()
        emails = self.user.get_user_emails(user_id) if user_id else []
        self.schema_data["user_emails"] = emails
        self.schema_data["user_email_count"] = len(emails)
        self.schema_data["user_email_requires_one"] = bool(Config.REQUIRES_USER_EMAIL)
        self.schema_data["user_email_delete_disabled"] = bool(
            Config.REQUIRES_USER_EMAIL and len(emails) <= 1
        )

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_add(self) -> bool:
        """Validate POST tokens and form fields for add email."""
        return self.validate_post("ref:user_email_add_form_error")

    def post(self) -> bool:
        """Handle POST request — add email."""
        if not self._validate_post_add():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        email = (self.schema_data["CONTEXT"]["POST"].get("email") or "").strip().lower()
        pin = (self.schema_data["CONTEXT"]["POST"].get("pin") or "").strip()

        owner_id = self.user.get_userid_by_email(email)
        if owner_id and owner_id != user_id:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email is already in use.",
            }
            return True
        if owner_id == user_id:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email already exists.",
            }
            return True

        if not self.user.verify_user_pin(email, user_id, pin):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Invalid PIN.",
            }
            return True

        if not self.user.add_user_email(user_id, email, main=False):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not add email.",
            }
            return True

        self.user.delete_user_pin(email, user_id, pin)
        self._load_user_emails()

        self.form_submit["result"] = {
            "success": "true",
            "message": "Email added successfully.",
        }
        return True


class UserEmailDeleteFormHandler(FormRequestHandler):
    """Handler for deleting an email."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_email_delete",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)
        self._load_user_emails()

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _load_user_emails(self):
        """Load user emails for display."""
        user_id = self._get_current_user_id()
        emails = self.user.get_user_emails(user_id) if user_id else []
        self.schema_data["user_emails"] = emails
        self.schema_data["user_email_count"] = len(emails)
        self.schema_data["user_email_requires_one"] = bool(Config.REQUIRES_USER_EMAIL)
        self.schema_data["user_email_delete_disabled"] = bool(
            Config.REQUIRES_USER_EMAIL and len(emails) <= 1
        )

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_delete(self) -> bool:
        """Validate POST tokens and form fields for delete email."""
        if not self.valid_form_tokens_post():
            return False
        if not self.valid_form_validation():
            return False
        if self.any_error_form_fields("ref:user_email_delete_form_error"):
            return False
        return True

    def post(self) -> bool:
        """Handle POST request — delete email."""
        if not self._validate_post_delete():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        email = (self.schema_data["CONTEXT"]["POST"].get("email") or "").strip()
        emails = self.user.get_user_emails(user_id)

        if Config.REQUIRES_USER_EMAIL and len(emails) <= 1:
            self.form_submit["result"] = {
                "success": "false",
                "message": "At least one email is required.",
            }
            return True

        selected = next(
            (item for item in emails if str(item.get("email") or "").lower() == email.lower()),
            None,
        )
        if not selected:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email not found.",
            }
            return True

        if not self.user.delete_user_email(user_id, selected.get("email", "")):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not delete email.",
            }
            return True

        self._load_user_emails()
        self.form_submit["result"] = {
            "success": "true",
            "message": "Email deleted successfully.",
        }
        return True


class UserAccountRequestHandler(RequestHandler):
    """Handler for account management page."""

    # pylint: disable=too-few-public-methods

    def __init__(self, prepared_request, comp_route="", neutral_route=None):
        super().__init__(prepared_request, comp_route, neutral_route)
        self.schema_data["dispatch_result"] = True
        self._load_user_emails()

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _load_user_emails(self):
        """Load user emails for account forms."""
        user_id = self._get_current_user_id()
        emails = self.user.get_user_emails(user_id) if user_id else []
        self.schema_data["user_emails"] = emails


class UserAccountPasswordPinFormHandler(FormRequestHandler):
    """Handler for sending password change PIN."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_account_password_pin",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_pin(self) -> bool:
        """Validate POST tokens and form fields for pin request."""
        return self.validate_post("ref:user_account_password_pin_form_error")

    def post(self) -> bool:
        """Handle POST request — send PIN for password change."""
        if not self._validate_post_pin():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        email = (self.schema_data["CONTEXT"]["POST"].get("email") or "").strip()
        if not self.user.verify_login_email(user_id, email):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Login email required.",
            }
            return True

        pin_params = self.user.create_account_pin("account_password", user_id)
        if not pin_params:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not send PIN.",
            }
            return True

        profile = self.schema_data.get("USER", {}).get("profile", {}) or {}
        minutes = max(1, (Config.PIN_ACCOUNT_EXPIRES_SECONDS + 59) // 60)
        mail_data = {
            "to": email,
            "subject": "Security PIN",
            "alias": profile.get("alias", ""),
            "locale": profile.get("locale", "en"),
            "pin": pin_params.get("pin", ""),
            "token": pin_params.get("token", ""),
            "expires_minutes": minutes,
        }
        mail = Mail(self.schema.properties)
        mail.send("account-pin", mail_data)

        self.form_submit["result"] = {
            "success": "true",
            "message": "PIN sent to your email.",
        }
        return True


class UserAccountPasswordChangeFormHandler(FormRequestHandler):
    """Handler for changing password."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_account_password_change",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_change(self) -> bool:
        """Validate POST tokens and form fields for password change."""
        return self.validate_post("ref:user_account_password_change_form_error")

    def post(self) -> bool:
        """Handle POST request — update password."""
        if not self._validate_post_change():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        pin = (self.schema_data["CONTEXT"]["POST"].get("pin") or "").strip()
        password = (self.schema_data["CONTEXT"]["POST"].get("password") or "").strip()

        if not self.user.verify_user_pin("account_password", user_id, pin):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Invalid PIN.",
            }
            return True

        if not self.user.set_password(user_id, password):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not update password.",
            }
            return True

        self.user.delete_user_pin("account_password", user_id, pin)
        self.form_submit["result"] = {
            "success": "true",
            "message": "Password updated successfully.",
        }
        return True


class UserAccountBirthdatePinFormHandler(FormRequestHandler):
    """Handler for sending birthdate change PIN."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_account_birthdate_pin",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_pin(self) -> bool:
        """Validate POST tokens and form fields for pin request."""
        return self.validate_post("ref:user_account_birthdate_pin_form_error")

    def post(self) -> bool:
        """Handle POST request — send PIN for birthdate change."""
        if not self._validate_post_pin():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        email = (self.schema_data["CONTEXT"]["POST"].get("email") or "").strip()
        if not self.user.verify_login_email(user_id, email):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Login email required.",
            }
            return True

        pin_params = self.user.create_account_pin("account_birthdate", user_id)
        if not pin_params:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not send PIN.",
            }
            return True

        profile = self.schema_data.get("USER", {}).get("profile", {}) or {}
        minutes = max(1, (Config.PIN_ACCOUNT_EXPIRES_SECONDS + 59) // 60)
        mail_data = {
            "to": email,
            "subject": "Security PIN",
            "alias": profile.get("alias", ""),
            "locale": profile.get("locale", "en"),
            "pin": pin_params.get("pin", ""),
            "token": pin_params.get("token", ""),
            "expires_minutes": minutes,
        }
        mail = Mail(self.schema.properties)
        mail.send("account-pin", mail_data)

        self.form_submit["result"] = {
            "success": "true",
            "message": "PIN sent to your email.",
        }
        return True


class UserAccountBirthdateChangeFormHandler(FormRequestHandler):
    """Handler for changing birthdate."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_account_birthdate_change",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_change(self) -> bool:
        """Validate POST tokens and form fields for birthdate change."""
        return self.validate_post("ref:user_account_birthdate_change_form_error")

    def post(self) -> bool:
        """Handle POST request — update birthdate."""
        if not self._validate_post_change():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        pin = (self.schema_data["CONTEXT"]["POST"].get("pin") or "").strip()
        birthdate = (self.schema_data["CONTEXT"]["POST"].get("birthdate") or "").strip()

        if not self.user.verify_user_pin("account_birthdate", user_id, pin):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Invalid PIN.",
            }
            return True

        if not self.user.set_birthdate(user_id, birthdate):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not update birthdate.",
            }
            return True

        self.user.delete_user_pin("account_birthdate", user_id, pin)
        self.form_submit["result"] = {
            "success": "true",
            "message": "Birthdate updated successfully.",
        }
        return True


class UserAccountLoginChangeFormHandler(FormRequestHandler):
    """Handler for changing login email."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prepared_request,
        comp_route="",
        neutral_route=None,
        ltoken=None,
        form_name="user_account_login_change",
    ):
        super().__init__(prepared_request, comp_route, neutral_route, ltoken, form_name)
        self._load_user_emails()

    def _get_current_user_id(self):
        """Get the current user ID from request context."""
        current_user = self.schema_data.get("USER", {})
        return current_user.get("userId")

    def _load_user_emails(self):
        """Load user emails for login form."""
        user_id = self._get_current_user_id()
        emails = self.user.get_user_emails(user_id) if user_id else []
        self.schema_data["user_emails"] = emails

    def get(self) -> bool:
        """Handle GET request — validate tokens and return form."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def _validate_post_change(self) -> bool:
        """Validate POST tokens and form fields for login change."""
        return self.validate_post("ref:user_account_login_change_form_error")

    def post(self) -> bool:
        """Handle POST request — update login email."""
        if not self._validate_post_change():
            return False

        user_id = self._get_current_user_id()
        if not user_id:
            return False

        email = (self.schema_data["CONTEXT"]["POST"].get("email") or "").strip().lower()
        current_password = (self.schema_data["CONTEXT"]["POST"].get("current_password") or "").strip()
        emails = self.user.get_user_emails(user_id)

        if not any(item.get("email") == email for item in emails):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email not found.",
            }
            return True

        if not self.user.verify_user_password(user_id, current_password):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Incorrect password.",
            }
            return True

        user_result = self.user.get_user(email)
        if user_result.get("success") and user_result.get("user_data", {}).get("userId") != user_id:
            self.form_submit["result"] = {
                "success": "false",
                "message": "Email already in use.",
            }
            return True

        if not self.user.set_login(user_id, email):
            self.form_submit["result"] = {
                "success": "false",
                "message": "Could not update login.",
            }
            return True

        self.form_submit["result"] = {
            "success": "true",
            "message": "Login updated successfully.",
        }
        return True
