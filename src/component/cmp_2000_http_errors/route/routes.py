"""HTTP errors routes module."""

from flask import current_app, g
from werkzeug.exceptions import HTTPException

from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module


@bp.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions for this component's routes."""

    if isinstance(e, HTTPException):
        code = e.code
        name = e.name
        description = e.description if current_app.debug else "Internal Server Error"
    else:
        # if current_app.debug:
        #     raise e

        code = 500
        name = "Internal Server Error"
        description = "An internal error occurred in app."

    handler = RequestHandler(g.pr, "HTTP_ERROR", bp.neutral_route)
    return handler.render_error(code, name, description)
