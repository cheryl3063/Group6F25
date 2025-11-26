from permissions_manager import PermissionManager
from sensors_listeners import SensorListener

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

# Screens
from trip_screen import TripRecordingScreen
from analytics_screen import AnalyticsScreen
from trip_summary_screen import TripSummaryScreen

# Scoring + backend
from trip_summary_utils import compute_summary
from mock_backend import save_score
import requests


class DriverApp(App):
    """
    Main controller for the Kivy application.
    Must include receive_trip_summary() for TripRecordingScreen.
    """
    def build(self):
        self.pm = PermissionManager()
        self.sensors = SensorListener()
        self.is_trip_running = False
        self.user_id = "user123"

        self.sm = ScreenManager()
        self.sm.add_widget(TripRecordingScreen(name="trip"))
        self.sm.add_widget(TripSummaryScreen(name="trip_summary"))
        self.sm.add_widget(AnalyticsScreen(name="analytics"))
        return self.sm

    def on_start(self):
        print("=== Startup: Checking Permissions ===")
        self.pm.request_permissions()
        if not self.pm.validate_permissions():
            print("❌ Permissions missing — some features may not work.")

    # ------------------------------------------------------------
    # TRIP CONTROL
    # ------------------------------------------------------------
    def start_trip_recording(self):
        if self.is_trip_running:
            return
        print("🚗 Trip recording started")

        try:
            self.sensors.start_listeners()
        except Exception as e:
            print(f"[Sensors] Error starting listeners: {e}")

        self.is_trip_running = True

    def stop_trip_recording(self):
        if not self.is_trip_running:
            return
        print("🛑 Trip recording stopped")

        try:
            stop = getattr(self.sensors, "stop_listeners", None)
            if callable(stop):
                stop()
        except Exception as e:
            print(f"[Sensors] stop_listeners error: {e}")

        self.is_trip_running = False

    # ------------------------------------------------------------
    # REQUIRED BY trip_screen.py
    # THIS IS THE FUNCTION KIVY WAS CRASHING ABOUT
    # ------------------------------------------------------------
    def receive_trip_summary(self, samples):
        print("\n=== App Received Raw Samples ===")
        print(samples)
        print("================================\n")

        # Compute summary
        summary = compute_summary(samples)
        print("\n=== FINAL SUMMARY ===")
        print(summary)
        print("======================\n")

        # Send to backend
        self._send_to_backend(summary)

        # Show summary screen
        summary_screen = self.sm.get_screen("trip_summary")
        summary_screen.set_samples(samples)
        self.sm.current = "trip_summary"

    # ------------------------------------------------------------
    # BACKEND SAVE
    # ------------------------------------------------------------
    def _send_to_backend(self, summary):
        url = "http://127.0.0.1:5050/save_trip"

        payload = {
            "user_id": self.user_id,
            "score": summary["safety_score"],
            "avg_speed": summary["avg_speed_kmh"],
            "distance_km": summary["total_distance_km"],
            "brake_events": summary["brake_events"],
            "harsh_accel": summary["harsh_accel"],
        }

        print("📡 Sending trip summary to backend...")
        try:
            r = requests.post(url, json=payload, timeout=3)
            print("BACKEND RESPONSE:", r.text)
        except Exception as e:
            print(f"[WARN] Backend unavailable → using mock backend.\nReason: {e}")
            save_score(self.user_id, payload)


def main():
    DriverApp().run()


if __name__ == "__main__":
    main()
