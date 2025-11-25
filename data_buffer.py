# data_buffer.py
import json
import os
from datetime import datetime


class DataBuffer:
    """
    Handles REAL-TIME trip sample buffering AND storing completed trips.
    """
    def __init__(self,
                 sample_file="trip_buffer.json",
                 trips_file="trip_history.json"):

        self.sample_file = sample_file
        self.trips_file = trips_file
        self.buffer = []

        # Load existing sample buffer
        if os.path.exists(self.sample_file):
            try:
                with open(self.sample_file, "r") as f:
                    self.buffer = json.load(f)
            except:
                self.buffer = []

    # -------------------------
    # REAL-TIME SAMPLE RECORDING
    # -------------------------
    def add_entry(self, data: dict):
        """Add a new sensor reading to the buffer."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **data
        }
        self.buffer.append(entry)
        self._save_samples()

    def _save_samples(self):
        """Save current trip samples to JSON."""
        with open(self.sample_file, "w") as f:
            json.dump(self.buffer, f, indent=2)

    # -------------------------
    # END OF TRIP → STORE HISTORY
    # -------------------------
    def save_completed_trip(self, summary: dict):
        """
        Called when a trip stops.
        Adds a summary object to trip_history.json.
        """
        trips = []

        if os.path.exists(self.trips_file):
            try:
                with open(self.trips_file, "r") as f:
                    trips = json.load(f)
            except:
                trips = []

        trip_record = {
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        }

        trips.append(trip_record)

        with open(self.trips_file, "w") as f:
            json.dump(trips, f, indent=2)

        # Clear real-time buffer after saving
        self.clear_samples()

    def clear_samples(self):
        """Clears sample buffer after trip ends."""
        self.buffer = []
        with open(self.sample_file, "w") as f:
            f.write("")

    # -------------------------
    # LOAD TRIP HISTORY
    # -------------------------
    def load_trip_history(self):
        if not os.path.exists(self.trips_file):
            return []

        with open(self.trips_file, "r") as f:
            return json.load(f)

def get_samples(self):
    return self.buffer
