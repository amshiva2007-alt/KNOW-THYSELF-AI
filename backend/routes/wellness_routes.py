"""
Know Thyself AI - Wellness Telemetry CRUD & Ingestion Routes
"""

from flask import Blueprint, jsonify, request
from backend.services.db_service import db

wellness_bp = Blueprint("wellness", __name__)


@wellness_bp.route("/api/wellness/records", methods=["GET"])
@wellness_bp.route("/api/wellness/metrics", methods=["GET"])
def list_records():
    """Retrieves all wellness records, optionally sliced by days or limit."""
    days = request.args.get("days", type=int)
    limit = request.args.get("limit", type=int)
    effective_limit = days or limit
    records = db.get_all_records(limit=effective_limit)
    return jsonify({
        "count": len(records),
        "records": records
    })


@wellness_bp.route("/api/wellness/records/<record_id>", methods=["GET"])
def get_record(record_id):
    """Retrieves a single record by ID."""
    record = db.get_record_by_id(record_id)
    if not record:
        return jsonify({"error": f"Record '{record_id}' not found"}), 404
    return jsonify(record)


@wellness_bp.route("/api/wellness/records", methods=["POST"])
@wellness_bp.route("/api/wellness/add", methods=["POST"])
def create_or_update_record():
    """Logs or updates a daily wellness record."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    saved_record = db.save_record(data)
    return jsonify({
        "message": "Wellness record successfully saved",
        "record": saved_record
    }), 201


@wellness_bp.route("/api/wellness/update", methods=["PUT", "POST"])
def update_record():
    """Explicit update endpoint for record modification."""
    data = request.get_json() or {}
    record_id = data.get("id")
    if not record_id:
        return jsonify({"error": "Missing record ID"}), 400

    saved = db.save_record(data)
    return jsonify({"message": "Record updated", "record": saved})


@wellness_bp.route("/api/wellness/delete", methods=["DELETE", "POST"])
def delete_record():
    """Deletes or purges a record."""
    data = request.get_json() or {}
    record_id = data.get("id") or request.args.get("id")
    # Soft removal from local db
    records = db.get_all_records()
    records = [r for r in records if r.get("id") != record_id]
    db._write_local_db(records)
    return jsonify({"message": f"Record {record_id} deleted successfully"})


@wellness_bp.route("/api/wellness/reset", methods=["POST"])
def reset_sample_data():
    """Resets dataset to standard 30-day sample data."""
    records = db.reset_to_sample_data()
    return jsonify({
        "message": "Reset to 30-day realistic sample dataset complete",
        "count": len(records)
    })


@wellness_bp.route("/api/wellness/export", methods=["GET"])
def export_wellness_data():
    """Returns complete raw export of stored telemetry."""
    records = db.get_all_records()
    return jsonify({
        "platform": "Know Thyself AI",
        "exported_at": db.get_database_status().get("latest_record_date"),
        "total_days": len(records),
        "data": records
    })
