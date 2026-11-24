"""
Know Thyself AI - Reports & PDF Generation Service
Creates professional executive wellness summaries in downloadable PDF and CSV formats.
Prominently features non-clinical medical disclaimers as required for wellness awareness platforms.
"""

from datetime import datetime
import io
import csv
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from backend.services.db_service import db
from backend.services.analytics_engine import WellnessAnalyticsEngine


class ReportService:
    """Produces multi-page executive wellness reports in PDF and CSV format."""

    @classmethod
    def generate_pdf_report(cls, days: int = 7) -> bytes:
        """Generates a PDF wellness intelligence report using ReportLab."""
        records = db.get_all_records()
        summary = WellnessAnalyticsEngine.get_summary_metrics(records, days=days)
        correlations = WellnessAnalyticsEngine.calculate_correlations(records)
        clusters = WellnessAnalyticsEngine.cluster_behavioural_patterns(records)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Gen Z Cyberpop Brand Colors
        navy = colors.HexColor("#090714")
        teal = colors.HexColor("#00FF9D")
        violet = colors.HexColor("#A855F7")
        pink = colors.HexColor("#FF2A85")
        dark_surface = colors.HexColor("#120E28")
        soft_white = colors.HexColor("#FFFFFF")
        gray_text = colors.HexColor("#8B7BB5")

        # Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=navy
        )
        tagline_style = ParagraphStyle(
            'ReportTagline',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=teal
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            leading=11,
            textColor=gray_text
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=navy,
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("KNOW THYSELF AI", title_style))
        elements.append(Paragraph("YOUR DATA. YOUR INTELLIGENCE. • Team CORE FOUR — wHACKiest 2026", tagline_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceBefore=4, spaceAfter=12))

        # 2. Executive Metadata & Mandatory Wellness Disclaimer
        meta_text = f"<b>Report Scope:</b> Last {days} Days • <b>Generated At:</b> {datetime.utcnow().strftime('%B %d, %Y %H:%M UTC')} • <b>User:</b> Alex Morgan (Demo Profile)"
        elements.append(Paragraph(meta_text, body_style))
        elements.append(Spacer(1, 6))

        disclaimer_box = (
            "<b>IMPORTANT WELLNESS AWARENESS NOTICE:</b> This report is generated strictly for personal wellness education and lifestyle awareness. "
            "It does NOT provide clinical diagnosis, medical evaluation, or treatment prescriptions. "
            "Always consult a licensed physician or healthcare professional regarding medical questions or significant symptom changes."
        )
        elements.append(Paragraph(disclaimer_box, disclaimer_style))
        elements.append(Spacer(1, 14))

        # 3. Overall Biometric KPI Summary Table
        elements.append(Paragraph("1. Primary Biometric Indicators", section_style))

        score_val = summary.get("overall_score", {}).get("value", 80)
        score_status = summary.get("overall_score", {}).get("status", "Optimal")
        act = summary.get("activity", {})
        slp = summary.get("sleep", {})
        hr = summary.get("heart_rate", {})
        scr = summary.get("screen_time", {})

        table_data = [
            ["Metric Domain", "Current Average", "Baseline Delta", "Status / Benchmark"],
            ["Holistic Wellness Score", f"{score_val} / 100", f"{summary.get('overall_score', {}).get('change', 0):+d} pts", score_status],
            ["Daily Activity", f"{act.get('avg_steps', 0):,} steps", f"{act.get('change', 0):+d} steps", f"{act.get('avg_active_mins', 0)} active mins/day"],
            ["Sleep Architecture", f"{slp.get('avg_hours', 0)} hrs/night", f"{slp.get('change', 0):+.1f} hrs", f"{slp.get('avg_efficiency', 0)}% efficiency"],
            ["Cardiovascular Balance", f"{hr.get('avg_resting_bpm', 0)} BPM resting", f"{hr.get('change', 0):+d} BPM", f"HRV {hr.get('avg_hrv_ms', 0)} ms"],
            ["Digital Exposure", f"{scr.get('avg_hours', 0)} hrs/day", f"{scr.get('change', 0):+.1f} hrs", f"{scr.get('avg_late_screen_mins', 0)} mins pre-bed"]
        ]

        t = Table(table_data, colWidths=[130, 110, 95, 175])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), dark_surface),
            ('TEXTCOLOR', (0, 0), (-1, 0), soft_white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
        ]))
        elements.append(t)
        elements.append(Spacer(1, 14))

        # 4. Discovered Cross-Metric Behavioural Correlations
        elements.append(Paragraph("2. Discovered Cross-Metric Behavioural Correlations", section_style))
        findings = correlations.get("findings", [])
        if findings:
            for f in findings:
                item_text = f"• <b>{f['metric_pair']} (r = {f['coefficient']}):</b> {f['summary']} <i>[Statistical correlation observed; not clinical causation]</i>"
                elements.append(Paragraph(item_text, body_style))
                elements.append(Spacer(1, 4))
        else:
            elements.append(Paragraph("Baseline stabilization in progress. No statistically anomalous correlations detected.", body_style))

        elements.append(Spacer(1, 10))

        # 5. Lifestyle Archetypes & Actionable Recommendations
        elements.append(Paragraph("3. AI Lifestyle Prescriptions & Habit Adherence", section_style))
        recs_text = (
            "• <b>Circadian Window Protocol:</b> Maintain bedtime at 23:15 ± 20 mins to stabilize slow-wave sleep depth.<br/>"
            "• <b>Pre-Sleep Digital Boundary:</b> Institute a 45-minute curfew on smartphone blue light to reduce sleep onset latency.<br/>"
            "• <b>Vagal Tone Stimulation:</b> Integrate 15-minute daylight movement to optimize sympathetic/parasympathetic balance."
        )
        elements.append(Paragraph(recs_text, body_style))

        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E2E8F0"), spaceAfter=8))
        elements.append(Paragraph("Know Thyself AI Platform • Built for wHACKiest 2026 by Team CORE FOUR • Confidential Personal Wellness Telemetry", disclaimer_style))

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    @classmethod
    def generate_csv_export(cls) -> str:
        """Generates CSV string of all stored telemetry."""
        records = db.get_all_records()
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "date", "wellness_score", "steps", "active_minutes", "distance_km", "calories_burned",
            "total_sleep_hours", "deep_sleep_hours", "rem_sleep_hours", "sleep_efficiency",
            "sleep_latency_minutes", "resting_heart_rate", "average_heart_rate", "hrv_ms",
            "total_screen_hours", "late_night_screen_minutes", "workout_type"
        ])

        for r in records:
            act = r.get("activity", {})
            slp = r.get("sleep", {})
            hr = r.get("heart_rate", {})
            scr = r.get("screen_time", {})

            writer.writerow([
                r.get("date"),
                r.get("wellness_score"),
                act.get("steps"),
                act.get("active_minutes"),
                act.get("distance_km"),
                act.get("calories_burned"),
                slp.get("total_sleep_hours"),
                slp.get("deep_sleep_hours"),
                slp.get("rem_sleep_hours"),
                slp.get("efficiency_score"),
                slp.get("sleep_latency_minutes"),
                hr.get("resting_bpm"),
                hr.get("average_bpm"),
                hr.get("hrv_ms"),
                scr.get("total_screen_hours"),
                scr.get("late_night_screen_minutes"),
                act.get("workout_type")
            ])

        return output.getvalue()


report_service = ReportService()
