"""Admin component routes."""

from flask import Response, g

from . import bp  # pylint: disable=no-name-in-module
from .admin_handler import (
    AdminHomeRequestHandler,
    AdminPostRequestHandler,
    AdminProfileRequestHandler,
    AdminUserRequestHandler,
)


@bp.route("/", methods=["GET"])
def admin_home() -> Response:
    """Admin home route handler.

    Access control (auth and roles) is handled by PreparedRequest
    in the global before_request. Only users with admin, dev, or
    moderator roles can access this route.
    """
    handler = AdminHomeRequestHandler(g.pr, "", bp.neutral_route)
    return handler.render_route()


@bp.route("/user", methods=["GET", "POST"])
def admin_user() -> Response:
    """Admin user management route handler.

    Provides user listing, search, filtering, and actions like
    setting disabled status and managing roles.
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


@bp.route("/post", methods=["GET"])
def admin_post() -> Response:
    """Admin post management route handler.

    Provides post administration interface.
    """
    handler = AdminPostRequestHandler(g.pr, "post", bp.neutral_route)
    return handler.render_route()
