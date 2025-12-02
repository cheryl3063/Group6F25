from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp


class TripSummaryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.summary = None

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        root.add_widget(Label(text="📄 Trip Summary", font_size=22, bold=True))

        self.metrics = Label(
            text="No trip loaded.",
            font_size=16,
            halign="left",
            valign="top",
            markup=True
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        btn_back = Button(text="⬅ Back to History", size_hint_y=None, height=dp(48))
        btn_back.bind(on_press=lambda *_: setattr(self.manager, "current", "history"))
        root.add_widget(btn_back)

        self.add_widget(root)

    def set_summary(self, summary):
        self.summary = summary
        self._render()

    def _render(self):
        if not self.summary:
            self.metrics.text = "No data yet."
            return

        s = self.summary
        self.metrics.text = (
            f"[b]{s.get('timestamp', 'No Timestamp')}[/b]\n\n"
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ Safety Score: [b]{s['safety_score']}[/b]"
        )
