# analytics_screen.py
import random
import io
import matplotlib.pyplot as plt

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

Window.clearcolor = (0, 0, 0, 1)

#-----#
self.manager.current = "history"
#---#

class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.running = False
        self.update_event = None

        # ROOT LAYOUT
        root = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(18)
        )

        title = Label(
            text="📊 Live Driver Analytics",
            font_size=30,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(title)

        # METRICS + CHART CARD
        card = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12),
            size_hint=(1, 0.7)
        )

        with card.canvas.before:
            Color(0.15, 0.15, 0.15, 0.9)
            self.card_bg = RoundedRectangle(radius=[20])

        def update_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size

        card.bind(pos=update_bg, size=update_bg)

        # METRICS LABELS
        self.avg_speed_label = Label(
            text="Average Speed: -- km/h",
            font_size=18,
            color=(0.95, 0.95, 0.95, 1)
        )
        self.distance_label = Label(
            text="Distance Travelled: -- km",
            font_size=18,
            color=(0.95, 0.95, 0.95, 1)
        )
        self.score_label = Label(
            text="Driver Score: --/100",
            font_size=18,
            color=(0.95, 0.95, 0.95, 1)
        )

        card.add_widget(self.avg_speed_label)
        card.add_widget(self.distance_label)
        card.add_widget(self.score_label)

        # CHART
        self.chart = Image(size_hint=(1, 1))
        card.add_widget(self.chart)

        root.add_widget(card)

        # BUTTON BAR
        btn_row = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(170)
        )

        self.run_button = Button(
            text="▶️ Start Live Simulation",
            font_size=18,
            background_color=(0.0, 0.35, 0.7, 1),
            size_hint_y=None,
            height=dp(52),
            color=(1, 1, 1, 1)
        )
        self.run_button.bind(on_press=self.start_simulation)

        self.stop_button = Button(
            text="🛑 Stop Simulation",
            font_size=18,
            background_color=(0.6, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(52),
            color=(1, 1, 1, 1)
        )
        self.stop_button.bind(on_press=self.stop_simulation)

        self.back_button = Button(
            text="⬅ Back to Trip",
            font_size=18,
            background_color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(52),
            color=(1, 1, 1, 1)
        )
        self.back_button.bind(on_press=self.go_back)

        btn_row.add_widget(self.run_button)
        btn_row.add_widget(self.stop_button)
        btn_row.add_widget(self.back_button)

        root.add_widget(btn_row)

        self.add_widget(root)

        Window.bind(on_resize=self.refresh_chart_size)

    # SIMULATION LOGIC
    def start_simulation(self, *args):
        if not self.running:
            self.running = True
            self.run_button.text = "🔵 Running..."
            self.update_event = Clock.schedule_interval(self.update_data, 2.5)
            self.update_data(0)

    def stop_simulation(self, *args):
        if self.running and self.update_event:
            Clock.unschedule(self.update_event)
            self.running = False
            self.run_button.text = "▶️ Start Live Simulation"
            self.show_summary_popup()

    def go_back(self, *args):
        if self.update_event:
            Clock.unschedule(self.update_event)
        self.manager.current = "trip_recording"

    # CHART & ANALYTICS UPDATE
    def update_data(self, dt):
        speeds = [random.randint(60, 130) for _ in range(12)]
        avg_speed = round(sum(speeds) / len(speeds), 1)
        distance = round(random.uniform(1, 25), 1)
        overspeed = len([s for s in speeds if s > 120])
        score = max(100 - overspeed * 5 - (avg_speed - 80) * 0.4, 0)

        self.avg_speed_label.text = f"Average Speed: {avg_speed} km/h"
        self.distance_label.text = f"Distance Travelled: {distance} km"
        self.score_label.text = f"Driver Score: {score:.1f}/100"

        buf = io.BytesIO()
        plt.figure(figsize=(9, 4), dpi=140)
        plt.plot(speeds, marker='o', color='limegreen', linewidth=2)
        plt.title(f"Speed vs Time ⏱️ | Score: {score:.1f}", fontsize=11, pad=8)
        plt.xlabel("Time Interval")
        plt.ylabel("Speed (km/h)")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close()

        buf.seek(0)
        data = buf.read()

        # Let Kivy load image bytes via texture
        tex = Texture.create(size=(900, 400))
        try:
            tex.blit_buffer(data, colorfmt='luminance')
        except Exception:
            pass

        self.chart.texture = tex

    def refresh_chart_size(self, *args):
        if self.running:
            self.update_data(0)

    def show_summary_popup(self):
        popup = Popup(
            title="Trip Completed ✅",
            content=Label(
                text=(
                    "🚗 Trip Summary\n\n"
                    "Average Speed: 85.7 km/h\n"
                    "Distance: 21.7 km\n"
                    "Driver Score: 92.7/100\n\n"
                    "Session Duration: ~30s ⏱️"
                ),
                color=(1, 1, 1, 1),
                font_size=16
            ),
            size_hint=(0.75, 0.55)
        )
        popup.open()
