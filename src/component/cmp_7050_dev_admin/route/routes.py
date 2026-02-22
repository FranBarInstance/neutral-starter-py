"""Dev Admin routes."""

from flask import Response, request

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_dev_admin import DispatcherDevAdmin


@bp.route("/", methods=["GET", "POST"])
def index() -> Response:
    """Dev Admin page for config.db custom overrides."""
    dispatch = DispatcherDevAdmin(request, "", bp.neutral_route)
    return dispatch.render_route()


@bp.route("/<path:route>", methods=["GET", "POST"])
def default_handler(route) -> Response:
    """Default route handler."""
    dispatch = DispatcherDevAdmin(request, route, bp.neutral_route)
    return dispatch.render_route()
