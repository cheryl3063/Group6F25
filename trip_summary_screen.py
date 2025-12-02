from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from trip_summary_utils import compute_summary
from mock_backend import save_latest_trip


class TripSummaryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.summary = None
        self.samples = []

        # Root container
        root = BoxLayout(
            orientation="vertical",
            padding=dp(32),
            spacing=dp(26),
            size_hint=(0.92, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Background card
        with root.canvas.before:
            Color(0.12, 0.12, 0.12, 0.92)
            self.bg_rect = RoundedRectangle(radius=[20])

        root.bind(pos=self._update_bg, size=self._update_bg)

        # Title
        title = Label(
            text="📄 Trip Summary",
            font_size=34,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(title)

        # Metrics block
        self.metrics = Label(
            text="No data yet.",
            font_size=22,
            color=(0.92, 0.92, 0.92, 1),
            halign="center",
            valign="middle"
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        # Button row
        btn_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(60)
        )

        back_btn = Button(
            text="⬅ Back",
            font_size=20,
            background_color=(0.22, 0.22, 0.22, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        btn_row.add_widget(back_btn)

        recalc_btn = Button(
            text="↻ Recompute",
            font_size=20,
            background_color=(0.10, 0.45, 0.82, 1),
            color=(1, 1, 1, 1)
        )
        recalc_btn.bind(on_press=lambda *_: self._render())
        btn_row.add_widget(recalc_btn)

        score_btn = Button(
            text="⭐ Score",
            font_size=20,
            background_color=(0.90, 0.68, 0.15, 1),
            color=(1, 1, 1, 1)
        )
        score_btn.bind(on_press=self.go_to_score)
        btn_row.add_widget(score_btn)

        root.add_widget(btn_row)
        self.add_widget(root)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.children[0].pos
        self.bg_rect.size = self.children[0].size

    def set_summary(self, summary):
        """Keep HEAD logic with timestamp formatting."""
        self.summary = summary

        self.metrics.text = (
            f"[b]{summary['timestamp']}[/b]\n\n"
            f"• Distance: {summary['total_distance_km']} km\n"
            f"• Avg Speed: {summary['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {summary['brake_events']}\n"
            f"• Harsh Accel: {summary['harsh_accel']}\n\n"
            f"⭐ Safety Score: [b]{summary['safety_score']}[/b]"
        )

    def set_samples(self, samples):
        self.samples = samples or []
        self._render()

    def _render(self):
        """Use backup UI logic + HEAD summary computation."""
        s = compute_summary(self.samples)

        self.metrics.text = (
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ Safety Score: {s['safety_score']}"
        )

        # Save for insights screen
        save_latest_trip({
            "total_distance_km": s["total_distance_km"],
            "avg_speed_kmh": s["avg_speed_kmh"],
            "brake_events": s["brake_events"],
            "harsh_accel": s["harsh_accel"],
            "safety_score": s["safety_score"]
        })

        # Auto-update score screen
        score_screen = self.manager.get_screen("score")
        score_screen.update_score({
            "score": s["safety_score"],
            "avg_speed": s["avg_speed_kmh"],
            "distance_km": s["total_distance_km"],
            "brake_events": s["brake_events"],
            "harsh_accel": s["harsh_accel"]
        })

    def go_to_score(self, *_):
        self.manager.current = "score"
