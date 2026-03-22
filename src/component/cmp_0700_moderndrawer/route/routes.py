"""Modern Drawer routes module."""

from flask import Response, send_from_directory

from app.config import Config

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


@bp.route("/css/moderndrawer.min.css", methods=["GET"])
def moderndrawer_css() -> Response:
    """moderndrawer.css"""
    response = send_from_directory(STATIC, "moderndrawer.min.css")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response


@bp.route("/js/moderndrawer.min.js", methods=["GET"])
def moderndrawer_js() -> Response:
    """moderndrawer.js"""
    response = send_from_directory(STATIC, "moderndrawer.min.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
