"""This module handles the routing for sign-in, sign-up, and related forms."""

import hashlib

from flask import Response, g

from app.config import Config
from app.extensions import cache, limiter, require_header_set

from . import bp  # pylint: disable=no-name-in-module
from .sign_handler import (
    SignRequestHandler,
    SignInRequestHandler,
    SignOutRequestHandler,
    SignPinRequestHandler,
    SignReminderRequestHandler,
    SignUpRequestHandler,
)


def sign_in_email_limit_key() -> str:
    """Rate-limit key based on normalized email for sign-in attempts."""
    email = (g.pr.req.form.get("email") or "").strip().lower()
    if not email:
        return "signin-email:missing"
    return "signin-email:" + hashlib.sha256(email.encode("utf-8")).hexdigest()


@bp.route("/in", defaults={"route": "in"}, methods=["GET"])
def sign_in_get(route) -> Response:
    """Handle GET requests for login form."""
    dispatch = SignInRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/in/form/<ltoken>", defaults={"route": "in/form"}, methods=["GET"])
def sign_in_form_get(route, ltoken) -> Response:
    """Handle GET requests for login form."""
    dispatch = SignInRequestHandler(g.pr, route, bp.neutral_route, ltoken, "sign_in_form", "email")
    dispatch.schema_data["dispatch_result"] = dispatch.form_get()
    return dispatch.render_route()


@bp.route("/in/form/<ltoken>", defaults={"route": "in/form"}, methods=["POST"])
@limiter.limit(Config.SIGNIN_LIMITS, error_message="Please wait and try again later.")
@limiter.limit(
    Config.SIGNIN_EMAIL_LIMITS,
    key_func=sign_in_email_limit_key,
    error_message="Please wait and try again later.",
)
def sign_in_form_post(route, ltoken) -> Response:
    """Handle POST requests for user authentication."""
    dispatch = SignInRequestHandler(g.pr, route, bp.neutral_route, ltoken, "sign_in_form", "email")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()

    return dispatch.render_route()


@bp.route("/up", defaults={"route": "up"}, methods=["GET"])
def sign_up_get(route) -> Response:
    """Handle GET requests for registration form."""
    dispatch = SignUpRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/up/form/<ltoken>", defaults={"route": "up/form"}, methods=["GET"])
def sign_up_form_get(route, ltoken) -> Response:
    """Handle GET requests for registration form."""
    dispatch = SignUpRequestHandler(g.pr, route, bp.neutral_route, ltoken, "sign_up_form", "email")
    dispatch.schema_data["dispatch_result"] = dispatch.form_get()
    return dispatch.render_route()


@bp.route("/up/form/<ltoken>", defaults={"route": "up/form"}, methods=["POST"])
@limiter.limit(Config.SIGNUP_LIMITS, error_message="Please wait and try again later.")
def sign_up_form_post(route, ltoken) -> Response:
    """Handle POST requests for new user registration."""
    dispatch = SignUpRequestHandler(g.pr, route, bp.neutral_route, ltoken, "sign_up_form", "email")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.render_route()


@bp.route("/reminder", defaults={"route": "reminder"}, methods=["GET"])
def sign_reminder_get(route) -> Response:
    """Handle GET requests for password reminder form."""
    dispatch = SignReminderRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/reminder/form/<ltoken>", defaults={"route": "reminder/form"}, methods=["GET"])
def sign_reminder_form_get(route, ltoken) -> Response:
    """Handle GET requests for password reminder form."""
    dispatch = SignReminderRequestHandler(g.pr, route, bp.neutral_route, ltoken, "sign_reminder_form", "email")
    dispatch.schema_data["dispatch_result"] = dispatch.form_get()
    return dispatch.render_route()


@bp.route("/reminder/form/<ltoken>", defaults={"route": "reminder/form"}, methods=["POST"])
@limiter.limit(Config.SIGNREMINDER_LIMITS, error_message="Please wait and try again later.")
@require_header_set("Requested-With-Ajax", "Require Ajax")
def sign_reminder_form_post(route, ltoken) -> Response:
    """Handle POST requests for password reminder form. Send reminder mail if successful."""
    dispatch = SignReminderRequestHandler(g.pr, route, bp.neutral_route, ltoken, "sign_reminder_form", "email")
    dispatch.schema_data["dispatch_result"] = dispatch.form_post()
    return dispatch.render_route()


@bp.route("/out", defaults={"route": "out"}, methods=["GET"])
def sign_out_get(route) -> Response:
    """Handle user logout and session cleanup."""
    dispatch = SignOutRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/out/form/<ltoken>", defaults={"route": "out/form"}, methods=["GET"])
@require_header_set("Requested-With-Ajax", "Require Ajax")
def sign_out_form(route, ltoken) -> Response:
    """Handle user logout and session cleanup."""
    dispatch = SignOutRequestHandler(g.pr, route, bp.neutral_route, ltoken)
    dispatch.schema_data["dispatch_result"] = dispatch.logout()
    return dispatch.render_route()


@bp.route("/pin/<pin_token>", defaults={"route": "pin"}, methods=["GET"])
def sign_pin_get(route, pin_token) -> Response:
    """Handle GET requests for PIN page container."""
    dispatch = SignPinRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["sign_pin_token"] = pin_token
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/pin/form/<pin_token>/<ltoken>", defaults={"route": "pin/form"}, methods=["GET"])
def sign_pin_form_get(route, pin_token, ltoken) -> Response:
    """Handle GET requests for PIN form."""
    dispatch = SignPinRequestHandler(
        g.pr,
        route,
        bp.neutral_route,
        ltoken,
        "sign_pin_form",
        "pin",
    )
    dispatch.schema_data["dispatch_result"] = dispatch.form_get(pin_token)
    return dispatch.render_route()


@bp.route("/pin/form/<pin_token>/<ltoken>", defaults={"route": "pin/form"}, methods=["POST"])
@limiter.limit(Config.SIGNT_LIMITS, error_message="Please wait and try again later.")
@require_header_set("Requested-With-Ajax", "Require Ajax")
def sign_pin_form_post(route, pin_token, ltoken) -> Response:
    """Handle POST requests for token-based PIN confirmation."""
    dispatch = SignPinRequestHandler(
        g.pr,
        route,
        bp.neutral_route,
        ltoken,
        "sign_pin_form",
        "pin",
    )
    dispatch.schema_data["dispatch_result"] = dispatch.form_post(pin_token)
    return dispatch.render_route()


@bp.route("/help/<item>", defaults={"route": "help"}, methods=["GET"])
@require_header_set("Requested-With-Ajax", "Require Ajax")
@cache.cached(timeout=3600)
def sign_help_item(route, item) -> Response:
    """Serve cached help content for specific items."""
    dispatch = SignRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["help_item"] = item
    dispatch.schema_data["dispatch_result"] = True
    dispatch.view.response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return dispatch.render_route()
