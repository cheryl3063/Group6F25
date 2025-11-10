# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.core.text import LabelBase

# Register emoji font
LabelBase.register(name="EmojiFont", fn_regular="C:\\Windows\\Fonts\\seguiemj.ttf")

class TripRecordingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=25, spacing=15)

        # Title
        self.title = Label(text="📡 Live Telemetry Dashboard", font_size=26, bold=True, font_name="EmojiFont")
        self.layout.add_widget(self.title)

        # Sensor labels
        self.accel_label = Label(text="🪶 Accelerometer → Waiting for data...", font_size=18, font_name="EmojiFont")
        self.gyro_label = Label(text="⚙️ Gyroscope → Waiting for data...", font_size=18, font_name="EmojiFont")
        self.gps_label = Label(text="🛰 GPS → Waiting for data...", font_size=18, font_name="EmojiFont")

        # Add all labels to layout
        self.layout.add_widget(self.accel_label)
        self.layout.add_widget(self.gyro_label)
        self.layout.add_widget(self.gps_label)

        self.add_widget(self.layout)
        self.running = False

    def on_enter(self):
        """Start telemetry updates when screen opens."""
        self.running = True
        Thread(target=self.update_telemetry, daemon=True).start()

    def on_leave(self):
        """Stop updating when leaving."""
        self.running = False

    def update_telemetry(self):
        """Simulate continuous sensor updates."""
        while self.running:
            # Randomized sensor data
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]
            lat = round(43.45 + random.uniform(-0.001, 0.001), 6)
            lon = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            # Update UI thread-safe
            Clock.schedule_once(lambda dt: self.refresh_labels(ax, ay, az, gx, gy, gz, lat, lon))
            time.sleep(1)

    def refresh_labels(self, ax, ay, az, gx, gy, gz, lat, lon):
        """Update labels with new values."""
        self.accel_label.text = f"🪶 Accelerometer → X={ax}, Y={ay}, Z={az}"
        self.gyro_label.text = f"⚙️ Gyroscope → X={gx}, Y={gy}, Z={gz}"
        self.gps_label.text = f"🛰 GPS → Lat={lat}, Lon={lon}"
