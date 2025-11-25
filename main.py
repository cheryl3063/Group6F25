from permissions_manager import PermissionManager
from sensors_listeners import SensorListener
from data_buffer import DataBuffer
from trip_summary_utils import compute_summary

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

# Screens
from trip_screen import TripRecordingScreen
from analytics_screen import AnalyticsScreen
from trip_summary_screen import TripSummaryScreen
from trip_history_screen import TripHistoryScreen


class DriveIQApp(App):

    def build(self):
        self.pm = PermissionManager()
        self.sensors = SensorListener()
        self.buffer = DataBuffer()
        self.is_trip_running = False

        self.sm = ScreenManager()
        self.sm.add_widget(TripRecordingScreen(name="trip"))
        self.sm.add_widget(AnalyticsScreen(name="analytics"))
        self.sm.add_widget(TripHistoryScreen(name="history"))
        self.sm.add_widget(TripSummaryScreen(name="summary"))
        return self.sm

    def on_start(self):
        print("=== Trip Start: Permission Check ===")
        self.pm.request_permissions()
        if not self.pm.validate_permissions():
            print("Trip cannot start without required permissions ❌")

    # ------------------------
    # TRIP CONTROL
    # ------------------------
    def start_trip_recording(self):
        if self.is_trip_running:
            return

        print("Trip recording started successfully! 🚗💨")
        try:
            self.sensors.start_listeners(self.buffer)
        except Exception as e:
            print(f"[Sensors] start_listeners error: {e}")

        self.is_trip_running = True

    def stop_trip_recording(self):
        if not self.is_trip_running:
            return

        print("Trip recording stopped 🛑")
        try:
            stop = getattr(self.sensors, "stop_listeners", None)
            if callable(stop):
                stop()
        except Exception as e:
            print(f"[Sensors] stop_listeners error: {e}")

        samples = self.buffer.load_file()
        summary = compute_summary(samples)

        # Save to trip history
        self.buffer.save_completed_trip(summary)

        # Move to summary screen
        summary_screen = self.sm.get_screen("summary")
        summary_screen.set_summary(summary)
        self.sm.current = "summary"

        self.is_trip_running = False


def main():
    DriveIQApp().run()


if __name__ == "__main__":
    main()
