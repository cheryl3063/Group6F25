# analytics_screen.py

import json
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.metrics import dp


class AnalyticsScreen(Screen):
    """
    Shows analytics based on the MOST RECENT saved trip.
    Reads from trip_history.json (new format) or history.json (older format).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # Title
        title = Label(text="📈 Live Driver Analytics", font_size=22, bold=True)
        root.add_widget(title)

        # Metrics labels
        self.avg_speed_label = Label(text="Average Speed: -- km/h", font_size=18)
        self.distance_label = Label(text="Distance Travelled: -- km", font_size=18)
        self.score_label = Label(text="Driver Score: --/100", font_size=18)

        root.add_widget(self.avg_speed_label)
        root.add_widget(self.distance_label)
        root.add_widget(self.score_label)

        # Log / info box
        self.log_box = TextInput(
            text="Press 'Start Live Simulation' after recording at least one trip.",
            readonly=True,
            size_hint_y=None,
            height=dp(120),
        )
        root.add_widget(self.log_box)

        # Buttons row 1: start / stop
        btn_row1 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        btn_start = Button(text="▶ Load Latest Trip Analytics")
        btn_start.bind(on_press=self.start_simulation)
        btn_row1.add_widget(btn_start)

        btn_stop = Button(text="⏹ Clear")
        btn_stop.bind(on_press=self.stop_simulation)
        btn_row1.add_widget(btn_stop)

        root.add_widget(btn_row1)

        # Buttons row 2: back
        btn_row2 = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))

        btn_back = Button(text="⬅ Back")
        btn_back.bind(on_press=self.go_back)
        btn_row2.add_widget(btn_back)

        root.add_widget(btn_row2)

        self.add_widget(root)

        self.sim_running = False

    # --------------------------------------------------
    # Load REAL metrics from history.json / trip_history.json
    # --------------------------------------------------
    def start_simulation(self, *_):
        self.sim_running = True

        # 1) Find which history file exists
        history_path = None
        for candidate in ("trip_history.json", "history.json"):
            if os.path.exists(candidate):
                history_path = candidate
                break

        if not history_path:
            self.avg_speed_label.text = "Average Speed: -- km/h"
            self.distance_label.text = "Distance Travelled: -- km"
            self.score_label.text = "Driver Score: --/100"
            self.log_box.text = (
                "No history file found.\n"
                "Record a trip first, then open Analytics again."
            )
            return

        # 2) Load the trips
        try:
            with open(history_path, "r") as f:
                raw_data = json.load(f)
        except Exception as e:
            self.log_box.text = f"Error reading {history_path}: {e}"
            return

        if not raw_data:
            self.avg_speed_label.text = "Average Speed: -- km/h"
            self.distance_label.text = "Distance Travelled: -- km"
            self.score_label.text = "Driver Score: --/100"
            self.log_box.text = f"{history_path} exists but contains no trips yet."
            return

        # 3) Normalize to a list of summary dicts
        trips = []
        for item in raw_data:
            if isinstance(item, dict) and "summary" in item:
                # format: {"timestamp": "...", "summary": {...}}
                trips.append(item["summary"])
            else:
                # format: {...summary fields directly...}
                trips.append(item)

        if not trips:
            self.log_box.text = "No valid trip summaries found in history."
            return

        # 4) Use the most recent trip
        last_summary = trips[-1]

        total_distance = last_summary.get("total_distance_km", 0)
        avg_speed = last_summary.get("avg_speed_kmh", 0)
        score = last_summary.get("safety_score", 0)

        # 5) Update labels with REAL values
        self.avg_speed_label.text = f"Average Speed: {avg_speed} km/h"
        self.distance_label.text = f"Distance Travelled: {total_distance} km"
        self.score_label.text = f"Driver Score: {score}/100"

        self.log_box.text = (
            f"Loaded latest trip from {history_path}.\n\n"
            f"- Distance: {total_distance} km\n"
            f"- Avg speed: {avg_speed} km/h\n"
            f"- Safety score: {score}/100\n"
        )

    def stop_simulation(self, *_):
        """Just clears the info; no background thread here."""
        self.sim_running = False
        self.avg_speed_label.text = "Average Speed: -- km/h"
        self.distance_label.text = "Distance Travelled: -- km"
        self.score_label.text = "Driver Score: --/100"
        self.log_box.text = "Analytics cleared. Press 'Load Latest Trip Analytics' again to reload."

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------
    def go_back(self, *_):
        """
        If this app has a 'dashboard' screen (login_ui_kivy.py flow),
        go back there. Otherwise fall back to 'trip'.
        """
        if not self.manager:
            return

        names = {s.name for s in self.manager.screens}

        if "dashboard" in names:
            self.manager.transition.direction = "right"
            self.manager.current = "dashboard"
        elif "trip" in names:
            self.manager.transition.direction = "right"
            self.manager.current = "trip"
