"""
Know Thyself AI - Reports & Export Routes
Provides PDF download and CSV export.
"""

from flask import Blueprint, jsonify, request, Response
from backend.services.report_service import report_service

report_bp = Blueprint("reports", __name__)


@report_bp.route("/api/reports/pdf", methods=["GET"])
def download_pdf_report():
    """Generates and serves a downloadable PDF wellness report."""
    days = request.args.get("days", default=7, type=int)
    try:
        pdf_bytes = report_service.generate_pdf_report(days=days)
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=KnowThyselfAI_Wellness_Report_{days}Days.pdf"
            }
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500


@report_bp.route("/api/reports/export", methods=["GET"])
def export_csv_report():
    """Generates and serves full telemetry CSV export."""
    try:
        csv_str = report_service.generate_csv_export()
        return Response(
            csv_str,
            mimetype="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=KnowThyselfAI_Telemetry_Export.csv"
            }
        )
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500
