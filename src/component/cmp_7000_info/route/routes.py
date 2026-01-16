"""Info routes module."""

from flask import Response, request

from core.dispatcher import Dispatcher  # pylint: disable=import-error

from . import bp  # pylint: disable=no-name-in-module


@bp.route("/<path:route>", methods=["GET"])
def info_catch_all(route) -> Response:
    """Handle undefined urls."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    return dispatch.view.render()
