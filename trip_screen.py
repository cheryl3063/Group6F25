from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
import random, time, json, os
from threading import Thread


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

        controls.add_widget(self.start_btn)
        controls.add_widget(self.stop_btn)
        self.layout.add_widget(controls)

        self.add_widget(self.layout)

        # Tracking telemetry state
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

    def load_saved_trip(self):
        if os.path.exists("autosave.json"):
            with open("autosave.json", "r") as f:
                return json.load(f)
        return None
