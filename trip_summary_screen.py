# trip_summary_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

from trip_summary_utils import compute_summary
from mock_backend import save_latest_trip, load_latest_trip


class TripSummaryScreen(Screen):

    # -----------------------------
    # Constructor – Build the UI
    # -----------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.samples = []

        # Center container
        root = BoxLayout(
            orientation="vertical",
            padding=dp(40),
            spacing=dp(25),
            size_hint=(0.9, 0.8),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Background card
        with root.canvas.before:
            Color(0.15, 0.15, 0.15, 0.9)
            self.bg_rect = RoundedRectangle(radius=[25])

        def update_bg(*_):
            self.bg_rect.pos = root.pos
            self.bg_rect.size = root.size

        root.bind(pos=update_bg, size=update_bg)

        # Title
        self.title = Label(
            text="📄 Trip Summary",
            font_size=32,
            bold=True,
            halign="center",
            color=(1, 1, 1, 1)
        )
        root.add_widget(self.title)

        # Summary label
        self.metrics = Label(
            text="No data yet.",
            font_size=22,
            halign="center",
            valign="middle",
            color=(0.9, 0.9, 0.9, 1)
        )
        self.metrics.bind(size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size))
        root.add_widget(self.metrics)

        # --- Button Row ---
        btn_row = BoxLayout(spacing=dp(15), size_hint_y=None, height=dp(60))

        # Back
        btn_back = Button(
            text="⬅ Back",
            font_size=20,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
        )
        btn_back.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        btn_row.add_widget(btn_back)

        # Recompute
        btn_refresh = Button(
            text="↻ Recompute",
            font_size=20,
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        btn_refresh.bind(on_press=lambda *_: self._render())
        btn_row.add_widget(btn_refresh)

        # Go to Score
        btn_score = Button(
            text="⭐ View Score",
            font_size=20,
            background_color=(0.8, 0.65, 0.1, 1),
            color=(1, 1, 1, 1)
        )
        btn_score.bind(on_press=self.go_to_score)
        btn_row.add_widget(btn_score)

        root.add_widget(btn_row)
        self.add_widget(root)

    # -----------------------------
    # Auto-refresh whenever opened
    # -----------------------------
    def on_pre_enter(self, *args):
        """Automatically refresh screen from mock backend every time it opens."""
        latest = load_latest_trip()

        if latest:
            self.metrics.text = (
                f"• Distance: {latest['total_distance_km']} km\n"
                f"• Avg Speed: {latest['avg_speed_kmh']} km/h\n"
                f"• Brake Events: {latest['brake_events']}\n"
                f"• Harsh Accel: {latest['harsh_accel']}\n\n"
                f"⭐ Safety Score: {latest['safety_score']}"
            )

            # Update score screen too
            score_screen = self.manager.get_screen("score")
            score_screen.update_score({
                "score": latest["safety_score"],
                "avg_speed": latest["avg_speed_kmh"],
                "distance_km": latest["total_distance_km"],
                "brake_events": latest["brake_events"],
                "harsh_accel": latest["harsh_accel"],
            })

        else:
            self.metrics.text = "No trip found. Record a trip first."

    # -----------------------------
    # Called when TripRecordingScreen stops
    # -----------------------------
    def set_samples(self, samples):
        self.samples = samples or []
        self._render()

    # -----------------------------
    # Compute + update + save
    # -----------------------------
    def _render(self):
        s = compute_summary(self.samples)

        # Save to mock backend
        save_latest_trip(s)

        # Update UI
        self.metrics.text = (
            f"• Distance: {s['total_distance_km']} km\n"
            f"• Avg Speed: {s['avg_speed_kmh']} km/h\n"
            f"• Brake Events: {s['brake_events']}\n"
            f"• Harsh Accel: {s['harsh_accel']}\n\n"
            f"⭐ Safety Score: {s['safety_score']}"
        )

        # Update score screen
        score = self.manager.get_screen("score")
        score.update_score({
            "score": s["safety_score"],
            "avg_speed": s["avg_speed_kmh"],
            "distance_km": s["total_distance_km"],
            "brake_events": s["brake_events"],
            "harsh_accel": s["harsh_accel"]
        })

    # -----------------------------
    # Navigate to Score Screen
    # -----------------------------
    def go_to_score(self, *_):
        s = compute_summary(self.samples)

        score = self.manager.get_screen("score")
        score.update_score({
            "score": s["safety_score"],
            "avg_speed": s["avg_speed_kmh"],
            "distance_km": s["total_distance_km"],
            "brake_events": s["brake_events"],
            "harsh_accel": s["harsh_accel"]
        })

        self.manager.current = "score"
