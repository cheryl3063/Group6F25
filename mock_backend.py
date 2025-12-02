import json
import os

SAVE_FILE = "latest_trip.json"


def load_weekly_history():
    """Static weekly performance trend for InsightsScreen."""
    return [
        {"day": "Mon", "score": 82},
        {"day": "Tue", "score": 90},
        {"day": "Wed", "score": 85},
        {"day": "Thu", "score": 88},
        {"day": "Fri", "score": 92},
        {"day": "Sat", "score": 80},
        {"day": "Sun", "score": 78},
    ]


def save_latest_trip(summary):
    """
    Save last summary for ScoreScreen.
    summary is expected to be:
    {
        "total_distance_km": ...,
        "avg_speed_kmh": ...,
        "brake_events": ...,
        "harsh_accel": ...,
        "safety_score": ...
        (optional) "timestamp": ...
    }
    """
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(summary, f, indent=2)
        return True
    except Exception as exc:
        print(f"[mock_backend] Failed to save trip: {exc}")
        return False


def load_latest_trip():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[mock_backend] Failed to load saved trip: {exc}")
        return None
