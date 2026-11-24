"""
Know Thyself AI - Authentication Routes
"""

from flask import Blueprint, jsonify, request
from backend.services.auth_service import auth_service

auth_bp = Blueprint("auth", __name__)


def get_token_from_header():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    """Registers a new user account."""
    data = request.get_json() or {}
    email = data.get("email", "")
    password = data.get("password", "")
    name = data.get("name", "")

    try:
        result = auth_service.register_user(email, password, name)
        return jsonify({"message": "Registration successful", **result}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticates user with email and password."""
    data = request.get_json() or {}
    email = data.get("email", "")
    password = data.get("password", "")

    try:
        result = auth_service.login_user(email, password)
        return jsonify({"message": "Login successful", **result})
    except ValueError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/api/auth/demo", methods=["POST", "GET"])
def demo_login():
    """Instant 1-click evaluator login with pre-configured demo account."""
    result = auth_service.get_demo_session()
    return jsonify({
        "message": "Demo mode activated. Loaded pre-populated 30-day biometric data.",
        **result
    })


@auth_bp.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Retrieves current authenticated user profile."""
    token = get_token_from_header()
    user = auth_service.validate_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"user": user})


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    """Logs out user session."""
    return jsonify({"message": "Logged out successfully"})
