"""Home routes module."""

from flask import Response, request

from core.dispatcher import Dispatcher  # pylint: disable=import-error

from . import bp  # pylint: disable=no-name-in-module


@bp.route('/', defaults={'route': ''}, methods=['GET'])
def home(route) -> Response:
    """Route handler for the home page."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = True
    return dispatch.view.render()
