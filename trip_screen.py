# trip_screen.py
# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
import json
import os

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen


class TripRecordingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ROOT LAYOUT
        root = BoxLayout(
            orientation="vertical",
            padding=dp(24),
            spacing=dp(20)
        )

        # TITLE
        title = Label(
            text="📡 Live Trip Recording",
            font_size=32,
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(title)

        # TELEMETRY CARD
        card = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(16),
            size_hint=(1, None),
            height=dp(280)
        )

        with card.canvas.before:
            Color(0.15, 0.15, 0.15, 0.90)
            self.card_bg = RoundedRectangle(radius=[22])

        def update_card_bg(*_):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size

        card.bind(pos=update_card_bg, size=update_card_bg)

        # SENSOR LABELS
        self.accel_label = Label(
            text="🪶 Accelerometer: waiting...",
            font_size=20,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        self.accel_label.bind(size=lambda *_: setattr(self.accel_label, "text_size", self.accel_label.size))

        self.gyro_label = Label(
            text="⚙️ Gyroscope: waiting...",
            font_size=20,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        self.gyro_label.bind(size=lambda *_: setattr(self.gyro_label, "text_size", self.gyro_label.size))

        self.gps_label = Label(
            text="🛰 GPS: waiting...",
            font_size=20,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1)
        )
        self.gps_label.bind(size=lambda *_: setattr(self.gps_label, "text_size", self.gps_label.size))

        card.add_widget(self.accel_label)
        card.add_widget(self.gyro_label)
        card.add_widget(self.gps_label)

        root.add_widget(card)

        # BUTTON BAR
        btn_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(16),
            size_hint=(1, None),
            height=dp(60)
        )

        self.start_btn = Button(
            text="▶️ Start Trip",
            font_size=20,
            background_color=(0.0, 0.45, 0.90, 1),
            color=(1, 1, 1, 1)
        )
        self.start_btn.bind(on_press=self._start_clicked)

        self.stop_btn = Button(
            text="🛑 Stop Trip",
            font_size=20,
            background_color=(0.70, 0.10, 0.10, 1),
            color=(1, 1, 1, 1)
        )
        self.stop_btn.bind(on_press=self._stop_clicked)

        btn_row.add_widget(self.start_btn)
        btn_row.add_widget(self.stop_btn)

        root.add_widget(btn_row)

        self.add_widget(root)

        # STATE
        self.running = False
        self._thread = None
        self.samples = []

        Clock.schedule_interval(self.auto_save, 5)

    # BUTTON HANDLERS
    def _start_clicked(self, *_):
        if self.running:
            return
        self.running = True
        self.samples = []
        self.start_btn.text = "🔵 Recording..."

        self._thread = Thread(target=self.update_telemetry, daemon=True)
        self._thread.start()

    def _stop_clicked(self, *_):
        self.running = False
        self.start_btn.text = "▶️ Start Trip"

        if os.path.exists("autosave.json"):
            os.remove("autosave.json")

        summary_samples = []
        for s in self.samples:
            summary_samples.append({
                "speed": s["speed"],
                "brake_events": s["brake"],
                "harsh_accel": s["harsh"],
                "distance_km": s["dist"]
            })

        trip_summary = self.manager.get_screen("trip_summary")
        trip_summary.set_samples(summary_samples)

        self.manager.current = "trip_summary"

    # TELEMETRY LOOP
    def update_telemetry(self):
        while self.running:
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]
            lat = round(43.45 + random.uniform(-0.001, 0.001), 6)
            lon = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            sample = {
                "speed": random.randint(30, 90),
                "brake": random.choice([0, 0, 1]),
                "harsh": random.choice([0, 0, 1]),
                "dist": round(random.uniform(0.1, 0.4), 2),
            }
            self.samples.append(sample)

            Clock.schedule_once(
                lambda dt, ax=ax, ay=ay, az=az,
                gx=gx, gy=gy, gz=gz, lat=lat, lon=lon:
                self.refresh_labels(ax, ay, az, gx, gy, gz, lat, lon)
            )

            time.sleep(1)

    def refresh_labels(self, ax, ay, az, gx, gy, gz, lat, lon):
        self.accel_label.text = f"🪶 Accelerometer → X={ax}, Y={ay}, Z={az}"
        self.gyro_label.text = f"⚙️ Gyroscope → X={gx}, Y={gy}, Z={gz}"
        self.gps_label.text = f"🛰 GPS → Lat={lat}, Lon={lon}"

    # AUTO SAVE
    def auto_save(self, *_):
        if not self.running:
            return

        trip_data = {
            "accel": self.accel_label.text,
            "gyro": self.gyro_label.text,
            "gps": self.gps_label.text,
            "samples": self.samples
        }

        with open("autosave.json", "w") as f:
            json.dump(trip_data, f)

        print("Auto-saved trip data.")
