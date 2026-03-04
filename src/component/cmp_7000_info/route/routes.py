"""Info routes module."""

from flask import Response, g

from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module


@bp.route("/<path:route>", methods=["GET"])
def info_catch_all(route) -> Response:
    """Handle undefined urls."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()
