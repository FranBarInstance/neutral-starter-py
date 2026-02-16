"""Initialize Flask application and register blueprints."""

import ipaddress
import json
import os
import fnmatch
from importlib import import_module

from flask import Flask, request, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.routing import PathConverter

from utils.utils import merge_dict

from .config import Config
from .components import Components
from .debug_guard import is_debug_enabled, is_wsgi_debug_enabled
from .extensions import cache, limiter


class TrustedProxyHeaderGuard:
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
        running_under_wsgi = os.getenv("RUNNING_UNDER_WSGI", "false").lower() in {"true", "1", "yes"}
        debug = is_wsgi_debug_enabled() if running_under_wsgi else is_debug_enabled()

    app.debug = bool(debug)
    app.url_map.strict_slashes = False

    app.handle_errors = False
    cache.init_app(app)
    limiter.init_app(app)

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

    def normalize_host(host):
        """Normalize host for allow-list checks."""
        if not host:
            return ""

        value = host.strip().lower().rstrip(".")
        if value.startswith("["):
            end = value.find("]")
            if end != -1:
                return value[1:end]

        if ":" in value:
            return value.rsplit(":", 1)[0]

        return value

    def is_allowed_host(host):
        """Check host against configured allow-list with wildcard support."""
        for pattern in app.config.get("ALLOWED_HOSTS", []):
            normalized_pattern = (pattern or "").strip().lower().rstrip(".")
            if not normalized_pattern:
                continue
            if normalized_pattern == "*" or fnmatch.fnmatch(host, normalized_pattern):
                return True
        return False

    @app.before_request
    def reject_disallowed_host():
        """Reject requests with a Host header outside ALLOWED_HOSTS."""
        raw_host = (request.host or request.headers.get("Host") or "").strip().lower()
        normalized_host = normalize_host(raw_host)
        if not normalized_host or not is_allowed_host(normalized_host):
            abort(400)

    # Register security headers
    app.after_request(add_security_headers)

    class AnyExtensionConverter(PathConverter):
        """Capture any path that contains a dot (like files with extension)."""

        regex = r"^(?:.*/)?[^/]+\.[^/]+$"

    app.url_map.converters["anyext"] = AnyExtensionConverter
    app.components = Components(app)

    return app
