"""PWA routes module."""

import os

from flask import Response, request, send_from_directory

from app.config import Config
from app.extensions import limiter
from core.dispatcher import Dispatcher

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"
PUBLIC = Config.STATIC_FOLDER
CONFIG = bp.component["manifest"]["config"]
DIR = CONFIG["static-dir"]


@bp.route("/service-worker.js", methods=["GET"])
def service_worker() -> Response:
    """service-worker.js is served from the root directory"""

    if CONFIG["public-has-service-worker"]:
        static = PUBLIC
    else:
        static = STATIC

    response = send_from_directory(static, "service-worker.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response


@bp.route(
    f"/{DIR}/manifest.json", defaults={"route": f"{DIR}/manifest.json"}, methods=["GET"]
)
@limiter.limit(Config.STATIC_LIMITS)
def pwa_manifest_json(route) -> Response:
    """manifest.json requires variable replacement."""

    if CONFIG["public-has-manifest"]:
        response = send_from_directory(PUBLIC, f"{DIR}/manifest.json")
        response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
        return response

    dispatch = Dispatcher(request, route, bp.neutral_route)
    template = f"{bp.neutral_route}/{route}"

    headers = {
        "Cache-Control": Config.STATIC_CACHE_CONTROL,
        "Content-Type": "application/json",
    }

    return dispatch.view.render(template, headers)


@bp.route(
    f"/{DIR}/offline.html", defaults={"route": f"{DIR}/offline.html"}, methods=["GET"]
)
@limiter.limit(Config.STATIC_LIMITS)
def pwa_offline(route) -> Response:
    """offline.html variable replacement."""

    if CONFIG["public-has-offline"]:
        response = send_from_directory(PUBLIC, f"{DIR}/offline.html")
        response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
        return response

    dispatch = Dispatcher(request, route, bp.neutral_route)
    template = f"{bp.neutral_route}/{route}"

    return dispatch.view.render(template)


@bp.route(f"/{DIR}/<relative_route>", methods=["GET"])
@limiter.limit(Config.STATIC_LIMITS)
def pwa_static(relative_route) -> Response:
    """remaining static files in /pwa/* or 404 error"""

    if CONFIG["public-has-service-worker"]:
        static = PUBLIC
    else:
        static = STATIC

    route = f"{DIR}/{relative_route}"
    file_path = os.path.join(static, route)

    if os.path.exists(file_path) and not os.path.isdir(file_path):
        response = send_from_directory(static, route)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
        return response

    dispatch = Dispatcher(request, "404")
    return dispatch.view.render_error()
