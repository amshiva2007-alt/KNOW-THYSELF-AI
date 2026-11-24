"""
Know Thyself AI - Analytics & Machine Learning Routes
Powers timeseries charts, correlation insights, KMeans clustering, and anomalies.
"""

from flask import Blueprint, jsonify, request
from backend.services.db_service import db
from backend.services.analytics_engine import WellnessAnalyticsEngine

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/api/analytics/summary", methods=["GET"])
@analytics_bp.route("/api/analytics/dashboard", methods=["GET"])
def get_summary():
    """Returns period headline cards and comparisons."""
    days = request.args.get("days", default=7, type=int)
    records = db.get_all_records()
    summary = WellnessAnalyticsEngine.get_summary_metrics(records, days=days)
    return jsonify(summary)


@analytics_bp.route("/api/analytics/activity", methods=["GET"])
def get_activity_analytics():
    """Returns activity-specific metrics and trends."""
    records = db.get_all_records(limit=30)
    df = WellnessAnalyticsEngine.records_to_dataframe(records)
    return jsonify({
        "avg_steps": int(df["steps"].mean()) if not df.empty else 0,
        "max_steps": int(df["steps"].max()) if not df.empty else 0,
        "avg_active_mins": int(df["active_minutes"].mean()) if not df.empty else 0,
        "total_calories": int(df["calories_burned"].sum()) if not df.empty else 0,
        "workouts": df["workout_type"].value_counts().to_dict() if "workout_type" in df else {}
    })


@analytics_bp.route("/api/analytics/sleep", methods=["GET"])
def get_sleep_analytics():
    """Returns sleep architecture metrics."""
    records = db.get_all_records(limit=30)
    df = WellnessAnalyticsEngine.records_to_dataframe(records)
    return jsonify({
        "avg_sleep_hours": round(float(df["total_sleep_hours"].mean()), 1) if not df.empty else 0,
        "avg_deep_hours": round(float(df["deep_sleep_hours"].mean()), 1) if not df.empty else 0,
        "avg_rem_hours": round(float(df["rem_sleep_hours"].mean()), 1) if not df.empty else 0,
        "avg_efficiency": int(df["sleep_efficiency"].mean()) if not df.empty else 0,
        "avg_latency": int(df["sleep_latency_minutes"].mean()) if not df.empty else 0
    })


@analytics_bp.route("/api/analytics/heart", methods=["GET"])
def get_heart_analytics():
    """Returns cardiovascular health and HRV metrics."""
    records = db.get_all_records(limit=30)
    df = WellnessAnalyticsEngine.records_to_dataframe(records)
    return jsonify({
        "avg_resting_hr": int(df["resting_hr"].mean()) if not df.empty else 0,
        "min_resting_hr": int(df["resting_hr"].min()) if not df.empty else 0,
        "avg_hrv": int(df["hrv_ms"].mean()) if not df.empty else 0,
        "max_hrv": int(df["hrv_ms"].max()) if not df.empty else 0
    })


@analytics_bp.route("/api/analytics/screen-time", methods=["GET"])
def get_screen_time_analytics():
    """Returns screen time engagement metrics."""
    records = db.get_all_records(limit=30)
    df = WellnessAnalyticsEngine.records_to_dataframe(records)
    return jsonify({
        "avg_screen_hours": round(float(df["total_screen_hours"].mean()), 1) if not df.empty else 0,
        "avg_late_screen_mins": int(df["late_night_screen_minutes"].mean()) if not df.empty else 0,
        "avg_pickups": int(df["pickup_count"].mean()) if not df.empty else 0
    })


@analytics_bp.route("/api/analytics/correlations", methods=["GET"])
def get_correlations():
    """Calculates cross-domain Pearson correlations revealing biological patterns."""
    records = db.get_all_records()
    correlations = WellnessAnalyticsEngine.calculate_correlations(records)
    return jsonify(correlations)


@analytics_bp.route("/api/analytics/clusters", methods=["GET"])
def get_clusters():
    """Runs KMeans clustering to categorize lifestyle days into archetypes."""
    records = db.get_all_records()
    clusters = WellnessAnalyticsEngine.cluster_behavioural_patterns(records)
    return jsonify(clusters)


@analytics_bp.route("/api/analytics/anomalies", methods=["GET"])
def get_anomalies():
    """Detects physiological outlier days using Isolation Forest."""
    records = db.get_all_records()
    anomalies = WellnessAnalyticsEngine.detect_anomalies(records)
    return jsonify({"count": len(anomalies), "anomalies": anomalies})


@analytics_bp.route("/api/analytics/timeseries", methods=["GET"])
def get_timeseries():
    """Provides optimized, synchronous arrays for Chart.js visualisations."""
    days = request.args.get("days", default=14, type=int)
    records = db.get_all_records(limit=days)

    labels = []
    dates = []
    steps = []
    active_minutes = []
    sleep_hours = []
    deep_sleep = []
    rem_sleep = []
    sleep_efficiency = []
    sleep_latency = []
    resting_hr = []
    hrv = []
    screen_hours = []
    late_screen_mins = []
    wellness_scores = []

    for r in records:
        date_str = r.get("date", "")
        dates.append(date_str)
        labels.append(date_str[5:])  # MM-DD

        act = r.get("activity", {})
        slp = r.get("sleep", {})
        hr = r.get("heart_rate", {})
        scr = r.get("screen_time", {})

        steps.append(act.get("steps", 0))
        active_minutes.append(act.get("active_minutes", 0))
        sleep_hours.append(slp.get("total_sleep_hours", 0.0))
        deep_sleep.append(slp.get("deep_sleep_hours", 0.0))
        rem_sleep.append(slp.get("rem_sleep_hours", 0.0))
        sleep_efficiency.append(slp.get("efficiency_score", 0))
        sleep_latency.append(slp.get("sleep_latency_minutes", 0))
        resting_hr.append(hr.get("resting_bpm", 0))
        hrv.append(hr.get("hrv_ms", 0))
        screen_hours.append(scr.get("total_screen_hours", 0.0))
        late_screen_mins.append(scr.get("late_night_screen_minutes", 0))
        wellness_scores.append(r.get("wellness_score", 0))

    return jsonify({
        "days": len(records),
        "labels": labels,
        "dates": dates,
        "datasets": {
            "steps": steps,
            "active_minutes": active_minutes,
            "sleep_hours": sleep_hours,
            "deep_sleep": deep_sleep,
            "rem_sleep": rem_sleep,
            "sleep_efficiency": sleep_efficiency,
            "sleep_latency": sleep_latency,
            "resting_hr": resting_hr,
            "hrv": hrv,
            "screen_hours": screen_hours,
            "late_screen_mins": late_screen_mins,
            "wellness_scores": wellness_scores
        }
    })
