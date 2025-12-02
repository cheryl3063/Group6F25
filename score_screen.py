from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp

from mock_backend import load_latest_trip


class ScoreScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_summary = None

        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(16))

        root.add_widget(Label(text="⭐ Driver Score", font_size=26, bold=True))

        self.score_label = Label(text="No score yet.", font_size=20, markup=True)
        root.add_widget(self.score_label)

        btn_row = Boxlayout = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))

        back_btn = Button(text="⬅ Dashboard")
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        btn_row.add_widget(back_btn)

        refresh_btn = Button(text="↻ Reload")
        refresh_btn.bind(on_press=lambda *_: self.load_from_file())
        btn_row.add_widget(refresh_btn)

        root.add_widget(btn_row)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.load_from_file()

    def load_from_file(self):
        summary = load_latest_trip()
        if summary:
            self.update_score(summary)
        else:
            self.score_label.text = "No recent trip summary found."

    def update_score(self, summary):
        self.current_summary = summary
        self.score_label.text = (
            f"[b>Safety Score:[/b] {summary['safety_score']}\n\n"
            f"Distance: {summary['total_distance_km']} km\n"
            f"Avg Speed: {summary['avg_speed_kmh']} km/h\n"
            f"Brakes: {summary['brake_events']}  |  "
            f"Harsh Accel: {summary['harsh_accel']}"
        )
