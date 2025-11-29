# mock_backend.py
import json
import os

# Path for mock saved trip file
SAVE_FILE = "latest_trip.json"


# =========================================================
#  WEEKLY TREND DATA  (Phase 2 requirement)
# =========================================================
def load_weekly_history():
    """Return static weekly performance trend."""
    return [
        {"day": "Mon", "score": 82},
        {"day": "Tue", "score": 90},
        {"day": "Wed", "score": 85},
        {"day": "Thu", "score": 88},
        {"day": "Fri", "score": 92},
        {"day": "Sat", "score": 80},
        {"day": "Sun", "score": 78},
    ]


# =========================================================
#  SAVE CURRENT TRIP SUMMARY
# =========================================================
def save_latest_trip(data):
    """
    Save trip summary (computed in Trip Summary Screen)
    so ScoreScreen can reload it.
    """
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception as exc:
        print(f"[mock_backend] Failed to save trip: {exc}")
        return False


# =========================================================
#  LOAD LAST SAVED TRIP SUMMARY
# =========================================================
def load_latest_trip():
    """
    Load summary for ScoreScreen.
    Returns None if file doesn't exist.
    """
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[mock_backend] Failed to load saved trip: {exc}")
        return None
