"""HTTP errors routes module."""

from flask import current_app, request
from werkzeug.exceptions import HTTPException

from core.dispatcher import Dispatcher  # pylint: disable=import-error

from . import bp  # pylint: disable=no-name-in-module


@bp.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions globally."""

    if isinstance(e, HTTPException):
        code = e.code
        name = e.name
        description = e.description
    else:
        if current_app.debug:
            raise e

        code = 500
        name = "Internal Server Error"
        description = "An internal error occurred in app."

    dispatch = Dispatcher(request, "HTTP_ERROR", bp.neutral_route)
    return dispatch.view.render_error(code, name, description)
