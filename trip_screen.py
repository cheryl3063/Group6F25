# -*- coding: utf-8 -*-
import random
import time
from threading import Thread
import json
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation   # <-- for banner animation


class TripRecordingScreen(Screen):

    SPEED_THRESHOLD = 85   # ---- TASK 82: SPEED ALERT THRESHOLD ----

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation="vertical", padding=25, spacing=15)

        # ------------------------------------------------------
        # 🔔 TASK 81 — ALERT BANNER (yellow, at TOP)
        # ------------------------------------------------------
        self.alert_label = Label(
            text="",
            font_size=16,
            size_hint_y=None,
            height=40,
            opacity=0,
            color=(0, 0, 0, 1),
            halign="center",
            valign="middle"
        )

        # text wraps nicely
        self.alert_label.bind(
            size=lambda *_: setattr(self.alert_label, "text_size", self.alert_label.size)
        )

        # yellow background behind the label
        with self.alert_label.canvas.before:
            Color(1, 0.9, 0.3, 1)   # yellow
            self.alert_bg = Rectangle()

        self.alert_label.bind(pos=self._update_alert_bg, size=self._update_alert_bg)

        # TOP of layout
        self.layout.add_widget(self.alert_label)
        # ------------------------------------------------------

        # Title
        self.title = Label(
            text="📡 Live Telemetry Dashboard",
            font_size=26,
            bold=True
        )
        self.layout.add_widget(self.title)

        # Labels
        self.accel_label = Label(text="🪶 Accelerometer → Waiting for data...", font_size=18)
        self.gyro_label = Label(text="⚙️ Gyroscope → Waiting for data...", font_size=18)
        self.gps_label = Label(text="🛰 GPS → Waiting for data...", font_size=18)

        self.layout.add_widget(self.accel_label)
        self.layout.add_widget(self.gyro_label)
        self.layout.add_widget(self.gps_label)

        # Controls
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

        self.speed_alert_triggered = False

        Clock.schedule_interval(self.auto_save, 5)

    # ------------------------------------------------------
    # UPDATE YELLOW BANNER BACKGROUND
    # ------------------------------------------------------
    def _update_alert_bg(self, instance, value):
        self.alert_bg.pos = instance.pos
        self.alert_bg.size = instance.size

    # ------------------------------------------------------
    # SHOW ALERT WITH FADE + SLIDE + SOFT “BOUNCE”
    # ------------------------------------------------------
    def show_alert(self, message):
        self.alert_label.text = f"⚠ {message}"

        # Start from current (TOP) position
        base_y = self.alert_label.y

        # Make sure it's visible
        self.alert_label.opacity = 1
        self.alert_label.y = base_y

        # After a delay, animate:
        #  - slide up a bit
        #  - then gently settle slightly lower
        #  - fade out slowly
        def animate_fade(*_):
            up = Animation(y=base_y + 30, d=0.5, t="out_quad")
            # then: settle slightly down + fade out slowly
            settle_and_fade = Animation(
                y=base_y + 20,
                opacity=0,
                d=1.6,
                t="out_quad"
            )
            (up + settle_and_fade).start(self.alert_label)

        # Keep banner visible
        Clock.schedule_once(animate_fade, 3.0)

    # ------------------------------------------------------
    # START TRIP
    # ------------------------------------------------------
    def _start_clicked(self, *_):
        if self.running:
            return

        # reset alert state
        self.alert_label.opacity = 0
        self.speed_alert_triggered = False

        self.running = True
        self.samples = []
        self.start_btn.text = "🔵 Recording…"

        summary_screen = self.manager.get_screen("trip_summary")
        summary_screen.alert_rules.reset()

        self._thread = Thread(target=self.update_telemetry, daemon=True)
        self._thread.start()

    # ------------------------------------------------------
    # STOP TRIP
    # ------------------------------------------------------
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

        self.manager.transition.direction = "left"
        self.manager.current = "trip_summary"

    # ------------------------------------------------------
    # TELEMETRY LOOP (TRIGGERS THE ALERT)
    # ------------------------------------------------------
    def update_telemetry(self):
        while self.running:
            speed = random.randint(30, 110)     # higher range so alert can trigger
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]
            lat = round(43.45 + random.uniform(-0.001, 0.001), 6)
            lon = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            sample = {
                "speed": speed,
                "brake": random.choice([0, 0, 1]),
                "harsh": random.choice([0, 0, 1]),
                "dist": round(random.uniform(0.1, 0.4), 2),
            }
            self.samples.append(sample)

            # ---- TASK 82 — DETECT HIGH SPEED ----
            if speed > self.SPEED_THRESHOLD and not self.speed_alert_triggered:
                self.speed_alert_triggered = True
                Clock.schedule_once(
                    lambda dt, spd=speed: self.show_alert(
                        f"High speed detected ({spd} km/h)!"
                    )
                )

            Clock.schedule_once(
                lambda dt, ax=ax, ay=ay, az=az,
                       gx=gx, gy=gy, gz=gz, lat=lat, lon=lon:
                self.refresh_labels(ax, ay, az, gx, gy, gz, lat, lon),
                0  # forces refresh to run IMMEDIATELY
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
    # AUTO-SAVE
    # ------------------------------------------------------
    def auto_save(self, *args):
        if not self.running:
            return

        with open("autosave.json", "w") as f:
            json.dump({
                "accel": self.accel_label.text,
                "gyro": self.gyro_label.text,
                "gps": self.gps_label.text,
                "samples": self.samples
            }, f)

    def load_saved_trip(self):
        if os.path.exists("autosave.json"):
            with open("autosave.json", "r") as f:
                return json.load(f)
        return None
