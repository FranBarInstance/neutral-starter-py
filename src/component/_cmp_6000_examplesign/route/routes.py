"""
Fake login routes

IMPORTANT: The business logic is for demonstration purposes only.
In real applications, create appropriate logic in custom Dispatcher, eg: DispatcherExampleSign
"""

from flask import request, Response
from .dispatcher_example_sign import (
    DispatcherFormExampleSign,
    DispatcherFormExampleSignIn,
    DispatcherFormExampleSignOut
)
from . import bp  # pylint: disable=no-name-in-module


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def index(route) -> Response:
    """Main index route"""
    dispatch = DispatcherFormExampleSign(
        request,
        route,
        bp.neutral_route
    )
    return dispatch.view.render()


@bp.route("/login", defaults={"route": "login"}, methods=["GET"])
def login_get(route) -> Response:
    """Login container page"""
    dispatch = DispatcherFormExampleSignIn(
        request,
        route,
        bp.neutral_route,
        None,
        "fake_login"
    )
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.view.render()


@bp.route("/login/ajax/<ltoken>", defaults={"route": "login/ajax"}, methods=["GET"])
def login_ajax_get(route, ltoken) -> Response:
    """Login AJAX route"""
    dispatch = DispatcherFormExampleSignIn(
        request,
        route,
        bp.neutral_route,
        ltoken,
        "fake_login",
        "email"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.view.render()


@bp.route("/login/ajax/<ltoken>", defaults={"route": "login/ajax"}, methods=["POST"])
def login_ajax_post(route, ltoken) -> Response:
    """Login AJAX route"""
    dispatch = DispatcherFormExampleSignIn(
        request,
        route,
        bp.neutral_route,
        ltoken,
        "fake_login",
        "email"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.view.render()


@bp.route("/logout", defaults={"route": "logout"}, methods=["GET"])
def logout_get(route) -> Response:
    """Logout page"""
    dispatch = DispatcherFormExampleSignOut(request, route, bp.neutral_route)
    dispatch.schema_data["dispatch_result"] = True
    return dispatch.view.render()


@bp.route("/logout/ajax/<ltoken>", defaults={"route": "logout/ajax"}, methods=["GET"])
def logout_ajax(route, ltoken) -> Response:
    """Logout AJAX route"""
    dispatch = DispatcherFormExampleSignOut(
        request,
        route,
        bp.neutral_route,
        ltoken,
        "fake_logout"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.view.render()


@bp.route("/logout/ajax/<ltoken>", defaults={"route": "logout/ajax"}, methods=["POST"])
def logout_ajax_post(route, ltoken) -> Response:
    """Logout AJAX route"""
    dispatch = DispatcherFormExampleSignOut(
        request,
        route,
        bp.neutral_route,
        ltoken,
        "fake_logout"
    )
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.view.render()
