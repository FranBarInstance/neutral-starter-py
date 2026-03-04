"""Initialize Flask application and register blueprints."""

import ipaddress
import json
import os
import fnmatch
from importlib import import_module
from http import HTTPStatus

from flask import Flask, request, abort, g
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.routing import PathConverter

from utils.utils import merge_dict
from utils.network import normalize_host, is_allowed_host


from .config import Config
from .bootstrap_db import bootstrap_databases
from .components import Components
from .debug_guard import is_debug_enabled, is_wsgi_debug_enabled
from .extensions import cache, limiter
from core.prepared_request import PreparedRequest


def _verify_before_request_order(app):
    """Verify mandatory execution order of before_request handlers.

    Security invariant: reject_disallowed_host must run before prepare_request_context.
    If this order is not guaranteed, the app must fail to start (fail closed).

    Raises:
        RuntimeError: If before_request handlers are not in correct order.
    """
    # Get all before_request handlers (None key means app-level handlers)
    handlers = app.before_request_funcs.get(None, [])

    # Find positions of our security handlers
    host_guard_pos = None
    prepared_request_pos = None

    for idx, handler in enumerate(handlers):
        # Check function names (handler could be wrapped by functools.wraps)
        handler_name = getattr(handler, '__name__', str(handler))
        if handler_name == 'reject_disallowed_host':
            host_guard_pos = idx
        elif handler_name == 'prepare_request_context':
            prepared_request_pos = idx

    # Verify both handlers exist
    if host_guard_pos is None:
        raise RuntimeError(
            "SECURITY INVARIANT VIOLATION: reject_disallowed_host before_request handler not found. "
            "Host validation must run before PreparedRequest. App startup aborted."
        )

    if prepared_request_pos is None:
        raise RuntimeError(
            "SECURITY INVARIANT VIOLATION: prepare_request_context before_request handler not found. "
            "PreparedRequest must be registered. App startup aborted."
        )

    # Verify order: host guard must come before prepared request
    if host_guard_pos >= prepared_request_pos:
        raise RuntimeError(
            f"SECURITY INVARIANT VIOLATION: before_request order incorrect. "
            f"reject_disallowed_host (pos {host_guard_pos}) must run before "
            f"prepare_request_context (pos {prepared_request_pos}). "
            f"App startup aborted."
        )


class TrustedProxyHeaderGuard: # pylint: disable=too-few-public-methods
    """Strip forwarded headers when request does not come from a trusted proxy."""

    FORWARDED_HEADER_KEYS = (
        "HTTP_FORWARDED",
        "HTTP_X_FORWARDED_FOR",
        "HTTP_X_FORWARDED_PROTO",
        "HTTP_X_FORWARDED_HOST",
        "HTTP_X_FORWARDED_PREFIX",
        "HTTP_X_FORWARDED_PORT",
    )

    def __init__(self, app, trusted_proxy_cidrs):
        self.app = app
        self._trusted_networks = []

        for value in trusted_proxy_cidrs or []:
            item = (value or "").strip()
            if not item:
                continue
            try:
                self._trusted_networks.append(ipaddress.ip_network(item, strict=False))
            except ValueError:
                try:
                    ip = ipaddress.ip_address(item)
                    self._trusted_networks.append(
                        ipaddress.ip_network(f"{ip}/{ip.max_prefixlen}", strict=False)
                    )
                except ValueError:
                    continue

    def __call__(self, environ, start_response):
        remote_addr = (environ.get("REMOTE_ADDR") or "").strip()
        trusted_remote = False

        try:
            remote_ip = ipaddress.ip_address(remote_addr)
            trusted_remote = any(remote_ip in network for network in self._trusted_networks)
        except ValueError:
            trusted_remote = False

        if not trusted_remote:
            for key in self.FORWARDED_HEADER_KEYS:
                environ.pop(key, None)

        return self.app(environ, start_response)


