"""
Know Thyself AI - Habit Tracking & Notification Service
Manages daily habit checklists, streak counters, completion percentages,
consistency heatmaps, and smart in-app notifications.
"""

from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from backend.config import Config

HABITS_DB_PATH = Config.BASE_DIR / "backend" / "data" / "habits_db.json"

DEFAULT_HABITS = [
    {
        "id": "habit-sleep-curfew",
        "title": "Digital Curfew (45m pre-bed)",
        "category": "screen",
        "description": "Shut off screens or switch to grayscale 45 minutes prior to sleep",
        "icon": "smartphone",
        "target_days_per_week": 6
    },
    {
        "id": "habit-bedtime-window",
        "title": "Consistent Bedtime (23:15)",
        "category": "sleep",
        "description": "Retire to bed within a 20-minute window to stabilize circadian rhythm",
        "icon": "moon",
        "target_days_per_week": 7
    },
    {
        "id": "habit-steps-target",
        "title": "8,500 Daily Movement Steps",
        "category": "activity",
        "description": "Reach baseline physical step target to stimulate lymphatic flow",
        "icon": "footprints",
        "target_days_per_week": 6
    },
    {
        "id": "habit-daylight-walk",
        "title": "Morning Daylight Exposure",
        "category": "activity",
        "description": "15-minute morning outdoor walk to anchor cortisol awakening response",
        "icon": "sun",
        "target_days_per_week": 5
    },
    {
        "id": "habit-hrv-breathing",
        "title": "5-Min Box Breathing / Recovery",
        "category": "heart",
        "description": "Slow parasympathetic breathwork to increase vagal nerve tone & HRV",
        "icon": "heart",
        "target_days_per_week": 5
    }
]


class HabitService:
    """Manages habits, streaks, weekly progress, and in-app notifications."""

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        HABITS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not HABITS_DB_PATH.exists():
            # Seed 28 days of historical completions for demo realism
            end_date = datetime.now()
            history = {}
            for day_offset in range(28):
                d_str = (end_date - timedelta(days=day_offset)).strftime("%Y-%m-%d")
                # Random realistic completion pattern
                day_completed = []
                if day_offset % 7 != 0:  # mostly active
                    day_completed.append("habit-sleep-curfew")
                if day_offset % 2 == 0:
                    day_completed.append("habit-bedtime-window")
                if day_offset % 3 != 0:
                    day_completed.append("habit-steps-target")
                if day_offset % 4 != 0:
                    day_completed.append("habit-daylight-walk")
                if day_offset % 2 != 0:
                    day_completed.append("habit-hrv-breathing")
                history[d_str] = day_completed

            initial_data = {
                "habits": DEFAULT_HABITS,
                "completions": history
            }
            with open(HABITS_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_db(self) -> Dict:
        self._ensure_db()
        try:
            with open(HABITS_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"habits": DEFAULT_HABITS, "completions": {}}

    def _write_db(self, data: Dict):
        self._ensure_db()
        with open(HABITS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_habits_status(self, target_date: Optional[str] = None) -> Dict[str, Any]:
        """Returns habits list with today's completion state, streaks, and heatmap."""
        data = self._read_db()
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")

        today_completed = data.get("completions", {}).get(target_date, [])
        habits = data.get("habits", DEFAULT_HABITS)

        # Calculate streaks for each habit
        habits_with_stats = []
        for h in habits:
            h_id = h["id"]
            streak = 0
            check_date = datetime.now()
            # Count backward consecutive days
            for d in range(30):
                d_str = (check_date - timedelta(days=d)).strftime("%Y-%m-%d")
                day_list = data.get("completions", {}).get(d_str, [])
                if h_id in day_list:
                    streak += 1
                elif d > 0:  # streak broken
                    break

            habits_with_stats.append({
                **h,
                "is_completed_today": h_id in today_completed,
                "current_streak_days": streak,
                "status": "Completed Today" if h_id in today_completed else "Pending"
            })

        # Calculate 28-day consistency heatmap matrix (4 weeks x 7 days)
        heatmap = []
        now = datetime.now()
        for i in range(27, -1, -1):
            day_dt = now - timedelta(days=i)
            day_str = day_dt.strftime("%Y-%m-%d")
            completed_count = len(data.get("completions", {}).get(day_str, []))
            total_habits = len(habits)
            pct = round((completed_count / total_habits) * 100) if total_habits else 0
            heatmap.append({
                "date": day_str,
                "day_name": day_dt.strftime("%a"),
                "completed": completed_count,
                "total": total_habits,
                "percentage": pct,
                "level": 0 if pct == 0 else 1 if pct < 40 else 2 if pct < 75 else 3
            })

        # Today's overall completion percentage
        today_pct = round((len(today_completed) / len(habits)) * 100) if habits else 0

        return {
            "date": target_date,
            "completion_percentage": today_pct,
            "completed_count": len(today_completed),
            "total_habits": len(habits),
            "habits": habits_with_stats,
            "heatmap": heatmap
        }

    def toggle_habit(self, habit_id: str, target_date: Optional[str] = None) -> Dict:
        """Toggles completion state of a specific habit for a given date."""
        data = self._read_db()
        if not target_date:
            target_date = datetime.now().strftime("%Y-%m-%d")

        completions = data.get("completions", {})
        day_list = completions.get(target_date, [])

        if habit_id in day_list:
            day_list.remove(habit_id)
            state = False
        else:
            day_list.append(habit_id)
            state = True

        completions[target_date] = day_list
        data["completions"] = completions
        self._write_db(data)

        return {
            "habit_id": habit_id,
            "date": target_date,
            "is_completed": state,
            "today_completed_count": len(day_list)
        }

    def get_notifications(self, records_summary: Dict[str, Any]) -> List[Dict]:
        """Generates contextual in-app smart nudges and reminders."""
        notifications = []
        now = datetime.now()

        # Morning movement reminder
        notifications.append({
            "id": "notif-morning",
            "type": "activity",
            "title": "Morning Movement Target",
            "message": "Start your day with a 15-minute daylight walk to anchor your circadian rhythm.",
            "timestamp": "08:30 AM",
            "icon": "sun",
            "read": False
        })

        # Evening screen curfew reminder
        late_screen = records_summary.get("screen_time", {}).get("avg_late_screen_mins", 45)
        if late_screen > 35:
            notifications.append({
                "id": "notif-curfew",
                "type": "screen",
                "title": "Pre-Bed Digital Boundary",
                "message": f"Your data indicates pre-bed screen time delays sleep onset. Plan to dim devices by 22:30.",
                "timestamp": "21:00 PM",
                "icon": "eye-off",
                "read": False
            })

        # Goal achievement badge
        avg_steps = records_summary.get("activity", {}).get("avg_steps", 8000)
        if avg_steps >= 8000:
            notifications.append({
                "id": "notif-goal",
                "type": "achievement",
                "title": "Consistency Milestone!",
                "message": f"You maintained an average of {avg_steps:,} daily steps this week. Autonomic recovery index is high.",
                "timestamp": "Yesterday",
                "icon": "trophy",
                "read": True
            })

        return notifications


habit_service = HabitService()
