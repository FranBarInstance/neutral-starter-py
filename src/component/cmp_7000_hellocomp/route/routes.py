# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Hello component routes module."""

from flask import Response, request

from core.dispatcher import Dispatcher

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_hellocomp import DispatcherHelloComp


# If business logic is needed, use custom route and dispatcher.
@bp.route("/test1", defaults={"route": "test1"}, methods=["GET"])
def test1(route) -> Response:
    """Handle test1 requests."""
    dispatch = DispatcherHelloComp(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = dispatch.test1()
    return dispatch.view.render()


# If not business logic is needed, use catch-all route and generic dispatcher.
@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def hellocomp_catch_all(route) -> Response:
    """Handle undefined urls."""

    # We use the generic dispatcher
    dispatch = Dispatcher(request, route, bp.neutral_route)

    # # In this case, it can also be done like this
    # dispatch = DispatcherHelloComp(request, route, bp.neutral_route)

    return dispatch.view.render()
