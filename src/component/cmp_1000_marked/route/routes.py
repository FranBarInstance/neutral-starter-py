"""marked routes module."""

from flask import Response, send_from_directory

from app.config import Config

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


@bp.route("/marked.esm.js", methods=["GET"])
def marked_esm() -> Response:
    """Serve the vendored marked ESM bundle."""
    response = send_from_directory(STATIC, "marked.esm.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
