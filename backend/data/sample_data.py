"""
Know Thyself AI - Sample Wellness Dataset Generator
Generates realistic, scientifically correlated 30-day wellness records
combining Activity, Sleep, Heart Rate, and Screen-Time metrics.
"""

from datetime import datetime, timedelta
import json
import math
import os
import random


def generate_30day_wellness_dataset():
    """Generates 30 days of coherent wellness data with realistic biological correlations."""
    random.seed(42)  # Seed for reproducible realistic demo data
    records = []
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=29)
    
    for day_idx in range(30):
        current_date = start_date + timedelta(days=day_idx)
        date_str = current_date.strftime("%Y-%m-%d")
        day_of_week = current_date.weekday()  # 5=Saturday, 6=Sunday
        is_weekend = day_of_week in [5, 6]
        
        # Base activity: weekends or weekdays
        if is_weekend:
            steps = int(random.gauss(6500, 2000))
            screen_hours = round(max(3.5, random.gauss(7.8, 1.4)), 1)
            late_night_screen = int(max(20, random.gauss(85, 30)))
            workout = random.choice(["Hiking", "Cycling", "Long Walk", "Rest"])
        else:
            steps = int(random.gauss(9200, 1800))
            screen_hours = round(max(4.0, random.gauss(8.5, 1.2)), 1)
            late_night_screen = int(max(10, random.gauss(55, 25)))
            workout = random.choice(["Running", "Strength Training", "HIIT", "Yoga", "Brisk Walk"])
            
        steps = max(3500, min(16000, steps))
        active_mins = int(steps / 115) + random.randint(-8, 15)
        active_mins = max(15, min(120, active_mins))
        distance_km = round(steps * 0.00078, 2)
        calories = int(1750 + (steps * 0.045) + (active_mins * 3.5) + random.randint(-40, 60))
        
        # Screen time breakdowns
        late_night_screen = min(150, late_night_screen)
        productivity_hrs = round(max(1.0, screen_hours * random.uniform(0.45, 0.65)), 1)
        entertainment_hrs = round(max(0.5, screen_hours - productivity_hrs), 1)
        pickups = int(screen_hours * random.randint(9, 14))
        
        # Biological impact of late-night screen time and activity on sleep:
        # High late night screen time increases sleep latency and reduces deep sleep
        sleep_latency = int(12 + (late_night_screen * 0.22) + random.randint(-4, 8))
        sleep_latency = max(8, min(65, sleep_latency))
        
        # Total sleep
        base_sleep = 7.6 if is_weekend else 7.1
        sleep_penalty = (late_night_screen / 120.0) * 0.9
        activity_bonus = (active_mins / 90.0) * 0.4
        total_sleep = round(max(4.8, min(9.2, base_sleep - sleep_penalty + activity_bonus + random.gauss(0, 0.35))), 2)
        
        # Sleep stages
        deep_ratio = max(0.10, min(0.26, 0.20 - (late_night_screen * 0.0007) + (active_mins * 0.0008)))
        rem_ratio = max(0.18, min(0.28, 0.23 - (sleep_latency * 0.001)))
        deep_hours = round(total_sleep * deep_ratio, 2)
        rem_hours = round(total_sleep * rem_ratio, 2)
        light_hours = round(total_sleep - (deep_hours + rem_hours), 2)
        
        efficiency = int(max(60, min(96, 92 - (sleep_latency * 0.35) - (late_night_screen * 0.08) + random.randint(-3, 4))))
        
        # Heart rate dynamics
        # High activity + good sleep yields higher HRV and lower resting HR
        resting_hr = int(64 - (active_mins * 0.05) + (late_night_screen * 0.04) + random.gauss(0, 2))
        resting_hr = max(52, min(78, resting_hr))
        avg_hr = resting_hr + random.randint(8, 16)
        max_hr = int(125 + (active_mins * 0.35) + random.randint(-8, 12))
        
        # HRV (Heart Rate Variability in ms) - Higher is healthier
        hrv = int(62 + (deep_hours * 8.5) - (late_night_screen * 0.12) - (resting_hr * 0.25) + random.gauss(0, 4))
        hrv = max(28, min(92, hrv))
        
        # Composite Wellness Score (0 - 100)
        # Weighted formula reflecting holistic state
        score_activity = min(100, (steps / 10000) * 35 + (active_mins / 45) * 65)
        score_sleep = (efficiency * 0.6) + ((total_sleep / 8.0) * 40)
        score_heart = max(0, min(100, 100 - (resting_hr - 55) * 2.2 + (hrv - 45) * 0.8))
        score_screen = max(0, min(100, 100 - (screen_hours * 6.5) - (late_night_screen * 0.25)))
        
        composite_score = int(round(
            (score_activity * 0.30) + 
            (score_sleep * 0.35) + 
            (score_heart * 0.20) + 
            (score_screen * 0.15)
        ))
        composite_score = max(40, min(98, composite_score))
        
        # Behavioural Insight tags
        tags = []
        if late_night_screen > 75:
            tags.append("High Pre-Sleep Screen Exposure")
        if sleep_latency > 30:
            tags.append("Delayed Sleep Onset")
        if deep_hours >= 1.6:
            tags.append("High Deep Sleep Recovery")
        if steps >= 10000:
            tags.append("Active Day Target Met")
        if hrv < 45:
            tags.append("Autonomic Fatigue Indicator")
        if not tags:
            tags.append("Balanced Baseline")
            
        record = {
            "id": f"day-{date_str}",
            "date": date_str,
            "timestamp": f"{date_str}T23:59:59Z",
            "activity": {
                "steps": steps,
                "active_minutes": active_mins,
                "distance_km": distance_km,
                "calories_burned": calories,
                "workout_type": workout
            },
            "sleep": {
                "total_sleep_hours": total_sleep,
                "deep_sleep_hours": deep_hours,
                "rem_sleep_hours": rem_hours,
                "light_sleep_hours": light_hours,
                "efficiency_score": efficiency,
                "sleep_latency_minutes": sleep_latency,
                "bedtime": f"{'00' if late_night_screen > 80 else '23'}:{random.randint(10, 50):02d}",
                "wake_time": f"0{random.randint(6, 8)}:{random.randint(10, 45):02d}"
            },
            "heart_rate": {
                "resting_bpm": resting_hr,
                "average_bpm": avg_hr,
                "max_bpm": max_hr,
                "hrv_ms": hrv
            },
            "screen_time": {
                "total_screen_hours": screen_hours,
                "late_night_screen_minutes": late_night_screen,
                "productivity_hours": productivity_hrs,
                "entertainment_social_hours": entertainment_hrs,
                "pickup_count": pickups
            },
            "wellness_score": composite_score,
            "tags": tags
        }
        records.append(record)
        
    return records


def export_sample_data_file(filepath=None):
    """Exports sample records to json file."""
    if filepath is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "..", "sample_data", "wellness_demo.json")
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    dataset = generate_30day_wellness_dataset()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)
    return dataset


if __name__ == "__main__":
    data = export_sample_data_file()
    print(f"Generated {len(data)} sample wellness records successfully.")
