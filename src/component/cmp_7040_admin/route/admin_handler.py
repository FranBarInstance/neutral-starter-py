"""Admin route handlers with role-based action control."""

import re
import time

from flask import request

from app.config import Config
from constants import (
    DELETED,
    MODERATED,
    SPAM,
    UNCONFIRMED,
    UNVALIDATED,
    RBAC_DEFAULT_ROLES,
)
from core.image import Image
from core.request_handler import RequestHandler
from utils.tokens import ltoken_check


class AdminRequestHandler(RequestHandler):
    """Base admin request handler with common role resolution.

    Provides shared functionality for all admin handlers including
    role resolution from PreparedRequest context.
    """

    # pylint: disable=too-few-public-methods
    # Base class designed for inheritance, subclasses add specific behavior

    # Valid ID pattern: alphanumeric, hyphens, and underscores only
    _VALID_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    _MAX_ID_LENGTH = 64

    # pylint: disable=too-few-public-methods
    # Base class designed for inheritance, subclasses add specific behavior

    @classmethod
    def _is_valid_id(cls, value: str) -> bool:
        """Validate that an ID contains only allowed characters and length."""
        if not value or not isinstance(value, str):
            return False
        if len(value) > cls._MAX_ID_LENGTH:
            return False
        return bool(cls._VALID_ID_PATTERN.match(value))

    @staticmethod
    def _is_valid_disabled_reason(reason: int) -> bool:
        """Validate that a disabled reason is one of the allowed values."""
        return reason in Config.DISABLED.values()

    @staticmethod
    def _build_disabled_options() -> list[dict]:
        pairs = sorted(
            ((name, code) for name, code in Config.DISABLED.items()),
            key=lambda item: item[1],
        )
        return [{"name": name, "code": code} for name, code in pairs]

    @staticmethod
    def _build_profile_disabled_options() -> list[dict]:
        allowed_codes = {
            Config.DISABLED[MODERATED],
            Config.DISABLED[SPAM],
        }
        return [
            item
            for item in AdminRequestHandler._build_disabled_options()
            if item["code"] in allowed_codes
        ]

    def _resolve_current_roles(self) -> tuple[str | None, set[str]]:
        """Resolve current user roles from PreparedRequest context.

        Roles are resolved by PreparedRequest and stored in USER.
        This method extracts them from the prepared context without DB queries.

        Returns:
            Tuple of (user_id, roles_set)
        """
        user_data = self.schema_data.get("USER", {})
        user_id = user_data.get("id") or user_data.get("userId")
        # Roles come from PreparedRequest's per-request USER context
        role_map = user_data.get("profile_roles", {})
        roles = set(role_map.keys())
        return user_id, roles

    def _get_role_permissions(self) -> tuple[bool, bool]:
        """Get role-based permissions for current user.

        Returns:
            Tuple of (can_full, can_moderate)
            - can_full: True if user has admin role
            - can_moderate: True if user has moderator role
        """
        _, roles = self._resolve_current_roles()
        can_full = "admin" in roles
        can_moderate = "moderator" in roles
        return can_full, can_moderate

    def _image_site_links(self) -> tuple[str, str]:
        """Return public profile and variant image links from current schema data."""
        current = self.schema_data.get("current", {}) or {}
        site = current.get("site", {}) if isinstance(current, dict) else {}
        profile_link = str(site.get("image_link_profile") or site.get("image_link") or "").strip()
        variant_link = str(site.get("image_link_variant") or site.get("image_link") or "").strip()
        return profile_link, variant_link

    def _get_profile_cache_targets(self, profile_id: str) -> list[dict]:
        """Resolve one profile cache target with profile id and username."""
        normalized_profile_id = str(profile_id or "").strip()
        if not normalized_profile_id:
            return []
        result = self.user.model.exec(
            "user",
            "get-profile-by-profileid",
            {"profileId": normalized_profile_id},
        )
        rows = result.get("rows", []) if result else []
        if not rows or not rows[0]:
            return []
        row = rows[0]
        return [{
            "profileId": str(row[0] or "").strip(),
            "username": str(row[2] or "").strip(),
        }]

    def _get_user_profile_cache_targets(self, user_id: str) -> list[dict]:
        """Resolve all profile cache targets for one user."""
        normalized_user_id = str(user_id or "").strip()
        if not normalized_user_id:
            return []
        result = self.user.model.exec(
            "user",
            "admin-get-profiles-by-userid",
            {"userId": normalized_user_id},
        )
        rows = result.get("rows", []) if result else []
        targets = []
        for row in rows:
            targets.append(
                {
                    "profileId": str(row[0] or "").strip(),
                    "username": str(row[2] or "").strip(),
                }
            )
        return targets

    def _invalidate_public_profile_images(self, profile_id: str, username: str = "") -> None:
        """Invalidate all cached public images for one profile."""
        profile_link, variant_link = self._image_site_links()
        Image().invalidate_all_public_profile_images_cache(
            profile_id=profile_id,
            username=username,
            profile_image_link=profile_link,
            variant_image_link=variant_link,
        )

    def _invalidate_public_user_images(self, user_id: str) -> None:
        """Invalidate all cached public images for all profiles owned by one user."""
        for target in self._get_user_profile_cache_targets(user_id):
            self._invalidate_public_profile_images(target["profileId"], target["username"])


