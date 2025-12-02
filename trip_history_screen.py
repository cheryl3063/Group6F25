import json
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from datetime import datetime, timedelta


class TripHistoryScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        # TITLE
        root.add_widget(Label(text="📚 Trip History", font_size=22, bold=True))

        # Filter row (Today / Week / All)
        filter_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.filter_value = "all"

        btn_today = Button(text="Today")
        btn_today.bind(on_press=lambda *_: self.set_filter("today"))

        btn_week = Button(text="Week")
        btn_week.bind(on_press=lambda *_: self.set_filter("week"))

        btn_all = Button(text="All Time")
        btn_all.bind(on_press=lambda *_: self.set_filter("all"))

        filter_row.add_widget(btn_today)
        filter_row.add_widget(btn_week)
        filter_row.add_widget(btn_all)
        root.add_widget(filter_row)

        # Scrollable trip list
        scroll = ScrollView(do_scroll_y=True)
        self.history_box = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
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

    def set_filter(self, val):
        self.filter_value = val
        self.load_history()

    def on_pre_enter(self):
        self.load_history()

    def passes_filter(self, trip):
        ts = datetime.strptime(trip["timestamp"], "%Y-%m-%d %H:%M:%S")
        now = datetime.now()

        if self.filter_value == "today":
            return ts.date() == now.date()
        if self.filter_value == "week":
            return ts >= now - timedelta(days=7)
        return True

    def load_history(self):
        path = "history.json"
        self.history_box.clear_widgets()

        if not os.path.exists(path):
            self.history_box.add_widget(Label(text="No trips yet."))
            return

        with open(path, "r") as f:
            history = json.load(f)

        # SORT NEWEST → OLDEST
        history.sort(key=lambda t: t["timestamp"], reverse=True)

        # Apply filter
        trips = [t for t in history if self.passes_filter(t)]

        if not trips:
            self.history_box.add_widget(Label(text="No trips match your filter."))
            return

        for trip in trips:

            btn = Button(
                text=(
                    f"[b]{trip['timestamp']}[/b]\n"
                    f"Distance: {trip['total_distance_km']} km | "
                    f"Score: {trip['safety_score']}"
                ),
                markup=True,
                size_hint_y=None,
                height=dp(90),
                halign="left",
                valign="middle",
            )

            btn.bind(on_press=lambda _, t=trip: self.open_summary(t))
            self.history_box.add_widget(btn)

    def open_summary(self, trip):
        screen = self.manager.get_screen("trip_summary")
        screen.set_summary(trip)
        self.manager.current = "trip_summary"
