# analytics_screen.py
import io
import random
import matplotlib.pyplot as plt

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.core.image import Image as CoreImage

from trip_manager import TripManager


class AnalyticsScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.tm = TripManager("user123")

        # MAIN LAYOUT
        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20)
        )

        # TITLE
        title = Label(
            text="📊 Analytics",
            font_size=32,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, None),
            height=dp(40),
        )
        root.add_widget(title)

        # STATS LABEL
        self.stats_label = Label(
            text="Loading...",
            font_size=20,
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, None),
            height=dp(80)
        )
        root.add_widget(self.stats_label)

        # CHART IMAGE
        self.chart = Image(
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 0.65)
        )
        root.add_widget(self.chart)

        # REFRESH BUTTON
        btn_refresh = Button(
            text="🔄 Refresh Analytics",
            size_hint=(1, None),
            height=dp(55),
            font_size=18,
            background_color=(0.1, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        btn_refresh.bind(on_press=lambda *_: self.update_ui())
        root.add_widget(btn_refresh)

        self.add_widget(root)

    # Screen load
    def on_pre_enter(self, *args):
        self.update_ui()

    # Update stats + chart
    def update_ui(self):
        stats = self.tm.get_stats_for_analytics()

        # update stats text
        self.stats_label.text = (
            f"Total Trips: {stats['trips']}\n"
            f"Total Distance: {stats['total_distance']} km\n"
            f"Average Score: {stats['average_score']}"
        )

        # generate chart
        self.draw_chart()

    # Draws chart and loads into Kivy
    def draw_chart(self):
        trips = list(range(1, 15))
        scores = [random.randint(60, 95) for _ in trips]
        distances = [round(random.uniform(0.5, 4.0), 1) for _ in trips]

        plt.figure(figsize=(6, 3))
        plt.plot(trips, scores, marker='o', label="Score")
        plt.plot(trips, distances, marker='x', label="Distance")
        plt.title("Trip Performance Trends")
        plt.xlabel("Trip #")
        plt.ylabel("Values")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        self.chart.texture = CoreImage(buf, ext="png").texture
