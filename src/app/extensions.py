"""Extensions for flask app"""

from functools import wraps
from flask import request, redirect, url_for
from flask_limiter import Limiter
from flask_caching import Cache
from core.dispatcher import Dispatcher
from utils.utils import get_ip
from .config import Config

# Initialize Flask-Limiter for rate limiting
# _FIXME: In production need storage like Redis or Memcached
# @limiter.limit not working with memory:// storage
# https://flask-limiter.readthedocs.io/en/stable/storage.html#memory-storage
limiter = Limiter(
    key_func=get_ip,
    default_limits=[Config.DEFAULT_LIMITS],
    storage_uri="memory://"
)

# Cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})


def require_header_set(header, msg="Require header"):
    """
    Decorator that enforces the presence of a specific header in HTTP requests.

    Args:
        header (str): The name of the required HTTP header
        msg (str): Custom message to display if header is missing

    Returns:
        function: Decorated function that checks for header presence

    Raises:
        Returns 403 Forbidden response if header is missing
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.headers.get(header):
                dispatch = Dispatcher(request, "HTTP_ERROR")
                return dispatch.view.render_error("403", "Forbidden", msg)
            return f(*args, **kwargs)
        return wrapper
    return decorator

def require_header_set_redirect(header, endpoint="home"):
    """
    Decorator that redirects if a specific header is not present in HTTP requests.

    Args:
        header (str): The name of the required HTTP header
        endpoint (str): The endpoint to redirect to if header is missing

    Returns:
        function: Decorated function that checks for header presence and redirects if missing
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.headers.get(header):
                return redirect(url_for(endpoint))
            return f(*args, **kwargs)
        return wrapper
    return decorator
