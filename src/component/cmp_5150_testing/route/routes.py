"""Testing routes module."""

from flask import Response, g

from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def index(route) -> Response:
    """Route handler for testing routes."""
    dispatch = RequestHandler(g.pr, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.render_route()
