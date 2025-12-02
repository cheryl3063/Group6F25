# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
import json
import os
import requests

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from trip_manager import TripManager


class TripRecordingScreen(Screen):
    BACKEND_URL = "http://127.0.0.1:5050/save_trip"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.trip_manager = TripManager(user_id="user123")

        self.layout = BoxLayout(orientation="vertical", padding=25, spacing=15)

        self.title = Label(text="📡 Live Telemetry Dashboard", font_size=26, bold=True)
        self.layout.add_widget(self.title)

        self.accel_label = Label(text="🪶 Accelerometer → Waiting for data...", font_size=18)
        self.gyro_label = Label(text="⚙️ Gyroscope → Waiting for data...", font_size=18)
        self.gps_label = Label(text="🛰 GPS → Waiting for data...", font_size=18)

        self.layout.add_widget(self.accel_label)
        self.layout.add_widget(self.gyro_label)
        self.layout.add_widget(self.gps_label)

        controls = BoxLayout(size_hint=(1, 0.25), spacing=12)

        self.start_btn = Button(
            text="▶️ Start Trip",
            font_size=18,
            background_color=(0.0, 0.35, 0.7, 1),
            on_press=self._start_clicked
        )

        self.stop_btn = Button(
            text="🛑 Stop Trip",
            font_size=18,
            background_color=(0.55, 0.0, 0.0, 1),
            on_press=self._stop_clicked
        )

        controls.add_widget(self.start_btn)
        controls.add_widget(self.stop_btn)
        self.layout.add_widget(controls)
        self.add_widget(self.layout)

        self.running = False
        self._thread = None
        self.samples = []

        Clock.schedule_interval(self.auto_save, 5)

    def _start_clicked(self, *_):
        if self.running:
            return
        self.running = True
        self.samples = []
        self.start_btn.text = "🔵 Recording…"

        self._thread = Thread(target=self.update_telemetry, daemon=True)
        self._thread.start()

    def _stop_clicked(self, *_):
        self.running = False
        self.start_btn.text = "▶️ Start Trip"

        if os.path.exists("autosave.json"):
            os.remove("autosave.json")

        formatted_samples = [
            {
                "speed": s["speed"],
                "brake_events": s["brake"],
                "harsh_accel": s["harsh"],
                "distance_km": s["dist"],
            }
            for s in self.samples
        ]

        # Save via TripManager (local file)
        trip_entry = self.trip_manager.end_trip_and_save(formatted_samples)
        summary = trip_entry["summary"]
        summary["timestamp"] = trip_entry["timestamp"]

        print("\n=== SUMMARY (via TripManager) ===")
        print(summary)

        # Send to Flask backend (same format)
        self.send_to_backend(formatted_samples, summary)

        # Navigate to summary screen (Trip Flow C start)
        summary_screen = self.manager.get_screen("trip_summary")
        summary_screen.set_summary(summary)
        self.manager.current = "trip_summary"

    def send_to_backend(self, samples, summary):
        payload = {"samples": samples, "summary": summary}

        try:
            print("📡 Sending trip to backend...")
            r = requests.post(self.BACKEND_URL, json=payload, timeout=5)
            print("BACKEND RESPONSE:", r.text)
        except Exception as e:
            print("❌ Backend error:", e)

    def update_telemetry(self):
        import random
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
                lambda dt, ax=ax, ay=ay, az=az, gx=gx, gy=gy, gz=gz, lat=lat, lon=lon:
                self.refresh_labels(ax, ay, az, gx, gy, gz, lat, lon)
            )

            time.sleep(1)

    def refresh_labels(self, ax, ay, az, gx, gy, gz, lat, lon):
        self.accel_label.text = f"🪶 Accelerometer → X={ax}, Y={ay}, Z={az}"
        self.gyro_label.text = f"⚙️ Gyroscope → X={gx}, Y={gy}, Z={gz}"
        self.gps_label.text = f"🛰 GPS → Lat={lat}, Lon={lon}"

    def auto_save(self, *args):
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

    def load_saved_trip(self):
        if os.path.exists("autosave.json"):
            with open("autosave.json", "r") as f:
                return json.load(f)
        return None
