# mock_backend.py
import json
import os

MOCK_PATH = "mock_latest_trip.json"


def save_latest_trip(summary_dict):
    """Save the most recent trip summary to a mock JSON file."""
    with open(MOCK_PATH, "w") as f:
        json.dump(summary_dict, f, indent=4)


def load_latest_trip():
    """Load the most recent trip summary, if it exists."""
    if not os.path.exists(MOCK_PATH):
        return None
    with open(MOCK_PATH, "r") as f:
        return json.load(f)
