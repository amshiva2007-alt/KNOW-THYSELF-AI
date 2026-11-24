"""
Know Thyself AI - User Profile & Onboarding Routes
"""

from flask import Blueprint, jsonify, request
from backend.services.auth_service import auth_service
from backend.routes.auth_routes import get_token_from_header

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/user/profile", methods=["GET", "POST"])
def user_profile():
    """Gets or updates current user profile."""
    token = get_token_from_header()
    user = auth_service.validate_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.get_json() or {}
        updated = auth_service.update_profile(user["id"], data)
        return jsonify({"message": "Profile updated", "user": updated})

    return jsonify({"profile": user.get("profile", {}), "user": user})


@user_bp.route("/api/user/onboarding", methods=["POST"])
def complete_onboarding():
    """Saves multi-step onboarding results."""
    token = get_token_from_header()
    user = auth_service.validate_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    data["onboarding_completed"] = True
    updated = auth_service.update_profile(user["id"], data)
    return jsonify({
        "message": "Onboarding completed successfully",
        "user": updated
    })


@user_bp.route("/api/user/preferences", methods=["GET", "POST"])
def user_preferences():
    """Gets or updates user preferences (notifications, theme, goals)."""
    token = get_token_from_header()
    user = auth_service.validate_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == "POST":
        data = request.get_json() or {}
        updated = auth_service.update_preferences(user["id"], data)
        return jsonify({"message": "Preferences updated", "preferences": updated})

    return jsonify({"preferences": user.get("preferences", {})})
