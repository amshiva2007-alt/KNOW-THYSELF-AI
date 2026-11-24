"""
Know Thyself AI - System Health Routes
"""

from datetime import datetime
from flask import Blueprint, jsonify
from backend.config import Config
from backend.services.db_service import db

health_bp = Blueprint("health", __name__)
SERVER_START_TIME = datetime.utcnow()


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Returns application health, database mode, and AI service readiness."""
    db_status = db.get_database_status()
    uptime_seconds = int((datetime.utcnow() - SERVER_START_TIME).total_seconds())

    return jsonify({
        "status": "healthy",
        "app_name": "Know Thyself AI",
        "tagline": "Your Data. Your Intelligence.",
        "uptime_seconds": uptime_seconds,
        "database": db_status,
        "ai": {
            "gemini_configured": Config.has_gemini_key(),
            "model": Config.GEMINI_MODEL
        },
        "server_time": datetime.utcnow().isoformat() + "Z"
    })
