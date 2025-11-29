# trip_manager.py
import json
import os
import uuid
from datetime import datetime

BACKEND_FILE = "saved_trips.json"


class TripManager:
    def __init__(self, user_id="user123"):
        self.user_id = user_id

    # ---------------------------------------------------------
    def _load_backend(self):
        """Safe load backend JSON."""
        if not os.path.exists(BACKEND_FILE):
            print("⚠ No backend found → starting fresh.")
            return {}

        try:
            with open(BACKEND_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except Exception as e:
            print("ERROR reading backend:", e)
            return {}

    # ---------------------------------------------------------
    def _save_backend(self, data):
        """Safe write backend JSON."""
        try:
            with open(BACKEND_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("ERROR writing backend:", e)

    # ---------------------------------------------------------
    def _compute_summary(self, samples):
        """Compute trip summary."""
        if not samples:
            return {
                "total_distance_km": 0,
                "avg_speed_kmh": 0,
                "brake_events": 0,
                "harsh_accel": 0,
                "safety_score": 0
            }

        total_distance = sum(s["distance_km"] for s in samples)
        avg_speed = sum(s["speed"] for s in samples) / len(samples)
        total_brake = sum(s["brake_events"] for s in samples)
        total_harsh = sum(s["harsh_accel"] for s in samples)

        # Simple scoring
        score = max(0, 100 - (total_brake * 5 + total_harsh * 7))

        return {
            "total_distance_km": round(total_distance, 2),
            "avg_speed_kmh": round(avg_speed, 1),
            "brake_events": total_brake,
            "harsh_accel": total_harsh,
            "safety_score": score
        }

    # ---------------------------------------------------------
    def end_trip_and_save(self, samples):
        """Compute summary, attach trip_id, save to backend."""
        backend = self._load_backend()

        if self.user_id not in backend:
            backend[self.user_id] = []

        summary = self._compute_summary(samples)

        trip_entry = {
            "trip_id": str(uuid.uuid4()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "samples": samples,
            "summary": summary
        }

        backend[self.user_id].append(trip_entry)

        backend[self.user_id].sort(
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )

        self._save_backend(backend)

        print(f"[MOCK BACKEND] Saved trip for {self.user_id}")
        return summary

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------
    def get_all_trips(self):
        backend = self._load_backend()
        return backend.get(self.user_id, [])

    def get_latest_trip(self):
        trips = self.get_all_trips()
        return trips[0] if trips else None

    def get_latest_score(self):
        trip = self.get_latest_trip()
        if trip:
            return trip["summary"]["safety_score"]
        return None

    def get_stats_for_analytics(self):
        trips = self.get_all_trips()
        if not trips:
            return {
                "average_score": 0,
                "total_distance": 0.0,
                "trips": 0
            }

        total_distance = sum(t["summary"]["total_distance_km"] for t in trips)
        total_score = sum(t["summary"]["safety_score"] for t in trips)

        return {
            "average_score": round(total_score / len(trips), 1),
            "total_distance": round(total_distance, 2),
            "trips": len(trips)
        }