def add_security_headers(response): # pylint: disable=too-many-locals
    """Add security headers to the response."""
    from flask import g, current_app  # pylint: disable=import-outside-toplevel

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = current_app.config.get(
        "REFERRER_POLICY", "strict-origin-when-cross-origin"
    )
    permissions_policy = current_app.config.get("PERMISSIONS_POLICY", "")
    if permissions_policy:
        response.headers["Permissions-Policy"] = permissions_policy

    # Get nonce from Flask.g
    nonce = getattr(g, "csp_nonce", None)
    nonce_str = f" 'nonce-{nonce}'" if nonce else ""

    # Content Security Policy
    def get_csp_string(key):
        return " ".join(filter(None, current_app.config.get(key, [])))

    scripts = get_csp_string("CSP_ALLOWED_SCRIPT")
    styles = get_csp_string("CSP_ALLOWED_STYLE")
    images = get_csp_string("CSP_ALLOWED_IMG")
    fonts = get_csp_string("CSP_ALLOWED_FONT")
    connects = get_csp_string("CSP_ALLOWED_CONNECT")
    frames = get_csp_string("CSP_ALLOWED_FRAME")

    # CSP Unsafe options
    # Note: When unsafe-inline or unsafe-eval is used, nonce is not compatible
    script_unsafe = []
    if current_app.config.get("CSP_ALLOWED_SCRIPT_UNSAFE_INLINE"):
        script_unsafe.append("'unsafe-inline'")
    if current_app.config.get("CSP_ALLOWED_SCRIPT_UNSAFE_EVAL"):
        script_unsafe.append("'unsafe-eval'")

    style_unsafe = []
    if current_app.config.get("CSP_ALLOWED_STYLE_UNSAFE_INLINE"):
        style_unsafe.append("'unsafe-inline'")

    # Determine if nonce should be used (not compatible with unsafe-inline)
    use_nonce = nonce and not script_unsafe and not style_unsafe
    nonce_str = f" 'nonce-{nonce}'" if use_nonce else ""

    script_unsafe_str = f" {' '.join(script_unsafe)}" if script_unsafe else ""
    style_unsafe_str = f" {' '.join(style_unsafe)}" if style_unsafe else ""

    csp = (
        f"default-src 'self'; "
        f"script-src 'self'{nonce_str}{script_unsafe_str} {scripts}; "
        f"style-src 'self'{nonce_str}{style_unsafe_str} {styles}; "
        f"img-src 'self' data: {images}; "
        f"font-src 'self' {fonts}; "
        f"connect-src 'self' {connects}; "
        f"frame-src 'self' {frames}; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self';"
    )
    response.headers["Content-Security-Policy"] = csp

    return response


def create_app(config_class=Config, debug=None):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    if debug is None:
        running_under_wsgi = os.getenv("RUNNING_UNDER_WSGI", "false").lower() in {"true", "1", "yes"}  # pylint: disable=line-too-long
        debug = is_wsgi_debug_enabled() if running_under_wsgi else is_debug_enabled()  # pylint: disable=line-too-long

    app.debug = bool(debug)
    app.url_map.strict_slashes = False

    app.handle_errors = False
    cache.init_app(app)
    limiter.init_app(app)

    if app.config.get("AUTO_BOOTSTRAP_DB", False):
        bootstrap_databases(
            db_pwa_url=app.config["DB_PWA"],
            db_pwa_type=app.config["DB_PWA_TYPE"],
            db_safe_url=app.config["DB_SAFE"],
            db_safe_type=app.config["DB_SAFE_TYPE"],
            db_files_url=app.config["DB_FILES"],
            db_files_type=app.config["DB_FILES_TYPE"],
        )

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.wsgi_app = TrustedProxyHeaderGuard(app.wsgi_app, app.config.get("TRUSTED_PROXY_CIDRS", []))

    # Ensure SECRET_KEY is set and abort if not
    if not app.config["SECRET_KEY"]:
        raise ValueError("SECRET_KEY must be set in config/.env file")

    if app.debug:

        @app.after_request
        def log_route_info(response):
            if request.endpoint:
                view_func = app.view_functions.get(request.endpoint)
                if view_func:
                    print(f"{view_func.__name__} - {request.path}")
            return response

    @app.before_request
    def reject_disallowed_host():
        """Reject requests with a Host header outside ALLOWED_HOSTS."""
        raw_host = (request.host or request.headers.get("Host") or "").strip().lower()
        normalized_host = normalize_host(raw_host)
        if not normalized_host or not is_allowed_host(normalized_host, app.config.get("ALLOWED_HOSTS", [])):  # pylint: disable=line-too-long
            abort(400)

    @app.before_request
    def prepare_request_context():
        """Build canonical request bootstrap object (`g.pr`) after host validation."""
        component_bp = app.blueprints.get(request.blueprint) if request.blueprint else None
        view_args = request.view_args if isinstance(request.view_args, dict) else {}

        if component_bp is None:
            try:
                adapter = app.url_map.bind_to_environ(request.environ)
                rule, matched_args = adapter.match(return_rule=True)
                endpoint = rule.endpoint
                bp_name = str(endpoint).split(".", 1)[0]
                component_bp = app.blueprints.get(bp_name)
                if isinstance(matched_args, dict):
                    view_args = matched_args
            except Exception:  # pylint: disable=broad-except
                pass

        if component_bp is None and request.endpoint:
            bp_name = str(request.endpoint).split(".", 1)[0]
            component_bp = app.blueprints.get(bp_name)

        # Use request.path for security evaluation (full path)
        full_path = request.path

        g.pr = PreparedRequest(request).build(
            component_bp=component_bp,
            full_path=full_path
        )
        if not g.pr.allowed:
            # Design stage behavior: generic unauthorized response for all deny cases.
            return g.pr.view.render_error(401, HTTPStatus(401).phrase, "Unauthorized")

    # Verify mandatory execution order: reject_disallowed_host must run before prepare_request_context
    # This is a security invariant - if order is wrong, the app must fail to start
    _verify_before_request_order(app)

    # Register security headers
    app.after_request(add_security_headers)

    class AnyExtensionConverter(PathConverter):  # pylint: disable=too-few-public-methods
        """Capture any path that contains a dot (like files with extension)."""

        regex = r"^(?:.*/)?[^/]+\.[^/]+$"

    app.url_map.converters["anyext"] = AnyExtensionConverter
    app.components = Components(app)

    return app
