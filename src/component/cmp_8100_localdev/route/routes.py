"""Local Admin routes."""

from flask import Response, request

from app.extensions import require_header_set

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_localdev import DispatcherLocalDev


@bp.route("/", defaults={"route": ""}, methods=["GET"])
def index(route) -> Response:
    """Main local admin route."""
    dispatch = DispatcherLocalDev(request, route, bp.neutral_route)
    return dispatch.render_route()


@bp.route("/login", defaults={"route": "login"}, methods=["GET", "POST"])
def login(route) -> Response:
    """Local admin login route."""
    dispatch = DispatcherLocalDev(request, route, bp.neutral_route)
    return dispatch.render_route()


@bp.route("/login/ajax", defaults={"route": "login/ajax"}, methods=["GET", "POST"])
def login_ajax(route) -> Response:
    """Local admin login AJAX route."""
    dispatch = DispatcherLocalDev(request, route, bp.neutral_route)
    return dispatch.render_route()


@bp.route("/logout/ajax", defaults={"route": "logout/ajax"}, methods=["POST"])
@require_header_set("Requested-With-Ajax", "Only accessible with Ajax")
def logout_ajax(route) -> Response:
    """Local admin logout action for AJAX requests."""
    dispatch = DispatcherLocalDev(request, route, bp.neutral_route)
    return dispatch.render_route()


@bp.route("/<path:route>", methods=["GET", "POST"])
def default_handler(route) -> Response:
    """Fallback route handler."""
    dispatch = DispatcherLocalDev(request, route, bp.neutral_route)
    return dispatch.render_route()
