# trip_history_screen.py

import json
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp


class TripHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        self.title = Label(text="📚 Trip History", font_size=22, bold=True)
        root.add_widget(self.title)

        # Scroll container
        scroll = ScrollView(do_scroll_y=True)
        self.history_box = BoxLayout(
            orientation="vertical", spacing=dp(10), size_hint_y=None
        )
        self.history_box.bind(minimum_height=self.history_box.setter("height"))
        scroll.add_widget(self.history_box)
        root.add_widget(scroll)

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        btn_back = Button(text="⬅ Back")
        btn_back.bind(on_press=lambda *_: setattr(self.manager, "current", "analytics"))
        btn_row.add_widget(btn_back)

        btn_refresh = Button(text="↻ Refresh")
        btn_refresh.bind(on_press=lambda *_: self.load_history())
        btn_row.add_widget(btn_refresh)

        root.add_widget(btn_row)
        self.add_widget(root)

    def on_pre_enter(self):
        self.load_history()

    def load_history(self):
        """Loads and displays trips from local history.json"""
        history_path = "history.json"

        # Clear old trip cards
        self.history_box.clear_widgets()

        if not os.path.exists(history_path):
            self.history_box.add_widget(Label(text="No trips saved yet."))
            return

        with open(history_path, "r") as f:
            history = json.load(f)

        if not history:
            self.history_box.add_widget(Label(text="No trips saved yet."))
            return

        for i, trip in enumerate(history, start=1):
            card = Label(
                text=(
                    f"[b]Trip #{i}[/b]\n"
                    f"• Distance: {trip['total_distance_km']} km\n"
                    f"• Avg Speed: {trip['avg_speed_kmh']} km/h\n"
                    f"• Brakes: {trip['brake_events']}\n"
                    f"• Harsh Accel: {trip['harsh_accel']}\n"
                    f"⭐ Score: {trip['safety_score']}"
                ),
                markup=True,
                size_hint_y=None,
                height=dp(140),
            )
            self.history_box.add_widget(card)
