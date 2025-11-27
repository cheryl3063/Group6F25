# sensors_listeners.py
import random
import time
from datetime import datetime


class SensorListener:
    def __init__(self):
        self.is_active = False

    def start_listeners(self):
        """Start collecting simulated sensor data"""
        self.is_active = True
        print("\n=== Sensors Initialized ===")
        print("Accelerometer, Gyroscope, and GPS are now active.\n")

        for i in range(10):
            if not self.is_active:
                break

            # Simulate accelerometer (m/s²)
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]

            # Simulate gyroscope (rad/s)
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]

            # Simulate GPS (lat/long)
            latitude = round(43.45 + random.uniform(-0.001, 0.001), 6)
            longitude = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            timestamp = datetime.now().strftime("%H:%M:%S")

            print(f"[{timestamp}] Accelerometer → X={ax}, Y={ay}, Z={az}")
            print(f"[{timestamp}] Gyroscope → X={gx}, Y={gy}, Z={gz}")
            print(f"[{timestamp}] GPS → Lat={latitude}, Lon={longitude}\n")

            time.sleep(1)

    def stop_listeners(self):
        """Stop collecting sensor data"""
        self.is_active = False
        print("\n=== Sensors Stopped ===\n")
