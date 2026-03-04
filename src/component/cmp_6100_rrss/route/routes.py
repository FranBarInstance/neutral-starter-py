"""RRSS routes module."""

from flask import Response, g

from app.extensions import require_header_set
from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module
from .rrss_handler import RrssRequestHandler


@bp.route('/', defaults={'route': ''}, methods=['GET'])
def rrss(route) -> Response:
    """Handle rrss home page requests."""
    handler = RrssRequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_data['dispatch_result'] = handler.set_rss_name(bp.schema)
    return handler.render_route()


@bp.route('/ajax', methods=['GET'])
def rrss_ajax() -> Response:
    """Handle ajax requests."""
    handler = RequestHandler(g.pr, "404")
    return handler.render_error()


@bp.route('/ajax/<rrss_name>', defaults={'route': 'ajax'}, methods=['GET'])
@require_header_set('Requested-With-Ajax', 'Only accessible with Ajax')
def rrss_ajax_name(route, rrss_name) -> Response:
    """Handle ajax with rss name."""
    handler = RrssRequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_data['dispatch_result'] = handler.set_rss_name(bp.schema, rrss_name)

    if not handler.schema_data['dispatch_result']:
        handler = RequestHandler(g.pr, "404")
        return handler.render_error()

    return handler.render_route()


@bp.route('/rss/<rrss_name>', defaults={'route': 'rss'}, methods=['GET'])
def rrss_rss_name(route, rrss_name) -> Response:
    """Serve rss feed by name."""
    handler = RrssRequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_data['dispatch_result'] = handler.set_rss_name(bp.schema, rrss_name)

    if not handler.schema_data['dispatch_result']:
        handler = RequestHandler(g.pr, "404")
        return handler.render_error()

    return handler.render_route()


@bp.route('/<path:route>', methods=['GET'])
def rrss_catch_all(route) -> Response:
    """Handle undefined urls."""
    handler = RrssRequestHandler(g.pr, route, bp.neutral_route)
    handler.schema_data['dispatch_result'] = True
    return handler.render_route()
