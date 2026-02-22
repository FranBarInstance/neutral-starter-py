"""Dispatcher for admin component routes and user administration logic."""

import time

from flask import Response, abort, request

from app.config import Config
from constants import DELETED, MODERATED, SPAM, UNCONFIRMED, UNVALIDATED
from core.dispatcher import Dispatcher
from utils.tokens import ltoken_check


class DispatcherAdmin(Dispatcher):
    """Admin route dispatcher with role-based access control."""

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None):
        self._raw_route = comp_route
        super().__init__(req, comp_route, neutral_route, ltoken)

    @staticmethod
    def _build_disabled_options() -> list[dict]:
        pairs = sorted(
            ((name, code) for name, code in Config.DISABLED.items()),
            key=lambda item: item[1],
        )
        return [{"name": name, "code": code} for name, code in pairs]

    @staticmethod
    def _default_user_state() -> dict:
        return {
            "message": "",
            "error": "",
            "search": "",
            "role_filter": "",
            "disabled_filter": "",
            "order": "created",
            "users": [],
            "disabled_options": DispatcherAdmin._build_disabled_options(),
            "can_full": False,
            "can_moderate": False,
            "is_dev_or_admin": False,
        }

    def _resolve_current_roles(self) -> tuple[str | None, set[str]]:
        props = self.session.get_session_properties()
        user_data = props.get("user_data", {}) if isinstance(props, dict) else {}
        session_roles = user_data.get("roles", []) if isinstance(user_data, dict) else []
        user_id = user_data.get("userId") if isinstance(user_data, dict) else None

        roles = {
            str(role).strip().lower()
            for role in session_roles
            if str(role).strip()
        }

        if user_id:
            # Security-first: for authenticated users, trust current DB roles,
            # not potentially stale roles cached in session.
            roles = set(self.user.get_roles(user_id))

        return user_id, roles

    def _apply_user_action(self, state: dict, can_full: bool, can_moderate: bool) -> None:
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
        role_code = (request.form.get("role_code") or "").strip().lower()
        delete_confirm = (request.form.get("delete_confirm") or "").strip()

        if not user_id:
            state["error"] = "user_id is required."
            return

        if action == "set-disabled":
            try:
                reason = int(reason_raw)
            except ValueError:
                state["error"] = "Invalid disabled reason."
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

            state["message"] = "User disabled status updated."
            state["search"] = user_id
            return

        if action == "remove-disabled":
            try:
                reason = int(reason_raw)
            except ValueError:
                state["error"] = "Invalid disabled reason."
                return

            if not can_full:
                if not can_moderate:
                    state["error"] = "Action not allowed for moderator role."
                    return
                allowed = {Config.DISABLED[UNVALIDATED], Config.DISABLED[MODERATED]}
                if reason not in allowed:
                    state["error"] = "Moderators can only remove unvalidated or moderated."
                    return

            self.user.model.exec("user", "delete-disabled", {"reason": reason, "userId": user_id})
            if self.user.model.has_error:
                state["error"] = "Unable to remove disabled status."
                return

            state["message"] = "User disabled status removed."
            state["search"] = user_id
            return

        if action == "assign-role":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return

            if not role_code:
                state["error"] = "Role code is required."
                return

            if not self.user.assign_role(user_id, role_code):
                state["error"] = "Unable to assign role."
                return

            state["message"] = "Role assigned."
            state["search"] = user_id
            return

        if action == "remove-role":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return

            if not role_code:
                state["error"] = "Role code is required."
                return

            if not self.user.remove_role(user_id, role_code):
                state["error"] = "Unable to remove role."
                return

            state["message"] = "Role removed."
            state["search"] = user_id
            return

        if action == "delete-user":
            if not can_full:
                state["error"] = "Action not allowed for moderator role."
                return

            if delete_confirm != "DELETE":
                state["error"] = "Delete confirmation failed. Type DELETE to confirm."
                return

            if not self.user.delete_user(user_id):
                state["error"] = "Unable to delete user."
                return

            state["message"] = "User deleted."
            return

        state["error"] = "Unknown action."

    def _build_user_state(self, can_full: bool, can_moderate: bool) -> dict:
        state = self._default_user_state()
        state["can_full"] = can_full
        state["can_moderate"] = can_moderate
        state["is_dev_or_admin"] = can_full
        state["search"] = (request.values.get("search") or "").strip()
        state["roles_available"] = ["dev", "admin", "moderator", "editor"]

        requested_role_filter = (request.values.get("role_filter") or "").strip().lower()
        state["role_filter"] = requested_role_filter if requested_role_filter in set(state["roles_available"]) else ""

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

    def _fill_user_list(self, state: dict) -> None:
        state["users"] = self.user.admin_list_users(
            order_by=state["order"],
            search=state["search"],
            role_code=state["role_filter"],
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
                reason_code = int(item.get("reason"))
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

    def render_route(self) -> Response:
        """Execute admin route logic and render."""
        self.schema_data["dispatch_result"] = True

        _user_id, roles = self._resolve_current_roles()
        can_full = bool({"dev", "admin"}.intersection(roles))
        can_moderate = "moderator" in roles

        if not can_full and not can_moderate:
            abort(403)

        current = (self._raw_route or "").strip("/")

        if current == "":
            self.schema_data["admin_home"] = {
                "can_full": can_full,
                "can_moderate": can_moderate,
                "roles": sorted(roles),
            }
            return self.view.render()

        if current == "post":
            self.schema_data["admin_post"] = {
                "enabled": "true",
                "can_full": can_full,
                "can_moderate": can_moderate,
            }
            return self.view.render()

        if current != "user":
            abort(404)

        state = self._build_user_state(can_full=can_full, can_moderate=can_moderate)
        self._apply_user_action(state, can_full=can_full, can_moderate=can_moderate)
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
