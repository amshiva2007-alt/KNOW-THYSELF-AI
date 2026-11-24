"""
Know Thyself AI - Analytics Engine
Harnesses Python, Pandas, and Scikit-learn for advanced wellness data processing:
- Multidimensional correlation matrices
- Isolation Forest anomaly detection for disrupted days
- KMeans unsupervised clustering of behavioural lifestyle archetypes
- Time-series aggregates & holistic health scoring
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class WellnessAnalyticsEngine:
    """Scientific analytics engine for Activity, Sleep, Heart Rate & Screen Time."""

    @staticmethod
    def records_to_dataframe(records: List[Dict]) -> pd.DataFrame:
        """Flattens nested wellness record dictionaries into a tidy Pandas DataFrame."""
        if not records:
            return pd.DataFrame()

        flattened = []
        for r in records:
            act = r.get("activity", {})
            slp = r.get("sleep", {})
            hr = r.get("heart_rate", {})
            scr = r.get("screen_time", {})

            flattened.append({
                "id": r.get("id"),
                "date": r.get("date"),
                "wellness_score": r.get("wellness_score", 0),
                # Activity
                "steps": act.get("steps", 0),
                "active_minutes": act.get("active_minutes", 0),
                "distance_km": act.get("distance_km", 0.0),
                "calories_burned": act.get("calories_burned", 0),
                "workout_type": act.get("workout_type", "None"),
                # Sleep
                "total_sleep_hours": slp.get("total_sleep_hours", 0.0),
                "deep_sleep_hours": slp.get("deep_sleep_hours", 0.0),
                "rem_sleep_hours": slp.get("rem_sleep_hours", 0.0),
                "light_sleep_hours": slp.get("light_sleep_hours", 0.0),
                "sleep_efficiency": slp.get("efficiency_score", 0),
                "sleep_latency_minutes": slp.get("sleep_latency_minutes", 0),
                # Heart Rate
                "resting_hr": hr.get("resting_bpm", 0),
                "average_hr": hr.get("average_bpm", 0),
                "max_hr": hr.get("max_bpm", 0),
                "hrv_ms": hr.get("hrv_ms", 0),
                # Screen Time
                "total_screen_hours": scr.get("total_screen_hours", 0.0),
                "late_night_screen_minutes": scr.get("late_night_screen_minutes", 0),
                "productivity_hours": scr.get("productivity_hours", 0.0),
                "entertainment_hours": scr.get("entertainment_social_hours", 0.0),
                "pickup_count": scr.get("pickup_count", 0),
            })

        df = pd.DataFrame(flattened)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        return df

    @classmethod
    def calculate_correlations(cls, records: List[Dict]) -> Dict[str, Any]:
        """Calculates key cross-domain Pearson correlations revealing hidden lifestyle impacts."""
        df = cls.records_to_dataframe(records)
        if len(df) < 3:
            return {"correlations": {}, "key_findings": []}

        numeric_cols = [
            "steps", "active_minutes", "total_sleep_hours", "deep_sleep_hours",
            "sleep_efficiency", "sleep_latency_minutes", "resting_hr", "hrv_ms",
            "total_screen_hours", "late_night_screen_minutes", "wellness_score"
        ]
        
        corr_matrix = df[numeric_cols].corr().fillna(0)
        
        # Extract targeted biological relationships
        corr_late_screen_latency = round(float(corr_matrix.loc["late_night_screen_minutes", "sleep_latency_minutes"]), 2)
        corr_late_screen_deep = round(float(corr_matrix.loc["late_night_screen_minutes", "deep_sleep_hours"]), 2)
        corr_activity_hrv = round(float(corr_matrix.loc["active_minutes", "hrv_ms"]), 2)
        corr_activity_deep = round(float(corr_matrix.loc["active_minutes", "deep_sleep_hours"]), 2)
        corr_resting_sleep_eff = round(float(corr_matrix.loc["resting_hr", "sleep_efficiency"]), 2)
        corr_screen_wellness = round(float(corr_matrix.loc["total_screen_hours", "wellness_score"]), 2)

        findings = []
        if corr_late_screen_latency > 0.3:
            findings.append({
                "type": "negative_impact",
                "metric_pair": "Late Screen Time → Sleep Latency",
                "coefficient": corr_late_screen_latency,
                "summary": f"Strong positive correlation ({corr_late_screen_latency}): Late screen usage significantly delays your time to fall asleep."
            })
        if corr_late_screen_deep < -0.3:
            findings.append({
                "type": "negative_impact",
                "metric_pair": "Late Screen Time → Deep Sleep",
                "coefficient": corr_late_screen_deep,
                "summary": f"Inverse correlation ({corr_late_screen_deep}): Extended pre-bed device use reduces restorative slow-wave deep sleep."
            })
        if corr_activity_deep > 0.3:
            findings.append({
                "type": "positive_boost",
                "metric_pair": "Active Minutes → Deep Sleep",
                "coefficient": corr_activity_deep,
                "summary": f"Synergistic link ({corr_activity_deep}): Higher physical activity during daylight hours enhances restorative sleep depth."
            })
        if corr_activity_hrv > 0.25:
            findings.append({
                "type": "positive_boost",
                "metric_pair": "Exercise → Heart Rate Variability (HRV)",
                "coefficient": corr_activity_hrv,
                "summary": f"Autonomic boost ({corr_activity_hrv}): Consistent workouts improve nervous system flexibility and recovery index."
            })

        return {
            "correlations": {
                "screen_latency": corr_late_screen_latency,
                "screen_deep_sleep": corr_late_screen_deep,
                "activity_hrv": corr_activity_hrv,
                "activity_deep_sleep": corr_activity_deep,
                "resting_hr_efficiency": corr_resting_sleep_eff,
                "screen_wellness": corr_screen_wellness
            },
            "findings": findings
        }

    @classmethod
    def detect_anomalies(cls, records: List[Dict]) -> List[Dict]:
        """Detects atypical days using Scikit-learn Isolation Forest."""
        df = cls.records_to_dataframe(records)
        if len(df) < 5:
            return []

        features = ["steps", "total_sleep_hours", "deep_sleep_hours", "resting_hr", "late_night_screen_minutes"]
        X = df[features].fillna(df[features].mean())

        # Fit Isolation Forest
        iso = IsolationForest(contamination=0.15, random_state=42)
        preds = iso.fit_predict(X)  # -1 for anomalies, 1 for normal

        anomalies = []
        for idx, pred in enumerate(preds):
            if pred == -1:
                row = df.iloc[idx]
                reasons = []
                if row["late_night_screen_minutes"] > df["late_night_screen_minutes"].quantile(0.85):
                    reasons.append("Extreme late night screen exposure")
                if row["total_sleep_hours"] < df["total_sleep_hours"].quantile(0.15):
                    reasons.append("Severe sleep deprivation")
                if row["steps"] < df["steps"].quantile(0.15):
                    reasons.append("Unusual physical inactivity")
                if row["resting_hr"] > df["resting_hr"].quantile(0.85):
                    reasons.append("Elevated resting heart rate (cardiovascular load)")

                anomalies.append({
                    "date": row["date"].strftime("%Y-%m-%d"),
                    "wellness_score": int(row["wellness_score"]),
                    "reasons": reasons if reasons else ["Atypical physiological combination"]
                })

        return anomalies

    @classmethod
    def cluster_behavioural_patterns(cls, records: List[Dict]) -> Dict[str, Any]:
        """Clusters daily lifestyle data into 3 distinct behavioural archetypes using KMeans."""
        df = cls.records_to_dataframe(records)
        if len(df) < 6:
            return {"clusters": []}

        features = ["steps", "active_minutes", "total_sleep_hours", "deep_sleep_hours", "late_night_screen_minutes", "hrv_ms"]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df[features].fillna(df[features].mean()))

        n_clusters = min(3, len(df))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        df["cluster"] = labels
        clusters_summary = []

        archetype_names = [
            {"title": "High Energy & Restored", "badge": "Optimal", "color": "teal"},
            {"title": "Digital Overdrive & Fatigued", "badge": "Needs Balance", "color": "violet"},
            {"title": "Sedentary Baseline", "badge": "Moderate", "color": "navy"}
        ]

        for c_id in range(n_clusters):
            c_df = df[df["cluster"] == c_id]
            avg_steps = int(c_df["steps"].mean())
            avg_sleep = round(float(c_df["total_sleep_hours"].mean()), 1)
            avg_late_screen = int(c_df["late_night_screen_minutes"].mean())
            avg_hrv = int(c_df["hrv_ms"].mean())
            avg_score = int(c_df["wellness_score"].mean())

            # Assign best matching archetype based on attributes
            if avg_score >= 78 or avg_steps > 8500:
                arch = archetype_names[0]
            elif avg_late_screen > 65 or avg_score < 65:
                arch = archetype_names[1]
            else:
                arch = archetype_names[2]

            clusters_summary.append({
                "cluster_id": c_id,
                "name": arch["title"],
                "badge": arch["badge"],
                "color": arch["color"],
                "day_count": len(c_df),
                "percentage": round((len(c_df) / len(df)) * 100, 1),
                "metrics": {
                    "avg_steps": avg_steps,
                    "avg_sleep_hours": avg_sleep,
                    "avg_late_screen_mins": avg_late_screen,
                    "avg_hrv_ms": avg_hrv,
                    "avg_wellness_score": avg_score
                }
            })

        return {"clusters": clusters_summary}

    @classmethod
    def get_summary_metrics(cls, records: List[Dict], days: int = 7) -> Dict[str, Any]:
        """Calculates dashboard headline metrics and period changes."""
        df = cls.records_to_dataframe(records)
        if df.empty:
            return {}

        current_slice = df.tail(days)
        prev_slice = df.iloc[-2 * days: -days] if len(df) >= 2 * days else current_slice

        def safe_mean(slice_df, col):
            return float(slice_df[col].mean()) if col in slice_df and not slice_df.empty else 0.0

        curr_steps = int(safe_mean(current_slice, "steps"))
        prev_steps = int(safe_mean(prev_slice, "steps"))

        curr_sleep = round(safe_mean(current_slice, "total_sleep_hours"), 1)
        prev_sleep = round(safe_mean(prev_slice, "total_sleep_hours"), 1)

        curr_hr = int(safe_mean(current_slice, "resting_hr"))
        prev_hr = int(safe_mean(prev_slice, "resting_hr"))

        curr_screen = round(safe_mean(current_slice, "total_screen_hours"), 1)
        prev_screen = round(safe_mean(prev_slice, "total_screen_hours"), 1)

        curr_score = int(safe_mean(current_slice, "wellness_score"))
        prev_score = int(safe_mean(prev_slice, "wellness_score"))

        curr_hrv = int(safe_mean(current_slice, "hrv_ms"))

        return {
            "period_days": days,
            "overall_score": {
                "value": curr_score,
                "change": curr_score - prev_score,
                "status": "Optimal" if curr_score >= 80 else "Good" if curr_score >= 68 else "Needs Attention"
            },
            "activity": {
                "avg_steps": curr_steps,
                "change": curr_steps - prev_steps,
                "avg_active_mins": int(safe_mean(current_slice, "active_minutes")),
                "total_calories": int(current_slice["calories_burned"].sum())
            },
            "sleep": {
                "avg_hours": curr_sleep,
                "change": round(curr_sleep - prev_sleep, 1),
                "avg_deep_hours": round(safe_mean(current_slice, "deep_sleep_hours"), 1),
                "avg_efficiency": int(safe_mean(current_slice, "sleep_efficiency")),
                "avg_latency": int(safe_mean(current_slice, "sleep_latency_minutes"))
            },
            "heart_rate": {
                "avg_resting_bpm": curr_hr,
                "change": curr_hr - prev_hr,
                "avg_hrv_ms": curr_hrv
            },
            "screen_time": {
                "avg_hours": curr_screen,
                "change": round(curr_screen - prev_screen, 1),
                "avg_late_screen_mins": int(safe_mean(current_slice, "late_night_screen_minutes"))
            }
        }
