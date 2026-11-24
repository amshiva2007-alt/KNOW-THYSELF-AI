"""
Know Thyself AI - CSV Upload & Ingestion Routes
"""

from pathlib import Path
from flask import Blueprint, jsonify, request, send_file, Response
from backend.services.csv_service import csv_service
from backend.config import Config

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/api/upload/preview", methods=["POST"])
def preview_csv():
    """Parses CSV and returns column mapping, validation issues & top 5 rows preview."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded in 'file' field"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "File must be a .csv format"}), 400

    try:
        content = file.read()
        preview = csv_service.preview_csv(content)
        return jsonify(preview)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@upload_bp.route("/api/upload/csv", methods=["POST"])
def import_csv():
    """Imports validated CSV rows into database."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded in 'file' field"}), 400

    file = request.files["file"]
    try:
        content = file.read()
        result = csv_service.import_csv(content)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@upload_bp.route("/api/upload/sample-csv", methods=["GET"])
def download_sample_csv():
    """Provides downloadable sample CSV file for instant evaluator testing."""
    sample_path = Config.BASE_DIR / "sample_data" / "wellness_sample.csv"
    if not sample_path.exists():
        return jsonify({"error": "Sample file not found"}), 404

    return send_file(
        str(sample_path),
        mimetype="text/csv",
        as_attachment=True,
        download_name="wellness_sample.csv"
    )
