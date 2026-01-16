"""PWA routes module."""

import os

from flask import Response, request, send_from_directory

from app.config import Config  # pylint: disable=import-error
from app.extensions import limiter  # pylint: disable=import-error
from core.dispatcher import Dispatcher  # pylint: disable=import-error

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


@bp.route("/service-worker.js", methods=["GET"])
def service_worker() -> Response:
    """service-worker.js is served from the root directory"""
    response = send_from_directory(STATIC, "service-worker.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response


@bp.route("/pwa/manifest.json", defaults={"route": "pwa/manifest.json"}, methods=["GET"])
@limiter.limit(Config.STATIC_LIMITS)
def pwa_manifest_json(route) -> Response:
    """manifest.json requires variable replacement."""
    dispatch = Dispatcher(request, route, bp.neutral_route)
    template = f"{bp.neutral_route}/{route}"

    headers = {
        "Cache-Control": Config.STATIC_CACHE_CONTROL,
        "Content-Type": "application/json",
    }

    return dispatch.view.render(template, headers)


@bp.route("/pwa/<relative_route>", methods=["GET"])
@limiter.limit(Config.STATIC_LIMITS)
def pwa_static(relative_route) -> Response:
    """remaining static files in /pwa/* or 404 error"""
    static = os.path.join(STATIC, "pwa")
    file_path = os.path.join(static, relative_route)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        response = send_from_directory(static, relative_route)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
        return response

    dispatch = Dispatcher(request, "404")
    return dispatch.view.render_error()
