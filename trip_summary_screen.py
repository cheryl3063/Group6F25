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

        root = BoxLayout(
            orientation="vertical",
            padding=dp(32),
            spacing=dp(26),
            size_hint=(0.92, 0.92),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        with root.canvas.before:
            Color(0.12, 0.12, 0.12, 0.92)
            self.bg_rect = RoundedRectangle(radius=[20])

        root.bind(pos=self._update_bg, size=self._update_bg)

        title = Label(
            text="📄 Trip Summary",
            font_size=30,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(title)

        self.metrics = Label(
            text="No data yet.",
            font_size=20,
            color=(0.92, 0.92, 0.92, 1),
            halign="center",
            valign="middle",
            markup=True
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        btn_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint_y=None,
            height=dp(60)
        )

        back_btn = Button(
            text="⬅ Dashboard",
            font_size=18,
            background_color=(0.22, 0.22, 0.22, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        btn_row.add_widget(back_btn)

        history_btn = Button(
            text="📚 History",
            font_size=18,
            background_color=(0.15, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        history_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "history"))
        btn_row.add_widget(history_btn)

        score_btn = Button(
            text="⭐ Score",
            font_size=18,
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

    # -------- APIs --------
    def set_summary(self, summary):
        """
        Receives a summary dict (usually from TripManager or history),
        optionally containing 'timestamp'.
        """
        self.summary = summary
        self.samples = []  # reset
        self._render_from_summary()

    def set_samples(self, samples):
        """
        Optional: compute summary from raw samples using compute_summary().
        """
        self.samples = samples or []
        self.summary = compute_summary(self.samples)
        self._render_from_summary()

    def _render_from_summary(self):
        if not self.summary:
            self.metrics.text = "No data yet."
            return

        s = self.summary
        timestamp = s.get("timestamp", "Most recent trip")

        self.metrics.text = (
            f"[b]{timestamp}[/b]\n\n"
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ Safety Score: [b]{s['safety_score']}[/b]"
        )

        # Save for Score & Insights screens
        save_latest_trip(s)

        # Auto-update score screen if present
        try:
            score_screen = self.manager.get_screen("score")
            score_screen.update_score(s)
        except Exception:
            pass

    def go_to_score(self, *_):
        self.manager.current = "score"
