import random
import io
import matplotlib.pyplot as plt
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup

Window.clearcolor = (0, 0, 0, 1)


class AnalyticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.running = False
        self.update_event = None

        self.layout = BoxLayout(orientation="vertical", spacing=15, padding=25)
        self.title = Label(
            text="📊 Live Driver Analytics",
            font_size=22,
            bold=True,
            color=(1, 1, 1, 1),
            font_name="EmojiFont"
        )
        self.layout.add_widget(self.title)

        self.avg_speed_label = Label(
            text="Average Speed: -- km/h",
            font_size=16,
            color=(1, 1, 1, 1),
            font_name="EmojiFont"
        )
        self.distance_label = Label(
            text="Distance Travelled: -- km",
            font_size=16,
            color=(1, 1, 1, 1),
            font_name="EmojiFont"
        )
        self.score_label = Label(
            text="Driver Score: --/100",
            font_size=16,
            color=(1, 1, 1, 1),
            font_name="EmojiFont"
        )

        self.layout.add_widget(self.avg_speed_label)
        self.layout.add_widget(self.distance_label)
        self.layout.add_widget(self.score_label)

        # Chart section (expand height)
        self.chart = Image(size_hint=(1, 0.55))
        self.layout.add_widget(self.chart)

        # Buttons
        self.run_button = Button(
            text="▶️ Start Live Simulation",
            font_size=16,
            background_color=(0.0, 0.3, 0.6, 1),
            font_name="EmojiFont",
            on_press=self.start_simulation
        )
        self.stop_button = Button(
            text="🛑 Stop Simulation",
            font_size=16,
            background_color=(0.3, 0, 0, 1),
            font_name="EmojiFont",
            on_press=self.stop_simulation
        )
        self.back_button = Button(
            text="⬅️ Back to Dashboard",
            font_size=16,
            background_color=(0.15, 0.15, 0.15, 1),
            font_name="EmojiFont",
            on_press=self.go_back
        )

        self.layout.add_widget(self.run_button)
        self.layout.add_widget(self.stop_button)
        self.layout.add_widget(self.back_button)
        self.add_widget(self.layout)

        # Auto resize event for chart scaling
        Window.bind(on_resize=self.refresh_chart_size)

    # ---------------- Simulation Logic ----------------
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
        self.manager.current = "dashboard"

    # ---------------- Chart and Analytics ----------------
    def update_data(self, dt):
        speeds = [random.randint(60, 130) for _ in range(12)]
        avg_speed = round(sum(speeds) / len(speeds), 1)
        distance = round(random.uniform(1, 25), 1)
        overspeed = len([s for s in speeds if s > 120])
        score = max(100 - overspeed * 5 - (avg_speed - 80) * 0.4, 0)

        self.avg_speed_label.text = f"Average Speed: {avg_speed} km/h"
        self.distance_label.text = f"Distance Travelled: {distance} km"
        self.score_label.text = f"Driver Score: {score:.1f}/100"

        # Generate in-memory chart
        buf = io.BytesIO()
        plt.figure(figsize=(9, 5), dpi=150)
        plt.plot(speeds, marker='o', color='limegreen', linewidth=2)
        plt.title(f"Speed vs Time ⏱️ | Score: {score:.1f}", fontsize=12, pad=10)
        plt.xlabel("Time Interval", fontsize=10)
        plt.ylabel("Speed (km/h)", fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(buf, format='png')
        plt.close()

        buf.seek(0)
        texture = Texture.create(size=(900, 500))
        texture.blit_buffer(buf.read(), colorfmt='luminance')
        self.chart.texture = texture

    # Auto refresh size if window changes
    def refresh_chart_size(self, *args):
        if self.running:
            self.update_data(0)

    def show_summary_popup(self):
        popup = Popup(
            title="Trip Completed ✅",
            content=Label(
                text="🚗 Trip Summary\n\nAverage Speed: 85.7 km/h\nDistance: 21.7 km\nDriver Score: 92.7/100\n\nSession Duration: ~30s ⏱️",
                font_name="EmojiFont",
                color=(1, 1, 1, 1)
            ),
            size_hint=(0.75, 0.55)
        )
        popup.open()
