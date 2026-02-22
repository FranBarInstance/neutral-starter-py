"""Admin component routes."""

from flask import Response, request

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_admin import DispatcherAdmin


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET", "POST"])
def index(route) -> Response:
    """Admin route handler."""
    dispatch = DispatcherAdmin(request, route, bp.neutral_route)
    return dispatch.render_route()