class AdminHomeRequestHandler(AdminRequestHandler):
    """Handler for admin home route (/admin/)."""

    # pylint: disable=too-few-public-methods

    def render_route(self):
        """Render admin home page with role information."""
        self.schema_data["dispatch_result"] = True

        can_full, can_moderate = self._get_role_permissions()
        _, roles = self._resolve_current_roles()

        self.schema_data["admin_home"] = {
            "can_full": can_full,
            "can_moderate": can_moderate,
            "roles": sorted(roles),
        }
        return self.view.render()


class AdminPostRequestHandler(AdminRequestHandler):
    """Handler for admin post management route (/admin/post)."""

    # pylint: disable=too-few-public-methods

    def render_route(self):
        """Render admin post management page."""
        self.schema_data["dispatch_result"] = True

        can_full, can_moderate = self._get_role_permissions()

        self.schema_data["admin_post"] = {
            "enabled": "true",
            "can_full": can_full,
            "can_moderate": can_moderate,
        }
        return self.view.render()


class AdminImageRequestHandler(AdminRequestHandler):
    """Handler for admin image management route (/admin/image)."""

    # pylint: disable=too-few-public-methods

    @staticmethod
    def _default_image_state() -> dict:
        return {
            "message": "",
            "error": "",
            "search": "",
            "disabled_filter": "",
            "order": "created",
            "limit": 33,
            "offset": 0,
            "has_more": False,
            "next_offset": 0,
            "images": [],
            "exact_image_search": False,
            "exact_image": {},
            "disabled_options": [
                item
                for item in AdminRequestHandler._build_disabled_options()
                if item["code"] in {
                    Config.DISABLED[MODERATED],
                    Config.DISABLED[SPAM],
                }
            ],
            "can_full": False,
            "can_moderate": False,
            "is_dev_or_admin": False,
        }

    def _build_image_state(self, can_full: bool, can_moderate: bool) -> dict:
        state = self._default_image_state()
        state["can_full"] = can_full
        state["can_moderate"] = can_moderate
        state["is_dev_or_admin"] = can_full
        state["search"] = (request.values.get("search") or "").strip()

        requested_disabled_filter = (request.values.get("disabled_filter") or "").strip()
        disabled_codes = {str(item["code"]) for item in state["disabled_options"]}
        state["disabled_filter"] = requested_disabled_filter if requested_disabled_filter in disabled_codes else ""

        requested_order = (request.values.get("order") or "").strip().lower()
        allowed_orders = {
            "created",
            "disabled_created_date",
            "disabled_modified_date",
        }
        state["order"] = requested_order if requested_order in allowed_orders else "created"
        try:
            requested_offset = int(request.values.get("offset", 0))
        except (TypeError, ValueError):
            requested_offset = 0
        state["offset"] = max(0, requested_offset)
        return state

    def _resolve_profile_summaries(self, profile_ids: set[str]) -> dict[str, dict]:
        """Resolve user/profile display data for image rows."""
        summaries = {}
        for profile_id in profile_ids:
            if not profile_id:
                continue
            result = self.user.model.exec("user", "get-profile-by-profileid", {"profileId": profile_id})
            rows = result.get("rows", []) if result else []
            if not rows or not rows[0]:
                summaries[profile_id] = {
                    "profileId": profile_id,
                    "userId": "",
                    "username": "",
                    "alias": "",
                    "locale": "",
                }
                continue
            row = rows[0]
            summaries[profile_id] = {
                "profileId": row[0] or "",
                "userId": row[1] or "",
                "username": row[2] or "",
                "alias": row[5] or "",
                "locale": row[6] or "",
            }
        return summaries

    def _fill_image_list(self, state: dict) -> None:
        image_helper = Image()
        images = image_helper.admin_list_images(
            order_by=state["order"],
            search=state["search"],
            disabled_reason=state["disabled_filter"],
            limit=state["limit"] + 1,
            offset=state["offset"],
        )
        state["has_more"] = len(images) > state["limit"]
        state["images"] = images[: state["limit"]]
        state["next_offset"] = state["offset"] + len(state["images"])

        disabled_labels = {
            int(code): name
            for name, code in Config.DISABLED.items()
        }
        profile_summaries = self._resolve_profile_summaries(
            {str(row.get("profileId") or "").strip() for row in state["images"]}
        )

        for image_row in state["images"]:
            image_row["creator_profile"] = profile_summaries.get(
                str(image_row.get("profileId") or "").strip(),
                {},
            )
            disabled_items = []
            for item in image_row.get("disabled", []):
                try:
                    reason_code = int(item.get("reason"))
                except (TypeError, ValueError):
                    continue
                disabled_items.append(
                    {
                        "reason": reason_code,
                        "name": disabled_labels.get(reason_code, str(reason_code)),
                        "description": item.get("description") or "",
                        "created": item.get("created"),
                        "modified": item.get("modified"),
                    }
                )
            image_row["disabled"] = disabled_items

        search_value = str(state.get("search") or "").strip()
        exact_image = next(
            (
                row for row in state["images"]
                if str(row.get("imageId") or "").strip() == search_value
            ),
            None,
        )
        if exact_image:
            state["exact_image_search"] = True
            state["exact_image"] = exact_image
            state["has_more"] = False

    def _apply_image_action(self, state: dict, can_full: bool, can_moderate: bool) -> None:
        """Apply image status actions with security validation."""
        if request.method != "POST":
            return

        posted_ltoken = (request.form.get("ltoken") or "").strip()
        if not ltoken_check(posted_ltoken, self.schema_data["CONTEXT"].get("UTOKEN")):
            state["error"] = "Invalid form token."
            return

        action = (request.form.get("action") or "").strip()
        image_id = (request.form.get("image_id") or "").strip()
        reason_raw = (request.form.get("reason") or "").strip()
        description = (request.form.get("description") or "").strip()

        if image_id and not self._is_valid_id(image_id):
            state["error"] = "Invalid image_id format."
            return

        if not image_id:
            state["error"] = "image_id is required."
            return

        try:
            reason = int(reason_raw)
        except ValueError:
            state["error"] = "Invalid disabled reason."
            return

        allowed_image_reasons = {
            Config.DISABLED[DELETED],
            Config.DISABLED[MODERATED],
            Config.DISABLED[SPAM],
        }
        if reason not in allowed_image_reasons:
            state["error"] = "Allowed image reasons are deleted, moderated, or spam."
            return

        if can_moderate and not can_full:
            allowed = {Config.DISABLED[MODERATED], Config.DISABLED[SPAM]}
            if reason not in allowed:
                state["error"] = "Moderators can only set or remove moderated or spam."
                return

        if reason == Config.DISABLED[MODERATED] and not description and action == "set-image-disabled":
            state["error"] = "Description is required for moderated."
            return

        image_helper = Image()

        if action == "set-image-disabled":
            if not image_helper.set_image_disabled(image_id, reason, description):
                state["error"] = "Unable to update image disabled status."
                return
            state["message"] = "Image disabled status updated."
            state["search"] = image_id
            return

        if action == "remove-image-disabled":
            if not image_helper.delete_image_disabled(image_id, reason):
                state["error"] = "Unable to remove image disabled status."
                return
            state["message"] = "Image disabled status removed."
            state["search"] = image_id
            return

        state["error"] = "Unknown action."

    def render_route(self):
        """Render admin image management page."""
        self.schema_data["dispatch_result"] = True

        can_full, can_moderate = self._get_role_permissions()

        state = self._build_image_state(can_full=can_full, can_moderate=can_moderate)
        self._apply_image_action(state, can_full=can_full, can_moderate=can_moderate)
        self._fill_image_list(state)

        state["ltoken"] = self.schema_data.get("LTOKEN")
        state["timestamp"] = int(time.time())
        state["reason_deleted"] = Config.DISABLED[DELETED]
        state["reason_moderated"] = Config.DISABLED[MODERATED]
        state["reason_spam"] = Config.DISABLED[SPAM]

        self.schema_data["admin_image"] = state
        return self.view.render()


