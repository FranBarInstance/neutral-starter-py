"""
Fake login routes

IMPORTANT: The business logic is for demonstration purposes only.
In real applications, create appropriate logic in custom handler, eg: ExampleSignRequestHandler
"""

from flask import Response, g

from app.extensions import require_header_set
from app.config import Config

from .example_sign_handler import (
    ExampleSignRequestHandler,
    ExampleSignInRequestHandler,
    ExampleSignOutRequestHandler
)
from . import bp  # pylint: disable=no-name-in-module


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def index(route) -> Response:
    """Main index route"""
    dispatch = ExampleSignRequestHandler(g.pr, route, bp.neutral_route)
    return dispatch.render_route()


@bp.route("/login", defaults={"route": "login"}, methods=["GET"])
def login_get(route) -> Response:
    """Login container page"""
    dispatch = ExampleSignInRequestHandler(g.pr, route, bp.neutral_route, None, "fake_login")
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/login/ajax/<ltoken>", defaults={"route": "login/ajax"}, methods=["GET"])
def login_ajax_get(route, ltoken) -> Response:
    """Login AJAX route"""
    dispatch = ExampleSignInRequestHandler(
        g.pr,
        route,
        bp.neutral_route,
        ltoken,
        "fake_login",
        "email"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/login/ajax/<ltoken>", defaults={"route": "login/ajax"}, methods=["POST"])
def login_ajax_post(route, ltoken) -> Response:
    """Login AJAX route"""
    dispatch = ExampleSignInRequestHandler(
        g.pr,
        route,
        bp.neutral_route,
        ltoken,
        "fake_login",
        "email"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/logout", defaults={"route": "logout"}, methods=["GET"])
def logout_get(route) -> Response:
    """Logout page"""
    dispatch = ExampleSignOutRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()


@bp.route("/logout/ajax/<ltoken>", defaults={"route": "logout/ajax"}, methods=["GET"])
def logout_ajax(route, ltoken) -> Response:
    """Logout AJAX route"""
    dispatch = ExampleSignOutRequestHandler(
        g.pr,
        route,
        bp.neutral_route,
        ltoken,
        "fake_logout"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/logout/ajax/<ltoken>", defaults={"route": "logout/ajax"}, methods=["POST"])
def logout_ajax_post(route, ltoken) -> Response:
    """Logout AJAX route"""
    dispatch = ExampleSignOutRequestHandler(
        g.pr,
        route,
        bp.neutral_route,
        ltoken,
        "fake_logout"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()


@bp.route("/help/<item>", defaults={"route": "help"}, methods=["GET"])
@require_header_set("Requested-With-Ajax", "Require Ajax")
def sign_help_item(route, item) -> Response:
    """Serve cached help content for specific items."""
    dispatch = ExampleSignRequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["help_item"] = item
    dispatch.schema_data["dispatch_result"] = True
    dispatch.view.response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return dispatch.render_route()
