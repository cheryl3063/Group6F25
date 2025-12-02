from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.label import Label

from trip_manager import TripManager


class AnalyticsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tm = TripManager(user_id="user123")

        root = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))

        root.add_widget(Label(text="📊 Analytics", font_size=22, bold=True))

        self.stats_label = Label(text="Loading...", font_size=18)
        root.add_widget(self.stats_label)

        btn_history = Button(text="📚 View Trip History", size_hint_y=None, height=dp(48))
        btn_history.bind(on_press=lambda *_: setattr(self.manager, "current", "history"))
        root.add_widget(btn_history)

        btn_back = Button(text="⬅ Back to Dashboard", size_hint_y=None, height=dp(48))
        btn_back.bind(on_press=lambda *_: setattr(self.manager, "current", "dashboard"))
        root.add_widget(btn_back)

        self.add_widget(root)

    def on_pre_enter(self, *args):
        stats = self.tm.get_stats_for_analytics()

        self.stats_label.text = (
            f"Total Trips: {stats['trips']}\n"
            f"Total Distance: {stats['total_distance']} km\n"
            f"Average Score: {stats['average_score']}"
        )
