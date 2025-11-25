# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
import json
import os

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup

from permissions_manager import has_required_permissions


class TripRecordingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", padding=25, spacing=15)

        # Title
        self.title = Label(
            text="📡 Live Telemetry Dashboard",
            font_size=26,
            bold=True
        )
        self.layout.add_widget(self.title)

        # Error label (for permissions / flow issues)
        self.error_label = Label(
            text="",
            font_size=16,
            color=(1, 0, 0, 1),  # red
            halign="center"
        )
        self.error_label.bind(
            size=lambda *_: setattr(self.error_label, "text_size", self.error_label.size)
        )
        self.layout.add_widget(self.error_label)

        # Labels for telemetry
        self.accel_label = Label(text="🪶 Accelerometer → Waiting for data...", font_size=18)
        self.gyro_label = Label(text="⚙️ Gyroscope → Waiting for data...", font_size=18)
        self.gps_label = Label(text="🛰 GPS → Waiting for data...", font_size=18)

        self.layout.add_widget(self.accel_label)
        self.layout.add_widget(self.gyro_label)
        self.layout.add_widget(self.gps_label)

        # Controls (Start / Stop)
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
        # Initially you can't stop a trip that hasn't started
        self.stop_btn.disabled = True

        controls.add_widget(self.start_btn)
        controls.add_widget(self.stop_btn)
        self.layout.add_widget(controls)

        self.add_widget(self.layout)

        # Tracking telemetry state
        self.running = False
        self._thread = None

        # Raw samples for this trip
        # Each element looks like: {"speed": ..., "brake": ..., "harsh": ..., "dist": ...}
        self.samples = []

        # auto-save every 5 seconds
        Clock.schedule_interval(self.auto_save, 5)

    # ------------------------------------------------------
    # START BUTTON
    # ------------------------------------------------------
    def _start_clicked(self, *_):
        """
        Start a new trip if not already recording and permissions are valid.
        """
        # Already running? ignore extra taps → prevents double-start
        if self.running:
            return

        # ✅ Check permissions before starting trip
        if not has_required_permissions():
            # Show error text + popup
            self.error_label.text = "⚠ Permission required: enable Location + Motion to start a trip."
            self.show_permission_error()
            return
        else:
            # Clear any previous error
            self.error_label.text = ""

        # Reset previous trip state
        self.running = True
        self.samples = []

        # Reset UI labels at the beginning of a new trip
        self.accel_label.text = "🪶 Accelerometer → Reading..."
        self.gyro_label.text = "⚙️ Gyroscope → Reading..."
        self.gps_label.text = "🛰 GPS → Reading..."

        # Update button states
        self.start_btn.text = "🔵 Recording…"
        self.start_btn.disabled = True
        self.stop_btn.disabled = False

        # Start background thread for telemetry
        self._thread = Thread(target=self.update_telemetry, daemon=True)
        self._thread.start()

    # ------------------------------------------------------
    # STOP BUTTON → Go to Summary
    # ------------------------------------------------------
    def _stop_clicked(self, *_):
        """
        Stop the trip if currently recording and navigate to summary screen.
        """
        # If not recording, ignore → prevents invalid stop
        if not self.running:
            return

        self.running = False

        # Update buttons back to idle state
        self.start_btn.text = "▶️ Start Trip"
        self.start_btn.disabled = False
        self.stop_btn.disabled = True

        # Clear error (if any)
        self.error_label.text = ""

        # DELETE autosave file if it exists
        if os.path.exists("autosave.json"):
            os.remove("autosave.json")

        # --------------------------------------------------
        # 🔥 TASK 74: Build CLEAN sample list for summary
        # --------------------------------------------------
        summary_samples = []
        for s in self.samples:
            summary_samples.append({
                "speed": s["speed"],
                "brake_events": s["brake"],
                "harsh_accel": s["harsh"],
                "distance_km": s["dist"]
            })

        # Even if no samples, still handle gracefully
        if not summary_samples:
            print("No samples recorded for this trip.")

        # Send data to summary screen (Tonse's part)
        trip_summary = self.manager.get_screen("trip_summary")
        trip_summary.set_samples(summary_samples)

        # Navigate to summary
        self.manager.transition.direction = "left"
        self.manager.current = "trip_summary"

    # ------------------------------------------------------
    # PERMISSION ERROR POPUP
    # ------------------------------------------------------
    def show_permission_error(self):
        """
        Show a popup explaining that location/motion permissions are required.
        """
        box = BoxLayout(orientation="vertical", padding=20, spacing=10)

        msg = Label(
            text="Location and motion permissions are required to start a trip.\n"
                 "Please enable them in settings or permissions.json.",
            halign="center"
        )
        msg.bind(size=lambda *_: setattr(msg, "text_size", msg.size))

        btn_ok = Button(text="OK", size_hint_y=None, height=40)

        box.add_widget(msg)
        box.add_widget(btn_ok)

        popup = Popup(
            title="Permissions Required",
            content=box,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        btn_ok.bind(on_press=popup.dismiss)
        popup.open()

    # ------------------------------------------------------
    # TELEMETRY SIMULATION LOOP
    # ------------------------------------------------------
    def update_telemetry(self):
        """Simulate continuous sensor updates while running."""
        while self.running:
            # Accelerometer
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]

            # Gyroscope
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]

            # GPS
            lat = round(43.45 + random.uniform(-0.001, 0.001), 6)
            lon = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            # Fake additional metrics for summary (raw form)
            sample = {
                "speed": random.randint(30, 90),
                "brake": random.choice([0, 0, 1]),
                "harsh": random.choice([0, 0, 1]),
                "dist": round(random.uniform(0.1, 0.4), 2),
            }
            self.samples.append(sample)

            # Schedule UI update
            Clock.schedule_once(
                lambda dt, ax=ax, ay=ay, az=az,
                gx=gx, gy=gy, gz=gz, lat=lat, lon=lon:
                self.refresh_labels(ax, ay, az, gx, gy, gz, lat, lon)
            )

            time.sleep(1)

    # ------------------------------------------------------
    # UPDATE UI LABELS
    # ------------------------------------------------------
    def refresh_labels(self, ax, ay, az, gx, gy, gz, lat, lon):
        self.accel_label.text = f"🪶 Accelerometer → X={ax}, Y={ay}, Z={az}"
        self.gyro_label.text = f"⚙️ Gyroscope → X={gx}, Y={gy}, Z={gz}"
        self.gps_label.text = f"🛰 GPS → Lat={lat}, Lon={lon}"

    # ------------------------------------------------------
    # AUTO-SAVE FUNCTION
    # ------------------------------------------------------
    def auto_save(self, *args):
        """Automatically save the current telemetry readings to autosave.json."""
        if not self.running:
            return  # Only auto-save when trip is running

        trip_data = {
            "accel": self.accel_label.text,
            "gyro": self.gyro_label.text,
            "gps": self.gps_label.text,
            "samples": self.samples
        }

        with open("autosave.json", "w") as f:
            json.dump(trip_data, f)

        print("Auto-saved trip data.")

    # ------------------------------------------------------
    # LOAD SAVED TRIP (for resume)
    # ------------------------------------------------------
    def load_saved_trip(self):
        """Load previously saved data if available."""
        if os.path.exists("autosave.json"):
            with open("autosave.json", "r") as f:
                return json.load(f)
        return None
