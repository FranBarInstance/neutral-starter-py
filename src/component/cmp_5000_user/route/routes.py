"""User profile management routes."""

from flask import Response, g

from .user_handler import (
    UserRequestHandler,
    UserProfileFormHandler,
    UserEmailRequestHandler,
    UserEmailPinFormHandler,
    UserEmailAddFormHandler,
    UserEmailDeleteFormHandler,
    UserAccountRequestHandler,
    UserAccountPasswordPinFormHandler,
    UserAccountPasswordChangeFormHandler,
    UserAccountBirthdatePinFormHandler,
    UserAccountBirthdateChangeFormHandler,
    UserAccountLoginChangeFormHandler,
)
from . import bp  # pylint: disable=no-name-in-module


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def index(route) -> Response:
    """Main user profile view (read-only)."""
    handler = UserRequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()


@bp.route("/profile", defaults={"route": "profile"}, methods=["GET"])
def profile_get(route) -> Response:
    """Profile edit page."""
    dispatch = UserProfileFormHandler(g.pr, route, bp.neutral_route, None, "user_profile")
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/profile/ajax/<ltoken>", defaults={"route": "profile/ajax"}, methods=["GET"])
def profile_ajax_get(route, ltoken) -> Response:
    """Profile AJAX GET route — load form."""
    dispatch = UserProfileFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_profile")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/profile/ajax/<ltoken>", defaults={"route": "profile/ajax"}, methods=["POST"])
def profile_ajax_post(route, ltoken) -> Response:
    """Profile AJAX POST route — process form."""
    dispatch = UserProfileFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_profile")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/email", defaults={"route": "email"}, methods=["GET"])
def email_get(route) -> Response:
    """Email management page."""
    handler = UserEmailRequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()


@bp.route("/email/pin/ajax/<ltoken>", defaults={"route": "email/pin/ajax"}, methods=["GET"])
def email_pin_ajax_get(route, ltoken) -> Response:
    """Email PIN AJAX GET route — load form."""
    dispatch = UserEmailPinFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_email_pin")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/email/pin/ajax/<ltoken>", defaults={"route": "email/pin/ajax"}, methods=["POST"])
def email_pin_ajax_post(route, ltoken) -> Response:
    """Email PIN AJAX POST route — send PIN."""
    dispatch = UserEmailPinFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_email_pin")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/email/add/ajax/<ltoken>", defaults={"route": "email/add/ajax"}, methods=["GET"])
def email_add_ajax_get(route, ltoken) -> Response:
    """Email add AJAX GET route — load form."""
    dispatch = UserEmailAddFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_email_add")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/email/add/ajax/<ltoken>", defaults={"route": "email/add/ajax"}, methods=["POST"])
def email_add_ajax_post(route, ltoken) -> Response:
    """Email add AJAX POST route — add email."""
    dispatch = UserEmailAddFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_email_add")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/email/delete/ajax/<ltoken>", defaults={"route": "email/delete/ajax"}, methods=["GET"])
def email_delete_ajax_get(route, ltoken) -> Response:
    """Email delete AJAX GET route — load form."""
    dispatch = UserEmailDeleteFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_email_delete")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/email/delete/ajax/<ltoken>", defaults={"route": "email/delete/ajax"}, methods=["POST"])
def email_delete_ajax_post(route, ltoken) -> Response:
    """Email delete AJAX POST route — delete email."""
    dispatch = UserEmailDeleteFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_email_delete")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/account", defaults={"route": "account"}, methods=["GET"])
def account_get(route) -> Response:
    """Account management page."""
    handler = UserAccountRequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()


@bp.route("/account/password/pin/ajax/<ltoken>", defaults={"route": "account/password/pin/ajax"}, methods=["GET"])
def account_password_pin_ajax_get(route, ltoken) -> Response:
    """Account password PIN AJAX GET route — load form."""
    dispatch = UserAccountPasswordPinFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_password_pin")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/account/password/pin/ajax/<ltoken>", defaults={"route": "account/password/pin/ajax"}, methods=["POST"])
def account_password_pin_ajax_post(route, ltoken) -> Response:
    """Account password PIN AJAX POST route — send PIN."""
    dispatch = UserAccountPasswordPinFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_password_pin")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/account/password/ajax/<ltoken>", defaults={"route": "account/password/ajax"}, methods=["GET"])
def account_password_ajax_get(route, ltoken) -> Response:
    """Account password AJAX GET route — load form."""
    dispatch = UserAccountPasswordChangeFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_password_change")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/account/password/ajax/<ltoken>", defaults={"route": "account/password/ajax"}, methods=["POST"])
def account_password_ajax_post(route, ltoken) -> Response:
    """Account password AJAX POST route — update password."""
    dispatch = UserAccountPasswordChangeFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_password_change")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/account/birthdate/pin/ajax/<ltoken>", defaults={"route": "account/birthdate/pin/ajax"}, methods=["GET"])
def account_birthdate_pin_ajax_get(route, ltoken) -> Response:
    """Account birthdate PIN AJAX GET route — load form."""
    dispatch = UserAccountBirthdatePinFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_birthdate_pin")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/account/birthdate/pin/ajax/<ltoken>", defaults={"route": "account/birthdate/pin/ajax"}, methods=["POST"])
def account_birthdate_pin_ajax_post(route, ltoken) -> Response:
    """Account birthdate PIN AJAX POST route — send PIN."""
    dispatch = UserAccountBirthdatePinFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_birthdate_pin")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/account/birthdate/ajax/<ltoken>", defaults={"route": "account/birthdate/ajax"}, methods=["GET"])
def account_birthdate_ajax_get(route, ltoken) -> Response:
    """Account birthdate AJAX GET route — load form."""
    dispatch = UserAccountBirthdateChangeFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_birthdate_change")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/account/birthdate/ajax/<ltoken>", defaults={"route": "account/birthdate/ajax"}, methods=["POST"])
def account_birthdate_ajax_post(route, ltoken) -> Response:
    """Account birthdate AJAX POST route — update birthdate."""
    dispatch = UserAccountBirthdateChangeFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_birthdate_change")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/account/login/ajax/<ltoken>", defaults={"route": "account/login/ajax"}, methods=["GET"])
def account_login_ajax_get(route, ltoken) -> Response:
    """Account login AJAX GET route — load form."""
    dispatch = UserAccountLoginChangeFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_login_change")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/account/login/ajax/<ltoken>", defaults={"route": "account/login/ajax"}, methods=["POST"])
def account_login_ajax_post(route, ltoken) -> Response:
    """Account login AJAX POST route — update login."""
    dispatch = UserAccountLoginChangeFormHandler(g.pr, route, bp.neutral_route, ltoken, "user_account_login_change")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()