class AdminUserRequestHandler(AdminRequestHandler):
    """Handler for admin user management route (/admin/user)."""

    # pylint: disable=too-few-public-methods
    # render_route is the main public interface, other methods are internal helpers

    @staticmethod
    def _default_user_state() -> dict:
        return {
            "message": "",
            "error": "",
            "search": "",
            "filter_role": "",
            "disabled_filter": "",
            "order": "created",
            "users": [],
            "disabled_options": AdminRequestHandler._build_disabled_options(),
            "can_full": False,
            "can_moderate": False,
            "is_dev_or_admin": False,
        }

    def _build_user_state(self, can_full: bool, can_moderate: bool) -> dict:
        state = self._default_user_state()
        state["can_full"] = can_full
        state["can_moderate"] = can_moderate
        state["is_dev_or_admin"] = can_full
        state["search"] = (request.values.get("search") or "").strip()
        state["roles_available"] = [role[0] for role in RBAC_DEFAULT_ROLES]

        requested_filter_role = (request.values.get("filter_role") or "").strip().lower()
        state["filter_role"] = requested_filter_role if requested_filter_role in set(state["roles_available"]) else ""

        requested_disabled_filter = (request.values.get("disabled_filter") or "").strip()
        disabled_codes = {str(item["code"]) for item in state["disabled_options"]}
        state["disabled_filter"] = requested_disabled_filter if requested_disabled_filter in disabled_codes else ""

        requested_order = (request.values.get("order") or "").strip().lower()
        allowed_orders = {
            "created",
            "modified",
            "assigned_date",
            "disabled_created_date",
            "disabled_modified_date",
            "disabled_date",
        }
        state["order"] = requested_order if requested_order in allowed_orders else "created"
        return state

    def _fill_user_list(self, state: dict) -> None:
        state["users"] = self.user.admin_list_users(
            order_by=state["order"],
            search=state["search"],
            code=state["filter_role"],
            disabled_reason=state["disabled_filter"],
            limit=100,
            offset=0,
        )

        disabled_labels = {
            int(code): name
            for name, code in Config.DISABLED.items()
        }

        for user_row in state["users"]:
            disabled_items = []
            for item in user_row.get("disabled", []):
                try:
                    reason_code = int(item.get("reason"))
                except (TypeError, ValueError):
                    continue
                disabled_items.append(
                    {
                        "reason": reason_code,
                        "name": disabled_labels.get(reason_code, str(reason_code)),
                        "description": item.get("description") or "",
                        "created": item.get("created"),
                        "modified": item.get("modified"),
                    }
                )
            user_row["disabled"] = disabled_items

            p_disabled_items = []
            for item in user_row.get("profile_disabled", []):
                try:
                    reason_code = int(item.get("reason"))
                except (TypeError, ValueError):
                    continue
                p_disabled_items.append(
                    {
                        "reason": reason_code,
                        "name": disabled_labels.get(reason_code, str(reason_code)),
                        "description": item.get("description") or "",
                        "created": item.get("created"),
                        "modified": item.get("modified"),
                    }
                )
            user_row["profile_disabled"] = p_disabled_items

    def _apply_user_action(
        self,
        state: dict,
        can_full: bool,
        can_moderate: bool,
        current_user_id: str | None,
    ) -> None:
        """Apply user actions with comprehensive security validation."""
        if request.method != "POST":
            return

        posted_ltoken = (request.form.get("ltoken") or "").strip()
        if not ltoken_check(posted_ltoken, self.schema_data["CONTEXT"].get("UTOKEN")):
            state["error"] = "Invalid form token."
            return

        action = (request.form.get("action") or "").strip()
        user_id = (request.form.get("user_id") or "").strip()
        reason_raw = (request.form.get("reason") or "").strip()
        description = (request.form.get("description") or "").strip()
        delete_confirm = (request.form.get("delete_confirm") or "").strip()
        sessions_confirm = (request.form.get("sessions_confirm") or "").strip()

        # Validate ID if provided
        if user_id and not self._is_valid_id(user_id):
            state["error"] = "Invalid user_id format."
            return

        if not user_id:
            state["error"] = "user_id is required."
            return

        if action == "set-disabled":
            try:
                reason = int(reason_raw)
            except ValueError:
                state["error"] = "Invalid disabled reason."
                return

            if not self._is_valid_disabled_reason(reason):
                state["error"] = "Invalid disabled reason value."
                return
            if can_moderate and not can_full:
                allowed = {Config.DISABLED[UNVALIDATED], Config.DISABLED[MODERATED]}
                if reason not in allowed:
                    state["error"] = "Moderators can only set unvalidated or moderated."
                    return

            if reason == Config.DISABLED[MODERATED] and not description:
                state["error"] = "Description is required for moderated."
                return

            if not self.user.set_user_disabled(user_id, reason, description):
                state["error"] = "Unable to update user disabled status."
                return

            self._invalidate_public_user_images(user_id)

            state["message"] = "User disabled status updated."
            state["search"] = user_id
            return

        if action == "remove-disabled":
            try:
                reason = int(reason_raw)
            except ValueError:
                state["error"] = "Invalid disabled reason."
                return

            if not self._is_valid_disabled_reason(reason):
                state["error"] = "Invalid disabled reason value."
                return

            if not can_full:
                if not can_moderate:
                    state["error"] = "Action not allowed for moderator role."
                    return
                allowed = {Config.DISABLED[UNVALIDATED], Config.DISABLED[MODERATED]}
                if reason not in allowed:
                    state["error"] = "Moderators can only remove unvalidated or moderated."
                    return

            if not self.user.delete_user_disabled(user_id, reason):
                state["error"] = "Unable to remove disabled status."
                return

            self._invalidate_public_user_images(user_id)

            state["message"] = "User disabled status removed."
            state["search"] = user_id
            return

        if action == "delete-user":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return
            if current_user_id and user_id == current_user_id:
                state["error"] = "Deleting your own user is not allowed."
                return

            if delete_confirm != "DELETE":
                state["error"] = "Delete confirmation failed. Type DELETE to confirm."
                return

            cache_targets = self._get_user_profile_cache_targets(user_id)
            if not self.user.delete_user(user_id):
                state["error"] = "Unable to delete user."
                return

            for target in cache_targets:
                self._invalidate_public_profile_images(target["profileId"], target["username"])

            state["message"] = "User deleted."
            return

        if action == "close-sessions":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return
            if sessions_confirm != "CLOSE SESSIONS":
                state["error"] = "Session closure confirmation failed. Type CLOSE SESSIONS to confirm."
                return
            if not self.session.close_user_sessions(user_id):
                state["error"] = "Unable to close user sessions."
                return
            state["message"] = "All active sessions for the user were closed. Use only for extreme security cases."
            state["search"] = user_id
            return

        state["error"] = "Unknown action."

    def render_route(self):
        """Render admin user management page."""
        self.schema_data["dispatch_result"] = True

        current_user_id, _ = self._resolve_current_roles()
        can_full, can_moderate = self._get_role_permissions()

        state = self._build_user_state(can_full=can_full, can_moderate=can_moderate)
        self._apply_user_action(
            state,
            can_full=can_full,
            can_moderate=can_moderate,
            current_user_id=current_user_id,
        )
        self._fill_user_list(state)

        state["moderator_reasons"] = [
            Config.DISABLED[UNVALIDATED],
            Config.DISABLED[MODERATED],
        ]
        state["ltoken"] = self.schema_data.get("LTOKEN")
        state["timestamp"] = int(time.time())

        # Convenience markers for templates
        state["reason_deleted"] = Config.DISABLED[DELETED]
        state["reason_unconfirmed"] = Config.DISABLED[UNCONFIRMED]
        state["reason_unvalidated"] = Config.DISABLED[UNVALIDATED]
        state["reason_moderated"] = Config.DISABLED[MODERATED]
        state["reason_spam"] = Config.DISABLED[SPAM]

        self.schema_data["admin_user"] = state
        return self.view.render()


