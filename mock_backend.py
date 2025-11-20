import json
import os

BACKEND_FILE = "mock_backend.json"


def save_score(user_id, score_data):
    """
    score_data example:
    {
        "score": 85,
        "avg_speed": 67,
        "distance_km": 12.4
    }
    """
    # Load existing file or create new
    if os.path.exists(BACKEND_FILE):
        with open(BACKEND_FILE, "r") as f:
            db = json.load(f)
    else:
        db = {}

    # Ensure user entry exists
    if user_id not in db:
        db[user_id] = []

    # Add new score entry
    db[user_id].append(score_data)

    # Save back to file
    with open(BACKEND_FILE, "w") as f:
        json.dump(db, f, indent=4)

    print(f"[MOCK BACKEND] Saved score for user {user_id}: {score_data}")
