import json
import os
import uuid
from datetime import datetime

BACKEND_FILE = "mock_backend.json"


def save_score(user_id, summary_data):
    """
    summary_data is expected to contain:
    {
        "score": 85,
        "avg_speed": 67,
        "distance_km": 12.4,
        "brake_events": 3,
        "harsh_accel": 1
    }
    """

    # Load existing file or create new
    if os.path.exists(BACKEND_FILE):
        with open(BACKEND_FILE, "r") as f:
            try:
                db = json.load(f)
            except:
                db = {}
    else:
        db = {}

    # Ensure user key exists
    if user_id not in db:
        db[user_id] = []

    # Create a proper trip entry (matching TripManager format)
    trip_entry = {
        "trip_id": str(uuid.uuid4()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "samples": [],     # mock backend does not store samples
        "summary": summary_data
    }

    # Save entry
    db[user_id].append(trip_entry)

    # Write back to JSON file
    with open(BACKEND_FILE, "w") as f:
        json.dump(db, f, indent=4)

    print(f"[MOCK BACKEND] Saved new-format trip for user {user_id}: {trip_entry}")
