# trip_summary_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from trip_summary_utils import compute_summary


class TripSummaryScreen(Screen):
    """
    Shows a summary for ONE trip.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = []
        self.summary = None

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        self.title = Label(text="📄 Trip Summary", font_size=22, bold=True)
        root.add_widget(self.title)

        self.metrics = Label(
            text="No data yet.",
            font_size=16,
            halign="left",
            valign="top",
            markup=True,  # allow [b] tags for score
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        self.btn_back = Button(text="⬅ Back")
        self.btn_back.bind(on_press=self.go_back)
        btn_row.add_widget(self.btn_back)

        root.add_widget(btn_row)
        self.add_widget(root)

    # --------------------------------------------------
    # Called when trip just ended (from TripRecordingScreen)
    # --------------------------------------------------
    def set_samples(self, samples):
        """Called when real-time data finishes."""
        self.samples = samples or []
        self.summary = compute_summary(self.samples)
        self.render()

    # --------------------------------------------------
    # Called when history item is opened
    # --------------------------------------------------
    def set_summary(self, summary):
        """Called when history or backend passes a summary dict."""
        self.summary = summary or {}
        self.render()

    # --------------------------------------------------
    # Navigation: decide the best screen to go back to
    # --------------------------------------------------
    def go_back(self, *_):
        if not self.manager:
            return

        names = {screen.name for screen in self.manager.screens}

        # For login_ui_kivy.py flow
        if "dashboard" in names:
            self.manager.transition.direction = "right"
            self.manager.current = "dashboard"

        # For main.py + history flow
        elif "history" in names:
            self.manager.transition.direction = "right"
            self.manager.current = "history"

        # Fallback: go back to trip screen
        else:
            self.manager.transition.direction = "right"
            self.manager.current = "trip"

    # --------------------------------------------------
    # Update text on the screen
    # --------------------------------------------------
    def render(self):
        if not self.summary:
            self.metrics.text = "No trip data available."
            return

        s = self.summary
        self.metrics.text = (
            f"• Distance: {s.get('total_distance_km', 0)} km\n"
            f"• Avg Speed: {s.get('avg_speed_kmh', 0)} km/h\n"
            f"• Brake Events: {s.get('brake_events', 0)}\n"
            f"• Harsh Accel: {s.get('harsh_accel', 0)}\n\n"
            f"⭐ Safety Score: [b]{s.get('safety_score', 0)}[/b]"
        )
