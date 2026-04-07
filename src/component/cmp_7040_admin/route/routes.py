"""Admin component routes."""

from flask import Response, g
from app.extensions import require_header_set

from . import bp  # pylint: disable=no-name-in-module
from .admin_handler import (
    AdminHomeRequestHandler,
    AdminImageRequestHandler,
    AdminPostRequestHandler,
    AdminProfileRequestHandler,
    AdminUserRequestHandler,
)


@bp.route("/", methods=["GET"])
def admin_home() -> Response:
    """Admin home route handler.

    Access control (auth and roles) is handled by PreparedRequest
    in the global before_request. Only users with admin or
    moderator roles can access this route.
    """
    handler = AdminHomeRequestHandler(g.pr, "", bp.neutral_route)
    return handler.render_route()


@bp.route("/help", methods=["GET"])
def admin_help() -> Response:
    """Admin help route handler."""
    handler = AdminHomeRequestHandler(g.pr, "help", bp.neutral_route)
    return handler.render_route()


@bp.route("/user", methods=["GET", "POST"])
def admin_user() -> Response:
    """Admin user management route handler.

    Provides user listing, search, filtering, and actions like
    setting disabled status, closing sessions, and deleting users.
    """
    handler = AdminUserRequestHandler(g.pr, "user", bp.neutral_route)
    return handler.render_route()


@bp.route("/profile", methods=["GET", "POST"])
def admin_profile() -> Response:
    """Admin profile management route handler.

    Provides profile listing, search, filtering, and actions like
    setting profile disabled status (moderated, spam).
    """
    handler = AdminProfileRequestHandler(g.pr, "profile", bp.neutral_route)
    return handler.render_route()


@bp.route("/image", methods=["GET", "POST"])
def admin_image() -> Response:
    """Admin image management route handler."""
    handler = AdminImageRequestHandler(g.pr, "image", bp.neutral_route)
    return handler.render_route()


@bp.route("/image/ajax", methods=["GET"])
@require_header_set("Requested-With-Ajax", "Only accessible with Ajax")
def admin_image_ajax() -> Response:
    """Return paginated image list fragment for AJAX load-more."""
    handler = AdminImageRequestHandler(g.pr, "image/ajax", bp.neutral_route)
    handler.route = "image/ajax"
    return handler.render_route()


@bp.route("/post", methods=["GET"])
def admin_post() -> Response:
    """Admin post management route handler.

    Provides post administration interface.
    """
    handler = AdminPostRequestHandler(g.pr, "post", bp.neutral_route)
    return handler.render_route()
