# sensors_listeners.py
import random
import time
from datetime import datetime
from threshold_config import THRESHOLDS


class SensorListener:
    def __init__(self):
        self.is_active = False
        self.brake_events = 0
        self.harsh_accel_events = 0
        self.speeding_events = 0
        self.prev_accel_z = None

    def start_listeners(self, buffer=None):
        """Start collecting simulated sensor data"""
        self.is_active = True
        self.brake_events = 0
        self.harsh_accel_events = 0
        self.speeding_events = 0
        self.prev_accel_z = None

        print("\n=== Sensors Initialized ===\n")

        for i in range(10):
            if not self.is_active:
                break

            # --- Simulate accelerometer (m/s²)
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]

            # --- Simulate speed (km/h)
            speed_kmh = round(random.uniform(0, 140), 1)

            # --- Simulate GPS (lat/long)
            latitude = round(43.45 + random.uniform(-0.001, 0.001), 6)
            longitude = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            timestamp = datetime.now().strftime("%H:%M:%S")

            # Detect speeding
            if speed_kmh > THRESHOLDS["SPEED_LIMIT_KMH"]:
                self.speeding_events += 1
                print(f"⚠ SPEEDING DETECTED — {speed_kmh} km/h")

            # Detect braking + acceleration using change in Z acceleration
            if self.prev_accel_z is not None:
                diff = az - self.prev_accel_z

                if diff < -THRESHOLDS["BRAKE_SENSITIVITY"]:
                    self.brake_events += 1
                    print("⚠ HARSH BRAKING DETECTED")

                elif diff > THRESHOLDS["ACCEL_SENSITIVITY"]:
                    self.harsh_accel_events += 1
                    print("⚠ HARSH ACCELERATION DETECTED")

            self.prev_accel_z = az

            # Push to buffer if provided
            if buffer:
                buffer.add_sample({
                    "timestamp": timestamp,
                    "accel": {"x": ax, "y": ay, "z": az},
                    "speed": speed_kmh,
                    "gps": {"lat": latitude, "lon": longitude},
                    "events": {
                        "brake_events": self.brake_events,
                        "harsh_accel_events": self.harsh_accel_events,
                        "speeding_events": self.speeding_events
                    }
                })

            print(f"[{timestamp}] Speed={speed_kmh} | AccelZ={az} | GPS=({latitude}, {longitude})")
            time.sleep(1)

        print("\n=== Sensor Session Complete ===\n")

    def stop_listeners(self):
        """Stop collecting sensor data"""
        self.is_active = False
        print("\n=== Sensors Stopped ===\n")
