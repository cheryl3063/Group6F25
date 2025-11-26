# score_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from mock_backend import load_latest_trip


class ScoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(26),
            spacing=dp(22),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        card = BoxLayout(
            orientation="vertical",
            padding=dp(26),
            spacing=dp(20),
            size_hint=(0.85, 0.75),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Card background
        with card.canvas.before:
            Color(0.15, 0.15, 0.15, 0.9)
            self.card_bg = RoundedRectangle(radius=[25])

        def update_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size

        card.bind(size=update_bg, pos=update_bg)

        # Title
        title = Label(
            text="⭐ Driver Score",
            font_size=32,
            bold=True,
            color=(1, 1, 1, 1)
        )
        card.add_widget(title)

        # Main Score (big + colored)
        self.score_label = Label(
            text="--",
            font_size=70,
            bold=True,
            markup=True,
            color=(1, 1, 1, 1)
        )
        card.add_widget(self.score_label)

        # Detailed labels
        self.avg_speed_label = Label(font_size=22, color=(0.9, 0.9, 0.9, 1))
        self.distance_label = Label(font_size=22, color=(0.9, 0.9, 0.9, 1))
        self.brake_label = Label(font_size=22, markup=True)
        self.accel_label = Label(font_size=22, markup=True)

        card.add_widget(self.avg_speed_label)
        card.add_widget(self.distance_label)
        card.add_widget(self.brake_label)
        card.add_widget(self.accel_label)

        # Back button
        back = Button(
            text="⬅ Back",
            size_hint_y=None,
            height=dp(55),
            font_size=20,
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        back.bind(on_press=lambda *_: setattr(self.manager, "current", "trip_summary"))
        card.add_widget(back)

        root.add_widget(card)
        self.add_widget(root)


    # Auto-refresh score whenever screen opens
    def on_pre_enter(self, *args):
        latest = load_latest_trip()
        if latest:
            self.update_score({
                "score": latest["safety_score"],
                "avg_speed": latest["avg_speed_kmh"],
                "distance_km": latest["total_distance_km"],
                "brake_events": latest["brake_events"],
                "harsh_accel": latest["harsh_accel"]
            })

    # Main update method — called by Trip Summary
    def update_score(self, data):
        score = data["score"]

        # score color logic
        if score >= 80:
            sc = "3CB043"  # green
        elif score >= 60:
            sc = "F7C325"  # yellow
        else:
            sc = "D32F2F"  # red

        self.score_label.text = f"[color=#{sc}]{score}[/color]"

        self.avg_speed_label.text = f"Avg Speed: {data['avg_speed']} km/h"
        self.distance_label.text = f"Distance: {data['distance_km']} km"

        # braking color logic
        b = data["brake_events"]
        bc = "3CB043" if b == 0 else "F7C325" if b <= 2 else "D32F2F"
        self.brake_label.text = f"[color=#{bc}]Braking Events: {b}[/color]"

        # harsh accel color logic
        h = data["harsh_accel"]
        hc = "3CB043" if h == 0 else "F7C325" if h <= 2 else "D32F2F"
        self.accel_label.text = f"[color=#{hc}]Harsh Accel: {h}[/color]"
