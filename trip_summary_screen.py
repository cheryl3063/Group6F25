# trip_summary_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from trip_summary_utils import compute_summary

class TripSummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = []

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        self.title = Label(text="📄 Trip Summary", font_size=22, bold=True)
        root.add_widget(self.title)

        self.metrics = Label(
            text="No data yet.",
            font_size=16,
            halign="left",
            valign="top",
            markup=True
        )

        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.btn_back = Button(text="⬅ Back")
        self.btn_back.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        btn_row.add_widget(self.btn_back)

        self.btn_refresh = Button(text="↻ Recompute")
        self.btn_refresh.bind(on_press=lambda *_: self._render())
        btn_row.add_widget(self.btn_refresh)

        root.add_widget(btn_row)
        self.add_widget(root)

    def set_samples(self, samples):
        """Call this before showing the screen."""
        self.samples = samples or []
        self._render()

    def _render(self):
        s = compute_summary(self.samples)
        self.metrics.text = (
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ Safety Score: [b]{s['safety_score']}[/b]"
        )
