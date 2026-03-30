"""crypto-js routes module."""

from flask import Response, send_from_directory

from app.config import Config

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


@bp.route("/crypto-js.min.js", methods=["GET"])
def crypto_js() -> Response:
    """Serve the vendored crypto-js bundle."""
    response = send_from_directory(STATIC, "crypto-js.min.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
