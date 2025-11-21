# score_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp


class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(20)
        )

        # ----- Title -----
        self.title = Label(
            text="⭐ Driver Score",
            font_size=32,
            bold=True,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1)     # High contrast on dark backgrounds
        )
        root.add_widget(self.title)

        # ----- Score -----
        self.score_label = Label(
            text="Score: --",
            font_size=56,
            bold=True,
            markup=True,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        root.add_widget(self.score_label)

        # ----- Detail Metrics -----
        self.avg_speed_label = Label(
            text="Avg Speed: -- km/h",
            font_size=20,
            color=(0.9, 0.9, 0.9, 1),
            halign="left"
        )
        self.distance_label = Label(
            text="Distance: -- km",
            font_size=20,
            color=(0.9, 0.9, 0.9, 1),
            halign="left"
        )

        # Color-coded ones
        self.brake_label = Label(
            text="Brake Events: --",
            font_size=20,
            markup=True,
            halign="left"
        )
        self.accel_label = Label(
            text="Harsh Accel: --",
            font_size=20,
            markup=True,
            halign="left"
        )

        root.add_widget(self.avg_speed_label)
        root.add_widget(self.distance_label)
        root.add_widget(self.brake_label)
        root.add_widget(self.accel_label)

        # ----- Back Button (Bigger + Accessible) -----
        back_btn = Button(
            text="⬅ Back",
            size_hint_y=None,
            height=dp(55),
            font_size=20,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "trip_summary"))
        root.add_widget(back_btn)

        self.add_widget(root)

    # ------------------------------------------------------------------
    # UPDATE SCORE — called from TripSummaryScreen.go_to_score()
    # ------------------------------------------------------------------
    def update_score(self, data):
        score = data["score"]
        avg_speed = data["avg_speed"]
        distance_km = data["distance_km"]
        brake_events = data["brake_events"]
        harsh_accel = data["harsh_accel"]

        # Score text with color grading
        if score >= 80:
            sc_color = "3CB043"  # Friendlier green: colorblind-safe
        elif score >= 60:
            sc_color = "F7C325"  # Deeper yellow
        else:
            sc_color = "D32F2F"  # Accessible red

        self.score_label.text = f"[color=#{sc_color}]{score}[/color]"

        # Basic text
        self.avg_speed_label.text = f"Avg Speed: {avg_speed} km/h"
        self.distance_label.text = f"Distance: {distance_km} km"

        # Brake color coding
        if brake_events == 0:
            br_color = "3CB043"
        elif brake_events <= 2:
            br_color = "F7C325"
        else:
            br_color = "D32F2F"

        self.brake_label.text = f"[color=#{br_color}]Braking Events: {brake_events}[/color]"

        # Harsh accel color coding
        if harsh_accel == 0:
            ha_color = "3CB043"
        elif harsh_accel <= 2:
            ha_color = "F7C325"
        else:
            ha_color = "D32F2F"

        self.accel_label.text = f"[color=#{ha_color}]Harsh Accel: {harsh_accel}[/color]"
