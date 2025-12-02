from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp

from mock_backend import load_weekly_history


class InsightsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(24), spacing=dp(14))

        title = Label(text="📈 Insights & Trends", font_size=26, bold=True)
        root.add_widget(title)

        self.trend_label = Label(text="Loading trends...", font_size=18)
        root.add_widget(self.trend_label)

        self.add_widget(root)

    def on_pre_enter(self, *args):
        history = load_weekly_history()
        lines = [f"{row['day']}: {row['score']}" for row in history]
        self.trend_label.text = "Weekly Safety Scores:\n\n" + "\n".join(lines)
