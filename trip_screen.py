# -*- coding: utf-8 -*-
import random
import time
from threading import Thread

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

# Register emoji font (Windows path as you had it)
LabelBase.register(name="EmojiFont", fn_regular="C:\\Windows\\Fonts\\seguiemj.ttf")


class TripRecordingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=25, spacing=15)

        # Title
        self.title = Label(text="📡 Live Telemetry Dashboard",
                           font_size=26, bold=True, font_name="EmojiFont")
        self.layout.add_widget(self.title)

        # Sensor labels
        self.accel_label = Label(text="🪶 Accelerometer → Waiting for data...",
                                 font_size=18, font_name="EmojiFont")
        self.gyro_label = Label(text="⚙️ Gyroscope → Waiting for data...",
                                 font_size=18, font_name="EmojiFont")
        self.gps_label = Label(text="🛰 GPS → Waiting for data...",
                               font_size=18, font_name="EmojiFont")

        self.layout.add_widget(self.accel_label)
        self.layout.add_widget(self.gyro_label)
        self.layout.add_widget(self.gps_label)

        # Controls (Start / Stop)
        controls = BoxLayout(size_hint=(1, 0.25), spacing=12)
        self.start_btn = Button(text="▶️ Start Trip", font_size=18,
                                background_color=(0.0, 0.35, 0.7, 1),
                                font_name="EmojiFont",
                                on_press=self._start_clicked)
        self.stop_btn = Button(text="🛑 Stop Trip", font_size=18,
                               background_color=(0.55, 0.0, 0.0, 1),
                               font_name="EmojiFont",
                               on_press=self._stop_clicked)
        controls.add_widget(self.start_btn)
        controls.add_widget(self.stop_btn)
        self.layout.add_widget(controls)

        self.add_widget(self.layout)
        self.running = False
        self._thread = None

    # ------------- Screen hooks -------------
    def on_enter(self, *args):
        # Do not auto-start; let user press Start.
        pass

    def on_leave(self, *args):
        # Ensure background thread stops if user navigates away
        self.running = False

    # ------------- Button handlers -------------
    def _start_clicked(self, *_):
        if self.running:
            return
        # Tell the App to start sensors
        App.get_running_app().start_trip_recording()
        self.running = True
        self.start_btn.text = "🔵 Recording…"
        self._thread = Thread(target=self.update_telemetry, daemon=True)
        self._thread.start()

    def _stop_clicked(self, *_):
        # Stop local updates first
        self.running = False
        self.start_btn.text = "▶️ Start Trip"
        # Tell the App to stop sensors + navigate to analytics
        App.get_running_app().stop_trip_recording()

    # ------------- Telemetry simulation -------------
    def update_telemetry(self):
        """Simulate continuous sensor updates while running."""
        while self.running:
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]
            lat = round(43.45 + random.uniform(-0.001, 0.001), 6)
            lon = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            Clock.schedule_once(
                lambda dt, ax=ax, ay=ay, az=az, gx=gx, gy=gy, gz=gz, lat=lat, lon=lon:
                self.refresh_labels(ax, ay, az, gx, gy, gz, lat, lon)
            )
            time.sleep(1)

    def refresh_labels(self, ax, ay, az, gx, gy, gz, lat, lon):
        """Update labels with new values."""
        self.accel_label.text = f"🪶 Accelerometer → X={ax}, Y={ay}, Z={az}"
        self.gyro_label.text  = f"⚙️ Gyroscope → X={gx}, Y={gy}, Z={gz}"
        self.gps_label.text   = f"🛰 GPS → Lat={lat}, Lon={lon}"
