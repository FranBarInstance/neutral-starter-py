"""Image variant delivery routes."""

from flask import Response

from app.config import Config
from app.extensions import cache, limiter
from core.image import Image
from core.user import User

from . import bp  # pylint: disable=no-name-in-module


NOT_FOUND_IMAGE = f"{bp.component['path']}/static/404.webp"
PROFILE_IMAGE = f"{bp.component['path']}/static/profile.webp"


def _read_image_file(path: str) -> bytes:
    """Read a static image file from disk."""
    with open(path, "rb", encoding=None) as file_obj:
        return file_obj.read()


@bp.route("/p/<username>", methods=["GET"])
@limiter.limit(Config.STATIC_LIMITS)
@cache.cached(timeout=Config.CACHE_IMG)
def get_username_image(username: str) -> Response:
    """Serve a profile image thumb variant or the default profile placeholder."""
    if not username:
        response = Response(_read_image_file(PROFILE_IMAGE), mimetype="image/webp", status=200)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_PROFILE_CONTROL
        return response

    profile = User(Config.DB_PWA, Config.DB_PWA_TYPE).get_public_profile_by_username(username)
    image_id = str(profile.get("imageId") or "").strip()
    if not image_id:
        response = Response(_read_image_file(PROFILE_IMAGE), mimetype="image/webp", status=200)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_PROFILE_CONTROL
        return response

    image_variant = Image().get_variant(image_id, "thumb")
    if image_variant is None:
        response = Response(_read_image_file(PROFILE_IMAGE), mimetype="image/webp", status=200)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_PROFILE_CONTROL
        return response

    response = Response(image_variant.data, mimetype="image/webp", status=200)
    response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_PROFILE_CONTROL
    response.headers["X-Image-Width"] = str(image_variant.width)
    response.headers["X-Image-Height"] = str(image_variant.height)
    return response


@bp.route("/v/<image_id>/<variant>", methods=["GET"])
@limiter.limit(Config.STATIC_LIMITS)
@cache.cached(timeout=Config.CACHE_IMG)
def get_image_variant(image_id: str, variant: str) -> Response:
    """Serve one stored image variant."""
    image_variant = Image().get_public_variant(image_id, variant)
    if image_variant is None:
        response = Response(_read_image_file(NOT_FOUND_IMAGE), mimetype="image/webp", status=404)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_CONTROL
        return response

    response = Response(image_variant.data, mimetype="image/webp", status=200)
    response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_CONTROL
    response.headers["X-Image-Width"] = str(image_variant.width)
    response.headers["X-Image-Height"] = str(image_variant.height)
    return response


@bp.route('/', defaults={'_path_value': ''}, methods=['GET'])
@bp.route('/<path:_path_value>', methods=['GET'])
def serve_dynamic_content(_path_value) -> Response:
    """Serve dynamic content through RequestHandler."""
    response = Response(_read_image_file(NOT_FOUND_IMAGE), mimetype="image/webp", status=404)
    response.headers["Cache-Control"] = Config.STATIC_CACHE_IMG_CONTROL
    return response
