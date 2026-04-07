"""Album image routes."""

from __future__ import annotations

import os

from flask import Response, g, jsonify, request, send_from_directory

from app.config import Config
from app.extensions import limiter, require_header_set
from core.image import Image
from core.request_handler import RequestHandler

from . import bp  # pylint: disable=no-name-in-module

STATIC = f"{bp.component['path']}/static"


def _current_profile_id() -> str | None:
    """Return current profile id from request context."""
    current_user = g.pr.schema_data.get("USER", {}) if hasattr(g, "pr") else {}
    profile = current_user.get("profile", {}) if isinstance(current_user, dict) else {}
    return profile.get("id")


def _image_base_url() -> str:
    """Return the configured public base route for image variants."""
    if not hasattr(g, "pr"):
        return ""

    current = g.pr.schema_data.get("current", {}) or {}
    site = current.get("site", {}) if isinstance(current, dict) else {}
    image_link = str(site.get("image_link_variant") or site.get("image_link") or "").strip()
    return image_link.rstrip("/")


def _serialize_image_item(item: dict) -> dict:
    """Normalize one image item with route-aware public URLs."""
    data = dict(item or {})
    image_id = str(data.get("imageId") or "").strip()
    if not image_id:
        return data

    base = _image_base_url()
    if not base:
        return data

    data["thumbUrl"] = f"{base}/{image_id}/thumb"
    data["mediumUrl"] = f"{base}/{image_id}/medium"
    data["fullUrl"] = f"{base}/{image_id}/full"
    return data


@bp.route("/static/<path:asset_path>", methods=["GET"])
@limiter.limit(Config.STATIC_LIMITS)
def serve_static(asset_path) -> Response:
    """Serve component static assets."""
    file_path = os.path.join(STATIC, asset_path)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        response = send_from_directory(STATIC, asset_path)
        response.headers["Cache-Control"] = Config.STATIC_CACHE_CONTROL
        return response
    return Response("404 Not Found", status=404)


@bp.route("/field/list", methods=["GET"])
@require_header_set("Requested-With-Ajax", "Only accessible with Ajax")
def field_list() -> Response:
    """List images for the current profile and one album."""
    profile_id = _current_profile_id()
    if not profile_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    album_code = request.args.get("album_code", "gallery")
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except (ValueError, TypeError):
        limit = 50
        offset = 0

    items = Image().list_by_profile(profile_id, album_code=album_code, limit=limit, offset=offset)
    items = [_serialize_image_item(item) for item in items]
    return jsonify({"success": True, "items": items}), 200


@bp.route("/field/albums", methods=["GET"])
@require_header_set("Requested-With-Ajax", "Only accessible with Ajax")
def field_albums() -> Response:
    """List available album codes for the current profile."""
    profile_id = _current_profile_id()
    if not profile_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    items = Image().list_album_codes(profile_id)
    return jsonify({"success": True, "items": items}), 200


@bp.route("/field/upload", methods=["POST"])
@require_header_set("Requested-With-Ajax", "Only accessible with Ajax")
def field_upload() -> Response:
    """Upload one or many images for the current profile."""
    profile_id = _current_profile_id()
    if not profile_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    files = request.files.getlist("images") or request.files.getlist("image")
    if not files:
        return jsonify({"success": False, "error": "No images received."}), 400

    album_code = request.form.get("album_code", "gallery")
    try:
        items = Image().upload_images(files=files, profile_id=profile_id, album_code=album_code)
        items = [_serialize_image_item(item) for item in items]
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 422
    except RuntimeError as exc:
        return jsonify({"success": False, "error": str(exc)}), 500

    return jsonify({"success": True, "items": items}), 201


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def album_image_pages(route) -> Response:
    """Render album image pages."""
    handler = RequestHandler(g.pr, route, bp.neutral_route)
    return handler.render_route()


@bp.route("/field/delete", methods=["POST"])
@require_header_set("Requested-With-Ajax", "Only accessible with Ajax")
def field_delete() -> Response:
    """Delete an image for the current profile."""
    profile_id = _current_profile_id()
    if not profile_id:
        return jsonify({"success": False, "error": "Authentication required."}), 401

    image_id = request.form.get("image_id")
    if not image_id:
        return jsonify({"success": False, "error": "Image ID required."}), 400

    deleted = Image().delete_image(image_id=image_id, profile_id=profile_id)
    if not deleted:
        return jsonify({"success": False, "error": "Could not delete image or unauthorized."}), 403

    return jsonify({"success": True}), 200


@bp.route("/field/batch-action/ajax/<ltoken>", defaults={"route": "field/batch-action/ajax"}, methods=["GET"])
def field_batch_action_get(route, ltoken) -> Response:
    """Batch action form endpoint GET."""
    from .batch_action_handler import AlbumImageBatchActionFormHandler
    dispatch = AlbumImageBatchActionFormHandler(g.pr, route, bp.neutral_route, ltoken, "album_image_batch_action")
    dispatch.schema_data["dispatch_result"] = dispatch.get()
    return dispatch.render_route()


@bp.route("/field/batch-action/ajax/<ltoken>", defaults={"route": "field/batch-action/ajax"}, methods=["POST"])
def field_batch_action_post(route, ltoken) -> Response:
    """Batch action form endpoint POST."""
    from .batch_action_handler import AlbumImageBatchActionFormHandler
    dispatch = AlbumImageBatchActionFormHandler(g.pr, route, bp.neutral_route, ltoken, "album_image_batch_action")
    dispatch.schema_data["dispatch_result"] = dispatch.post()
    return dispatch.render_route()
