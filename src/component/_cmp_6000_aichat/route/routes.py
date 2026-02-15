"""AI Chat routes module."""

from flask import Response, jsonify, request

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_aichat import DispatcherAichat


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def aichat_catch_all(route) -> Response:
    """Handle AI Chat component page routes."""
    dispatch = DispatcherAichat(request, route, bp.neutral_route)
    return dispatch.view.render()


@bp.route("/api/chat", methods=["POST"])
def chat_api() -> Response:
    """API endpoint for chat messages."""
    dispatch = DispatcherAichat(request, "", bp.neutral_route)

    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        history = data.get("history") or []
        if not isinstance(history, list):
            return jsonify({"error": "History must be a list"}), 400

        profile = data.get("profile") or dispatch.get_default_profile()

        try:
            response = dispatch.prompt_chat(profile, user_message, history)
            return jsonify({
                "success": True,
                "response": response,
                "profile": profile
            })
        except ValueError as exc:
            return jsonify({
                "success": False,
                "error": str(exc)
            }), 400

    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(exc)}"
        }), 500


@bp.route("/api/profiles", methods=["GET"])
def get_profiles() -> Response:
    """API endpoint to get available AI profiles."""
    dispatch = DispatcherAichat(request, "", bp.neutral_route)

    try:
        profiles = dispatch.get_profiles()
        return jsonify({
            "success": True,
            "profiles": profiles
        })
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500