class AdminProfileRequestHandler(AdminRequestHandler):
    """Handler for admin profile management route (/admin/profile)."""

    # pylint: disable=too-few-public-methods
    # render_route is the main public interface, other methods are internal helpers

    @staticmethod
    def _default_profile_state() -> dict:
        return {
            "message": "",
            "error": "",
            "search": "",
            "filter_role": "",
            "disabled_filter": "",
            "order": "created",
            "users": [],
            "disabled_options": AdminRequestHandler._build_profile_disabled_options(),
            "can_full": False,
            "can_moderate": False,
            "is_dev_or_admin": False,
        }

    def _build_profile_state(self, can_full: bool, can_moderate: bool) -> dict:
        state = self._default_profile_state()
        state["can_full"] = can_full
        state["can_moderate"] = can_moderate
        state["is_dev_or_admin"] = can_full
        state["search"] = (request.values.get("search") or "").strip()
        state["roles_available"] = [role[0] for role in RBAC_DEFAULT_ROLES]

        requested_filter_role = (request.values.get("filter_role") or "").strip().lower()
        state["filter_role"] = requested_filter_role if requested_filter_role in set(state["roles_available"]) else ""

        requested_disabled_filter = (request.values.get("disabled_filter") or "").strip()
        disabled_codes = {str(item["code"]) for item in state["disabled_options"]}
        state["disabled_filter"] = requested_disabled_filter if requested_disabled_filter in disabled_codes else ""

        requested_order = (request.values.get("order") or "").strip().lower()
        allowed_orders = {
            "created",
            "modified",
            "role_date",
            "disabled_created_date",
            "disabled_modified_date",
            "disabled_date",
        }
        state["order"] = requested_order if requested_order in allowed_orders else "created"
        return state

    def _fill_profile_list(self, state: dict) -> None:
        state["users"] = self.user.admin_list_profiles(
            order_by=state["order"],
            search=state["search"],
            code=state["filter_role"],
            disabled_reason=state["disabled_filter"],
            limit=100,
            offset=0,
        )

        disabled_labels = {
            int(code): name
            for name, code in Config.DISABLED.items()
        }

        for user_row in state["users"]:
            disabled_items = []
            for item in user_row.get("disabled", []):
                try:
                    reason_code = int(item.get("reason"))
                except (TypeError, ValueError):
                    continue
                disabled_items.append(
                    {
                        "reason": reason_code,
                        "name": disabled_labels.get(reason_code, str(reason_code)),
                        "description": item.get("description") or "",
                        "created": item.get("created"),
                        "modified": item.get("modified"),
                    }
                )
            user_row["disabled"] = disabled_items

            p_disabled_items = []
            for item in user_row.get("profile_disabled", []):
                try:
                    reason_code = int(item.get("reason"))
                except (TypeError, ValueError):
                    continue
                p_disabled_items.append(
                    {
                        "reason": reason_code,
                        "name": disabled_labels.get(reason_code, str(reason_code)),
                        "description": item.get("description") or "",
                        "created": item.get("created"),
                        "modified": item.get("modified"),
                    }
                )
            user_row["profile_disabled"] = p_disabled_items

    def _apply_profile_action(
        self,
        state: dict,
        can_full: bool,
        can_moderate: bool,
    ) -> None:
        """Apply profile actions with security validation."""
        if request.method != "POST":
            return

        posted_ltoken = (request.form.get("ltoken") or "").strip()
        if not ltoken_check(posted_ltoken, self.schema_data["CONTEXT"].get("UTOKEN")):
            state["error"] = "Invalid form token."
            return

        action = (request.form.get("action") or "").strip()
        profile_id = (request.form.get("profile_id") or "").strip()
        reason_raw = (request.form.get("reason") or "").strip()
        description = (request.form.get("description") or "").strip()
        role_code = (request.form.get("role_code") or "").strip().lower()

        # Validate ID if provided
        if profile_id and not self._is_valid_id(profile_id):
            state["error"] = "Invalid profile_id format."
            return

        if not profile_id:
            state["error"] = "profile_id is required."
            return

        if action == "set-profile-disabled":
            try:
                reason = int(reason_raw)
            except ValueError:
                state["error"] = "Invalid disabled reason."
                return

            if not self._is_valid_disabled_reason(reason):
                state["error"] = "Invalid disabled reason value."
                return
            allowed_profile_reasons = {
                Config.DISABLED[MODERATED],
                Config.DISABLED[SPAM],
            }
            if reason not in allowed_profile_reasons:
                state["error"] = "Allowed profile reasons are moderated or spam."
                return

            if can_moderate and not can_full:
                allowed = {Config.DISABLED[MODERATED], Config.DISABLED[SPAM]}
                if reason not in allowed:
                    state["error"] = "Moderators can only set moderated or spam."
                    return

            if reason == Config.DISABLED[MODERATED] and not description:
                state["error"] = "Description is required for moderated."
                return

            if not self.user.set_profile_disabled(profile_id, reason, description):
                state["error"] = "Unable to update profile disabled status."
                return

            cache_targets = self._get_profile_cache_targets(profile_id)
            for target in cache_targets:
                self._invalidate_public_profile_images(target["profileId"], target["username"])

            state["message"] = "Profile disabled status updated."
            state["search"] = profile_id
            return

        if action == "remove-profile-disabled":
            try:
                reason = int(reason_raw)
            except ValueError:
                state["error"] = "Invalid disabled reason."
                return

            if not self._is_valid_disabled_reason(reason):
                state["error"] = "Invalid disabled reason value."
                return
            allowed_profile_reasons = {
                Config.DISABLED[MODERATED],
                Config.DISABLED[SPAM],
            }
            if reason not in allowed_profile_reasons:
                state["error"] = "Allowed profile reasons are moderated or spam."
                return

            if not can_full:
                if not can_moderate:
                    state["error"] = "Action not allowed for current role."
                    return
                allowed = {Config.DISABLED[MODERATED], Config.DISABLED[SPAM]}
                if reason not in allowed:
                    state["error"] = "Moderators can only remove moderated or spam."
                    return

            if not self.user.delete_profile_disabled(profile_id, reason):
                state["error"] = "Unable to remove profile disabled status."
                return

            cache_targets = self._get_profile_cache_targets(profile_id)
            for target in cache_targets:
                self._invalidate_public_profile_images(target["profileId"], target["username"])

            state["message"] = "Profile disabled status removed."
            state["search"] = profile_id
            return

        if action == "assign-role":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return
            if not role_code:
                state["error"] = "Role code is required."
                return
            if role_code not in set(state["roles_available"]):
                state["error"] = "Invalid role code."
                return
            if not self.user.assign_role_to_profile(profile_id, role_code):
                state["error"] = "Unable to assign role."
                return
            state["message"] = "Role assigned."
            state["search"] = profile_id
            return

        if action == "remove-role":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return
            if not role_code:
                state["error"] = "Role code is required."
                return
            if role_code not in set(state["roles_available"]):
                state["error"] = "Invalid role code."
                return
            if not self.user.remove_role_from_profile(profile_id, role_code):
                state["error"] = "Unable to remove role."
                return
            state["message"] = "Role removed."
            state["search"] = profile_id
            return

        state["error"] = "Unknown action."

    def render_route(self):
        """Render admin profile management page."""
        self.schema_data["dispatch_result"] = True

        can_full, can_moderate = self._get_role_permissions()

        state = self._build_profile_state(can_full=can_full, can_moderate=can_moderate)
        self._apply_profile_action(
            state,
            can_full=can_full,
            can_moderate=can_moderate,
        )
        self._fill_profile_list(state)

        state["moderator_reasons"] = [
            Config.DISABLED[UNVALIDATED],
            Config.DISABLED[MODERATED],
        ]
        state["ltoken"] = self.schema_data.get("LTOKEN")
        state["timestamp"] = int(time.time())

        # Convenience markers for templates
        state["reason_deleted"] = Config.DISABLED[DELETED]
        state["reason_unconfirmed"] = Config.DISABLED[UNCONFIRMED]
        state["reason_unvalidated"] = Config.DISABLED[UNVALIDATED]
        state["reason_moderated"] = Config.DISABLED[MODERATED]
        state["reason_spam"] = Config.DISABLED[SPAM]

        self.schema_data["admin_profile"] = state
        return self.view.render()
