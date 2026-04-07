"""catch_all Blueprint Module."""

import os

from flask import Response, g, send_from_directory

from app.config import Config
from app.extensions import limiter
from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module


@bp.route('/<anyext:asset_path>', methods=['GET'])
@limiter.limit(Config.STATIC_LIMITS)
def serve_static_file(asset_path) -> Response:
    """static file"""
    file_path = os.path.join(Config.STATIC_FOLDER, asset_path)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        response = send_from_directory(Config.STATIC_FOLDER, asset_path)
        response.headers['Cache-Control'] = Config.STATIC_CACHE_CONTROL
        return response

    dispatch = RequestHandler(g.pr, "404", bp.neutral_route)
    return dispatch.view.render_error()


@bp.route('/', defaults={'_path_value': ''}, methods=['GET'])
@bp.route('/<path:_path_value>', methods=['GET'])
def serve_dynamic_content(_path_value) -> Response:
    """Serve dynamic content through RequestHandler."""
    dispatch = RequestHandler(g.pr, "404", bp.neutral_route)
    return dispatch.view.render_error()
