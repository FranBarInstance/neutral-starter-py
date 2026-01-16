"""catch_all Blueprint Module."""

import os

from flask import Response, request, send_from_directory

from app.config import Config  # pylint: disable=import-error
from app.extensions import limiter  # pylint: disable=import-error
from core.dispatcher import Dispatcher  # pylint: disable=import-error

from . import bp  # pylint: disable=no-name-in-module


@bp.route('/<anyext:route>', methods=['GET'])
@limiter.limit(Config.STATIC_LIMITS)
def serve_static_file(route) -> Response:
    """static file"""
    file_path = os.path.join(Config.STATIC_FOLDER, route)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        response = send_from_directory(Config.STATIC_FOLDER, route)
        response.headers['Cache-Control'] = Config.STATIC_CACHE_CONTROL
        return response

    dispatch = Dispatcher(request, "404")
    return dispatch.view.render_error()


@bp.route('/', defaults={'route': ''}, methods=['GET'])
@bp.route('/<path:route>', methods=['GET'])
def serve_dynamic_content(route) -> Response:
    """Serve dynamic content through the Dispatcher."""
    dispatch = Dispatcher(request, route)
    dispatch.schema_data['dispatch_result'] = True
    return dispatch.view.render()
