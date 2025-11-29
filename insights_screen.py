# insights_screen.py

from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Rotate
from kivy.graphics.context_instructions import PushMatrix, PopMatrix
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen

from weekly_trend_widget import WeeklyTrendWidget
from mock_backend import load_latest_trip


class LoadingSpinner(Image):
    """
    Small rotating loading spinner using spinner.png
    (spinner.png must sit in the same folder as this .py file)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "spinner.png"
        self.size_hint = (None, None)
        self.size = (dp(24), dp(24))

        self.angle = 0
        self.rot = Rotate()
        self.canvas.before.add(PushMatrix())
        self.canvas.before.add(self.rot)
        self.canvas.after.add(PopMatrix())

        Clock.schedule_interval(self._rotate, 1 / 60.0)

    def _rotate(self, dt):
        self.angle = (self.angle + 180 * dt) % 360
        self.rot.angle = self.angle
        self.rot.origin = (self.center_x, self.center_y)


class InsightsScreen(Screen):
    """
    Shows:
      • Trip status
      • Last trip summary
      • Weekly trend
    With loading + empty states.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.clearcolor = (0, 0, 0, 1)

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(24)
        )

        title = Label(
            text="📈 Insights & Trends",
            font_size=30,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(48)
        )
        root.add_widget(title)

        # CARD 1 — Trip Status
        self.status_card = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120)
        )

        # Optional background card style could be added here
        status_title = Label(
            text="🚘 Trip Status",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.status_card.add_widget(status_title)

        self.status_body = BoxLayout(orientation="horizontal", spacing=dp(8))
        self.status_card.add_widget(self.status_body)
        root.add_widget(self.status_card)

        # CARD 2 — Last Trip Summary
        self.summary_card = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(200)
        )

        summary_title = Label(
            text="📄 Last Trip Summary",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1)
        )
        self.summary_card.add_widget(summary_title)

        self.summary_body = BoxLayout(orientation="vertical", spacing=dp(4))
        self.summary_card.add_widget(self.summary_body)
        root.add_widget(self.summary_card)

        # CARD 3 — Weekly Trend
        trend_card = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(260)
        )

        trend_title = Label(
            text="📊 Weekly Driving Trend",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1)
        )
        trend_card.add_widget(trend_title)

        self.trend_widget = WeeklyTrendWidget()
        trend_card.add_widget(self.trend_widget)

        root.add_widget(trend_card)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self._show_status_loading()
        self._show_summary_loading()
        Clock.schedule_once(self._refresh_data, 0.15)

    # LOADING STATES
    def _show_status_loading(self):
        self.status_body.clear_widgets()
        row = BoxLayout(orientation="horizontal", spacing=dp(8))
        row.add_widget(LoadingSpinner())
        row.add_widget(Label(
            text="Checking trip status…",
            font_size=18,
            color=(0.8, 0.8, 0.8, 1)
        ))
        self.status_body.add_widget(row)

    def _show_summary_loading(self):
        self.summary_body.clear_widgets()
        row = BoxLayout(orientation="horizontal", spacing=dp(8))
        row.add_widget(LoadingSpinner())
        row.add_widget(Label(
            text="Loading last trip…",
            font_size=18,
            color=(0.8, 0.8, 0.8, 1)
        ))
        self.summary_body.add_widget(row)

    # REFRESH CONTENT
    def _refresh_data(self, *args):
        # Trip Status based on TripRecordingScreen.running
        try:
            trip_screen = self.manager.get_screen("trip_recording")
            running = getattr(trip_screen, "running", False)
        except Exception:
            running = False

        self.status_body.clear_widgets()
        if running:
            txt = Label(
                text="🟢 Trip Recording Active",
                font_size=20,
                color=(0.2, 1, 0.2, 1)
            )
        else:
            txt = Label(
                text="🔴 No active trip",
                font_size=20,
                color=(1, 0.4, 0.4, 1)
            )
        self.status_body.add_widget(txt)

        # Last Trip Summary
        self.summary_body.clear_widgets()
        latest = load_latest_trip()

        if not latest:
            self.summary_body.add_widget(Label(
                text="No trips yet.\nStart a trip to see your summary here.",
                font_size=18,
                halign="center",
                valign="middle",
                color=(0.8, 0.8, 0.8, 1)
            ))
        else:
            lines = [
                f"⭐ Safety Score: {latest['safety_score']}",
                f"🚗 Distance: {latest['total_distance_km']} km",
                f"⏱ Avg Speed: {latest['avg_speed_kmh']} km/h",
                f"⚠ Brake Events: {latest['brake_events']}",
                f"⚡ Harsh Accel: {latest['harsh_accel']}",
            ]
            for line in lines:
                self.summary_body.add_widget(Label(
                    text=line,
                    font_size=18,
                    halign="left",
                    color=(0.9, 0.9, 0.9, 1)
                ))

        if hasattr(self, "trend_widget"):
            self.trend_widget.refresh_data()
