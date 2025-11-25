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
            valign="top"
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        self.btn_back = Button(text="⬅ Back")
        self.btn_back.bind(on_press=self.go_back)
        btn_row.add_widget(self.btn_back)

        #----------#
        btn.bind(on_press=lambda *_: self.open_summary(trip))
        #---------#

        root.add_widget(btn_row)
        self.add_widget(root)

    def set_samples(self, samples):
        """Called when real-time data finishes."""
        self.samples = samples or []
        self.summary = compute_summary(self.samples)
        self.render()

    def set_summary(self, summary):
        """Called when history item is opened."""
        self.summary = summary
        self.render()

    def go_back(self, *_):
        self.manager.current = "history"

    def render(self):
        if not self.summary:
            self.metrics.text = "No trip data available."
            return

        def set_summary(self, summary):
            """Called by main.py to set trip summary."""
            self.metrics.text = (
                f"• Distance: {summary['total_distance_km']} km\n"
                f"• Avg Speed: {summary['avg_speed_kmh']} km/h\n"
                f"• Brake Events: {summary['brake_events']}\n"
                f"• Harsh Accel: {summary['harsh_accel']}\n\n"
                f"⭐ Safety Score: [b]{summary['safety_score']}[/b]"
            )

        s = self.summary
        self.metrics.text = (
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ Safety Score: [b]{s['safety_score']}[/b]"
        )
