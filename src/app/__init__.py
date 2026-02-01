"""Initialize Flask application and register blueprints."""

import json
import os
from importlib import import_module

from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.routing import PathConverter

from utils.utils import merge_dict

from .config import Config
from .components import Components
from .extensions import cache, limiter


def add_security_headers(response):
    """Add security headers to the response."""
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    # Content Security Policy
    # We build the policy dynamically based on the configuration whitelist.
    from flask import current_app

    def get_csp_string(key):
        return " ".join(filter(None, current_app.config.get(key, [])))

    scripts = get_csp_string('CSP_ALLOWED_SCRIPT')
    styles = get_csp_string('CSP_ALLOWED_STYLE')
    images = get_csp_string('CSP_ALLOWED_IMG')
    fonts = get_csp_string('CSP_ALLOWED_FONT')
    connects = get_csp_string('CSP_ALLOWED_CONNECT')

    csp = (
        f"default-src 'self'; "
        f"script-src 'self' 'unsafe-inline' {scripts}; "
        f"style-src 'self' 'unsafe-inline' {styles}; "
        f"img-src 'self' data: {images}; "
        f"font-src 'self' {fonts}; "
        f"connect-src 'self' {connects}; "
        f"frame-ancestors 'none'; "
        f"base-uri 'self'; "
        f"form-action 'self';"
    )
    response.headers['Content-Security-Policy'] = csp

    return response

def create_app(config_class=Config, debug=False):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.debug = debug
    app.url_map.strict_slashes = False

    app.handle_errors = False
    cache.init_app(app)
    limiter.init_app(app)

    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

    # Ensure SECRET_KEY is set and abort if not
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY must be set in config/.env file")

    if app.debug:
        @app.after_request
        def log_route_info(response):
            if request.endpoint:
                view_func = app.view_functions.get(request.endpoint)
                if view_func:
                    print(f"{view_func.__name__} - {request.path}")
            return response

    # Register security headers
    app.after_request(add_security_headers)

    class AnyExtensionConverter(PathConverter):
        """Capture any path that contains a dot (like files with extension)."""
        regex = r'^(?:.*/)?[^/]+\.[^/]+$'

    app.url_map.converters['anyext'] = AnyExtensionConverter
    app.components = Components(app)

    return app
