# data_buffer.py
import json
import os
from datetime import datetime

class DataBuffer:
    def __init__(self, file_path="trip_buffer.json"):
        self.file_path = file_path
        self.buffer = []

        # Load existing buffer if file exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    self.buffer = json.load(f)
            except:
                self.buffer = []

    def add_entry(self, data: dict):
        """Add a new sensor reading to the buffer."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **data
        }
        self.buffer.append(entry)
        self.save_to_file()

    def save_to_file(self):
        """Persist buffer to local JSON file."""
        with open(self.file_path, "w") as f:
            json.dump(self.buffer, f, indent=2)

    def load_file(self):
        """Load JSON file contents directly."""
        if not os.path.exists(self.file_path):
            return []
        with open(self.file_path, "r") as f:
            return json.load(f)

    def clear(self):
        """Clear memory + JSON file."""
        self.buffer = []
        with open(self.file_path, "w") as f:
            f.write("")
