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
