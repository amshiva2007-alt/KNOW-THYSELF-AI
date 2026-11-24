"""
Know Thyself AI - Habit Tracker & Notification Routes
"""

from flask import Blueprint, jsonify, request
from backend.services.habit_service import habit_service
from backend.services.db_service import db
from backend.services.analytics_engine import WellnessAnalyticsEngine

habit_bp = Blueprint("habits", __name__)


@habit_bp.route("/api/habits", methods=["GET"])
def get_habits():
    """Retrieves habit checklist, completion status, streaks, and heatmap."""
    date_str = request.args.get("date")
    status = habit_service.get_habits_status(date_str)
    return jsonify(status)


@habit_bp.route("/api/habits/toggle", methods=["POST"])
def toggle_habit():
    """Toggles completion state of a specific habit."""
    data = request.get_json() or {}
    habit_id = data.get("habit_id")
    date_str = data.get("date")

    if not habit_id:
        return jsonify({"error": "Missing habit_id"}), 400

    res = habit_service.toggle_habit(habit_id, date_str)
    return jsonify(res)


@habit_bp.route("/api/notifications", methods=["GET"])
def get_notifications():
    """Retrieves in-app contextual notifications and smart wellness nudges."""
    records = db.get_all_records()
    summary = WellnessAnalyticsEngine.get_summary_metrics(records, days=7)
    notifications = habit_service.get_notifications(summary)
    return jsonify({"notifications": notifications, "unread_count": sum(1 for n in notifications if not n["read"])})
