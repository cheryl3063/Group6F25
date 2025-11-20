# score_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp


class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        self.title = Label(
            text="⭐ Driver Score",
            font_size=26,
            bold=True,
            halign="center",
            valign="middle"
        )
        root.add_widget(self.title)

        # --- Score Details ---
        self.score_label = Label(text="Score: --", font_size=22)
        self.avg_speed_label = Label(text="Avg Speed: -- km/h", font_size=18)
        self.distance_label = Label(text="Distance: -- km", font_size=18)
        self.brake_label = Label(text="Brake Events: --", font_size=18)
        self.accel_label = Label(text="Harsh Accel: --", font_size=18)

        root.add_widget(self.score_label)
        root.add_widget(self.avg_speed_label)
        root.add_widget(self.distance_label)
        root.add_widget(self.brake_label)
        root.add_widget(self.accel_label)

        # --- Back Button ---
        back_btn = Button(
            text="⬅ Back",
            size_hint_y=None,
            height=dp(45)
        )
        back_btn.bind(on_press=lambda *_: setattr(self.manager, "current", "trip_summary"))

        root.add_widget(back_btn)

        self.add_widget(root)

    # Called from TripSummaryScreen
    def update_score(self, data):
        self.score_label.text = f"Score: {data['score']}"
        self.avg_speed_label.text = f"Avg Speed: {data['avg_speed']} km/h"
        self.distance_label.text = f"Distance: {data['distance_km']} km"
        self.brake_label.text = f"Brake Events: {data['brake_events']}"
        self.accel_label.text = f"Harsh Accel: {data['harsh_accel']}"
