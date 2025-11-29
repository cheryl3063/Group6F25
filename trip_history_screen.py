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
        btn_back.bind(on_press=self._go_back)
        btn_row.add_widget(btn_back)

        btn_refresh = Button(text="↻ Refresh")
        btn_refresh.bind(on_press=lambda *_: self.load_history())
        btn_row.add_widget(btn_refresh)

        root.add_widget(btn_row)
        self.add_widget(root)

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------
    def _go_back(self, *_):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "analytics"

    # --------------------------------------------------
    # Auto-load when entering screen
    # --------------------------------------------------
    def on_pre_enter(self):
        self.load_history()

    # --------------------------------------------------
    # Load trip history from JSON file
    # --------------------------------------------------
    def load_history(self):
        """
        Loads and displays trips from local trip_history.json.

        Expected structure:
        [
            {
                "timestamp": "...",
                "summary": {
                    "total_distance_km": ...,
                    "avg_speed_kmh": ...,
                    "brake_events": ...,
                    "harsh_accel": ...,
                    "safety_score": ...
                }
            },
            ...
        ]
        """
        history_path = "trip_history.json"  # <--- match DataBuffer.trips_file

        # Clear old trip cards
        self.history_box.clear_widgets()

        if not os.path.exists(history_path):
            self.history_box.add_widget(Label(text="No trips saved yet."))
            return

        try:
            with open(history_path, "r") as f:
                raw = f.read().strip()
                if not raw:
                    history = []
                else:
                    history = json.loads(raw)
        except Exception as e:
            print(f"[TripHistoryScreen] Error reading {history_path}: {e}")
            self.history_box.add_widget(Label(text="Could not load trip history."))
            return

        if not history:
            self.history_box.add_widget(Label(text="No trips saved yet."))
            return

        # Newest first (optional)
        history = list(history)[::-1]

        for i, trip_record in enumerate(history, start=1):
            summary = trip_record.get("summary", {}) or {}
            timestamp = trip_record.get("timestamp", "Unknown time")

            dist = summary.get("total_distance_km", 0)
            avg = summary.get("avg_speed_kmh", 0)
            brakes = summary.get("brake_events", 0)
            harsh = summary.get("harsh_accel", 0)
            score = summary.get("safety_score", 0)

            # Use a Button so the whole card is clickable
            card = Button(
                text=(
                    f"Trip #{i}  ({timestamp})\n"
                    f"• Distance: {dist} km\n"
                    f"• Avg Speed: {avg} km/h\n"
                    f"• Brakes: {brakes}\n"
                    f"• Harsh Accel: {harsh}\n"
                    f"⭐ Score: {score}"
                ),
                size_hint_y=None,
                height=dp(140),
                halign="left",
                valign="middle"
            )
            # Make text wrap nicely
            card.bind(
                size=lambda btn, *_: setattr(btn, "text_size", btn.size)
            )

            # When pressed → open this trip in TripSummaryScreen
            card.bind(on_press=lambda _btn, s=summary: self.open_summary(s))

            self.history_box.add_widget(card)

    # --------------------------------------------------
    # Open selected trip in TripSummaryScreen
    # --------------------------------------------------
    def open_summary(self, summary: dict):
        """
        Called when a trip card is clicked.
        Sends the summary dict to the TripSummaryScreen.
        """
        if not self.manager:
            return

        try:
            summary_screen = self.manager.get_screen("summary")
        except Exception as e:
            print(f"[TripHistoryScreen] Could not get 'summary' screen: {e}")
            return

        summary_screen.set_summary(summary)
        self.manager.transition.direction = "left"
        self.manager.current = "summary"
