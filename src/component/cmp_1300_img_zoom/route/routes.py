"""Image Zoom routes module."""

from flask import Response, send_from_directory
from app.config import Config

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"

@bp.route("/img-zoom.css", methods=["GET"])
def img_zoom_css() -> Response:
    """img-zoom.css"""
    response = send_from_directory(STATIC, "img-zoom.css")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response

@bp.route("/img-zoom.js", methods=["GET"])
def img_zoom_js() -> Response:
    """img-zoom.js"""
    response = send_from_directory(STATIC, "img-zoom.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
