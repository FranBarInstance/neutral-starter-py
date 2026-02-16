"""AI Chat routes module."""

from flask import Response, current_app, jsonify, request

from app.extensions import limiter

from . import bp  # pylint: disable=no-name-in-module
from .dispatcher_aichat import DispatcherAichat

CONFIG = bp.component["manifest"].get("config", {})
CHAT_API_LIMITS = CONFIG.get("chat_api_limits", "20 per minute")
PROFILES_API_LIMITS = CONFIG.get("profiles_api_limits", "60 per minute")


def _require_session(dispatch: DispatcherAichat):
    """Return unauthorized response when session is not active."""
    if dispatch.schema_data["HAS_SESSION"] is None:
        return jsonify({
            "success": False,
            "error": "Authentication required"
        }), 401
    return None


@bp.route("/", defaults={"route": ""}, methods=["GET"])
@bp.route("/<path:route>", methods=["GET"])
def aichat_catch_all(route) -> Response:
    """Handle AI Chat component page routes."""
    dispatch = DispatcherAichat(request, route, bp.neutral_route)
    return dispatch.view.render()


@bp.route("/api/chat", methods=["POST"])
@limiter.limit(CHAT_API_LIMITS, error_message="Too many requests. Please try again later.")
def chat_api() -> Response:
    """API endpoint for chat messages."""
    dispatch = DispatcherAichat(request, "", bp.neutral_route)
    unauthorized = _require_session(dispatch)
    if unauthorized:
        return unauthorized

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
        except ValueError:
            current_app.logger.warning(
                "Invalid chat request in /aichat/api/chat",
                exc_info=True,
            )
            return jsonify({
                "success": False,
                "error": "Invalid chat request"
            }), 400

    except Exception:  # pylint: disable=broad-except
        current_app.logger.exception("Unexpected error in /aichat/api/chat")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500


@bp.route("/api/profiles", methods=["GET"])
@limiter.limit(PROFILES_API_LIMITS, error_message="Too many requests. Please try again later.")
def get_profiles() -> Response:
    """API endpoint to get available AI profiles."""
    dispatch = DispatcherAichat(request, "", bp.neutral_route)
    unauthorized = _require_session(dispatch)
    if unauthorized:
        return unauthorized

    try:
        profiles = dispatch.get_profiles()
        return jsonify({
            "success": True,
            "profiles": profiles
        })
    except Exception:  # pylint: disable=broad-except
        current_app.logger.exception("Unexpected error in /aichat/api/profiles")
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500
