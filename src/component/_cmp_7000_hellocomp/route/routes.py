# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Hello component routes module."""

import os

from flask import Response, g, send_from_directory
from hellocomp_0yt2sa import hellocomp

from app.config import Config
from app.extensions import require_header_set
from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module
from .hellocomp_handler import HelloCompRequestHandler

STATIC = f"{bp.component['path']}/static"


@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    """Handle test1 requests."""
    handler = HelloCompRequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_local_data["message"] = hellocomp()
    handler.schema_data["dispatch_result"] = handler.test1()
    return handler.render_route()


@bp.route("/ajax/example", defaults={"route": "ajax/example"}, methods=["GET"])
@require_header_set('Requested-With-Ajax', 'Only accessible with Ajax')
def ajax_example(route) -> Response:
    """Handle generic ajax example requests."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_local_data["message"] = hellocomp()
    return handler.render_route()


@bp.route("/ajax/modal-content", defaults={"route": "ajax/modal-content"}, methods=["GET"])
@require_header_set('Requested-With-Ajax', 'Only accessible with Ajax')
def ajax_modal_content(route) -> Response:
    """Handle ajax modal content requests."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_local_data["message"] = hellocomp()
    return handler.render_route()


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def hellocomp_catch_all(route) -> Response:
    """Handle undefined urls."""

    if route:
        file_path = os.path.join(STATIC, route)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            response = send_from_directory(STATIC, route)
            response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
            return response

    handler = RequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_local_data["message"] = hellocomp()
    return handler.render_route()
