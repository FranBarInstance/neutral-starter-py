"""materialicons routes module."""

from flask import Response, send_from_directory

from app.config import Config

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"
FONTS = f"{STATIC}/fonts"


@bp.route("/materialdesignicons.min.css", methods=["GET"])
def materialicons_css() -> Response:
    """Serve the vendored Material Design Icons stylesheet."""
    response = send_from_directory(STATIC, "materialdesignicons.min.css")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response


@bp.route("/fonts/<path:filename>", methods=["GET"])
def materialicons_font(filename: str) -> Response:
    """Serve the vendored Material Design Icons font files."""
    response = send_from_directory(FONTS, filename)
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
