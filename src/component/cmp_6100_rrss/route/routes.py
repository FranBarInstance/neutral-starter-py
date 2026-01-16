"""RRSS routes module."""

from flask import Response, request

from app.extensions import require_header_set

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_rrss import Dispatcher, DispatcherRrss


@bp.route('/', defaults={'route': ''}, methods=['GET'])
def rrss(route) -> Response:
    """Handle rrss home page requests."""
    dispatch = DispatcherRrss(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = dispatch.set_rss_name(bp.schema)
    return dispatch.view.render()


@bp.route('/ajax', methods=['GET'])
def rrss_ajax() -> Response:
    """Handle ajax requests."""
    dispatch = Dispatcher(request, "404")
    return dispatch.view.render_error()


@bp.route('/ajax/<rrss_name>', defaults={'route': 'ajax'}, methods=['GET'])
@require_header_set('Requested-With-Ajax', 'Only accessible with Ajax')
def rrss_ajax_name(route, rrss_name) -> Response:
    """Handle ajax with rss name."""
    dispatch = DispatcherRrss(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = dispatch.set_rss_name(bp.schema, rrss_name)

    if not dispatch.schema_data['dispatch_result']:
        dispatch = Dispatcher(request, "404")
        return dispatch.view.render_error()

    return dispatch.view.render()


@bp.route('/rss/<rrss_name>', defaults={'route': 'rss'}, methods=['GET'])
def rrss_rss_name(route, rrss_name) -> Response:
    """Serve rss feed by name."""
    dispatch = DispatcherRrss(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = dispatch.set_rss_name(bp.schema, rrss_name)

    if not dispatch.schema_data['dispatch_result']:
        dispatch = Dispatcher(request, "404")
        return dispatch.view.render_error()

    return dispatch.view.render()


@bp.route('/<path:route>', methods=['GET'])
def rrss_catch_all(route) -> Response:
    """Handle undefined urls."""
    dispatch = DispatcherRrss(request, route, bp.neutral_route)
    dispatch.schema_data['dispatch_result'] = True
    return dispatch.view.render()
