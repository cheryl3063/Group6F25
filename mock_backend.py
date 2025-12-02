import json
import os
from datetime import datetime

BACKEND_FILE = "mock_backend.json"


def save_score(user_id, score_data):
    """
    score_data example:
    {
        "score": 85,
        "avg_speed": 67,
        "distance_km": 12.4,
        "brake_events": 2,
        "harsh_accel": 1,
        "speeding_events": 3,
        "alerts": {
            "brakes": 2,
            "harsh_accel": 1,
            "speeding": 3
        }
    }
    """
    # Load existing file or create new
    if os.path.exists(BACKEND_FILE):
        try:
            with open(BACKEND_FILE, "r") as f:
                db = json.load(f)
        except Exception:
            # if file corrupted, reset
            db = {}
    else:
        db = {}

    # Ensure user entry exists
    if user_id not in db:
        db[user_id] = []

    # Create a safe copy so we can enrich it
    entry = dict(score_data)

    # Add timestamp if missing
    if "created_at" not in entry:
        entry["created_at"] = datetime.now().isoformat(timespec="seconds")

    # Add simple trip id if missing
    if "trip_id" not in entry:
        next_index = len(db[user_id]) + 1
        entry["trip_id"] = f"trip_{next_index}"

    # Add new score entry
    db[user_id].append(entry)

    # Save back to file
    with open(BACKEND_FILE, "w") as f:
        json.dump(db, f, indent=4)

    print(f"[MOCK BACKEND] Saved score for user {user_id}: {entry}")
