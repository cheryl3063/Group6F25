from permissions_manager import PermissionManager
from sensors_listeners import SensorListener

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

# screens
from trip_screen import TripRecordingScreen
from analytics_screen import AnalyticsScreen


class DriveIQApp(App):
    """
    App wrapper that owns permissions + sensor listener and exposes
    start/stop methods for the screens to call.
    """
    def build(self):
        self.pm = PermissionManager()
        self.sensors = SensorListener()
        self.is_trip_running = False

        self.sm = ScreenManager()
        self.sm.add_widget(TripRecordingScreen(name="trip"))
        self.sm.add_widget(AnalyticsScreen(name="analytics"))
        self.sm.add_widget(ScoreScreen(name="score"))

        return self.sm

    def on_start(self):
        print("=== Trip Start: Permission Check ===")
        # Ask for permissions on launch
        self.pm.request_permissions()
        if not self.pm.validate_permissions():
            print("Trip cannot start without required permissions ❌")

    # -------- Trip control used by TripRecordingScreen --------
    def start_trip_recording(self):
        if self.is_trip_running:
            return
        print("Trip recording started successfully! 🚗💨")
        try:
            self.sensors.start_listeners()
        except Exception as e:
            print(f"[Sensors] start_listeners error: {e}")
        self.is_trip_running = True

    def stop_trip_recording(self):
        if not self.is_trip_running:
            return
        print("Trip recording stopped 🛑")
        try:
            # Some implementations expose stop_listeners; ignore if not present
            stop = getattr(self.sensors, "stop_listeners", None)
            if callable(stop):
                stop()
        except Exception as e:
            print(f"[Sensors] stop_listeners error: {e}")

        self.is_trip_running = False

        # Move to analytics and show the summary popup
        analytics = self.sm.get_screen("analytics")
        analytics.show_summary_popup()
        self.sm.current = "analytics"


def main():
    DriveIQApp().run()


if __name__ == "__main__":
    main()
