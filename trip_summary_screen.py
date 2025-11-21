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

        # Outer layout
        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16)
        )

        # Title
        self.title = Label(
            text="📄 Trip Summary",
            font_size=26,
            bold=True,
            halign="center"
        )
        root.add_widget(self.title)

        # Metrics label
        self.metrics = Label(
            text="[i]No data yet.[/i]",
            font_size=18,
            halign="left",
            valign="top",
            markup=True
        )
        self.metrics.bind(
            size=lambda *_: setattr(self.metrics, "text_size", self.metrics.size)
        )
        root.add_widget(self.metrics)

        # Buttons row
        btn_row = BoxLayout(
            size_hint_y=None,
            height=dp(52),
            spacing=dp(10)
        )

        # Back button
        self.btn_back = Button(
            text="⬅ Back",
            background_color=(0.2, 0.2, 0.2, 1)
        )
        self.btn_back.bind(
            on_press=lambda *_: setattr(self.manager, "current", "dashboard")
        )
        btn_row.add_widget(self.btn_back)

        # Refresh
        self.btn_refresh = Button(
            text="↻ Refresh",
            background_color=(0.1, 0.4, 0.7, 1),
        )
        self.btn_refresh.bind(on_press=lambda *_: self._render())
        btn_row.add_widget(self.btn_refresh)

        # View score
        self.btn_view_score = Button(
            text="⭐ View Score",
            background_color=(0.85, 0.65, 0.0, 1)
        )
        self.btn_view_score.bind(on_press=lambda *_: self.go_to_score())
        btn_row.add_widget(self.btn_view_score)

        root.add_widget(btn_row)
        self.add_widget(root)

    # ----------------------------------------
    # Receive samples from TripRecordingScreen
    # ----------------------------------------
    def set_samples(self, samples):
        self.samples = samples or []
        self._render()

    # ----------------------------------------
    # Render summary with visual polish
    # ----------------------------------------
    def _render(self):
        s = compute_summary(self.samples)

        # Color-coding thresholds
        def colorize(value, good, warn):
            if value <= good:
                return "4CAF50"  # green
            elif value <= warn:
                return "FFC107"  # yellow
            return "F44336"      # red

        brake_color = colorize(s["brake_events"], 0, 2)
        harsh_color = colorize(s["harsh_accel"], 0, 2)

        # Prettier formatting
        self.metrics.markup = True
        self.metrics.text = (
            f"[b]Distance:[/b] {s['total_distance_km']} km\n"
            f"[b]Avg Speed:[/b] {s['avg_speed_kmh']} km/h\n"
            f"[b][color=#{brake_color}]Brake Events:[/color][/b] {s['brake_events']}\n"
            f"[b][color=#{harsh_color}]Harsh Accel:[/color][/b] {s['harsh_accel']}\n\n"
            f"[size=22]⭐ [b]{s['safety_score']}[/b][/size]"
        )

    # ----------------------------------------
    # Navigate to the score visualization screen
    # ----------------------------------------
    def go_to_score(self, *args):
        summary = compute_summary(self.samples)

        ui_data = {
            "score": summary["safety_score"],
            "avg_speed": summary["avg_speed_kmh"],
            "distance_km": summary["total_distance_km"],
            "brake_events": summary["brake_events"],
            "harsh_accel": summary["harsh_accel"]
        }

        score_screen = self.manager.get_screen("score")
        score_screen.update_score(ui_data)
        self.manager.current = "score"
