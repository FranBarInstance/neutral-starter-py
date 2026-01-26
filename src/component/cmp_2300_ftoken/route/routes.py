"""Ftoken routes module."""

from flask import Response, request, send_from_directory

from app.config import Config
from app.extensions import require_header_set

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_ftoken import DispatcherFtoken

STATIC = f"{bp.component['path']}/static"


@bp.route("/<key>/<fetch_id>/<form_id>", defaults={"route": ""}, methods=["GET"])
@require_header_set("Requested-With-Ajax", "Require Ajax")
def ftoken(route, key, fetch_id, form_id) -> Response:
    """Create form fields with ftoken"""
    dispatch = DispatcherFtoken(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = dispatch.ftoken(key, fetch_id, form_id)
    return dispatch.view.render()


@bp.route("/ftoken.min.js", methods=["GET"])
def ftoken_js() -> Response:
    """ftoken.min.js"""
    response = send_from_directory(STATIC, "ftoken.min.js")
    response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
    return response
