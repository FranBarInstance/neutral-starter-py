"""Back To Top routes module."""

from flask import Response, send_from_directory

from app.config import Config  # pylint: disable=import-error

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


@bp.route("/css/backtotop.min.css", methods=["GET"])
def backtotop_css() -> Response:
    """backtotop.css"""
    response = send_from_directory(STATIC, "backtotop.min.css")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response


@bp.route("/js/backtotop.min.js", methods=["GET"])
def backtotop_js() -> Response:
    """backtotop.js"""
    response = send_from_directory(STATIC, "backtotop.min.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
