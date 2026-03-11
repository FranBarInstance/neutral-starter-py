"""User profile management routes."""

from flask import Response, g

from .user_handler import (
    UserRequestHandler,
    UserProfileFormHandler,
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
