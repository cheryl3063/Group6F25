import random
import time
from datetime import datetime
from threading import Thread


class SensorListener:
    def __init__(self):
        self.is_active = False
        self.thread = None

        # This stores the most recent reading
        self.latest_data = None

    # ----------------------------------------------------------------------
    # Start sensor stream
    # ----------------------------------------------------------------------
    def start_listeners(self):
        if self.is_active:
            return

        print("SensorListener → STARTED")
        self.is_active = True

        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    # ----------------------------------------------------------------------
    # Stop sensor stream
    # ----------------------------------------------------------------------
    def stop_listeners(self):
        print("SensorListener → STOPPED")
        self.is_active = False

    # ----------------------------------------------------------------------
    # Internal loop
    # ----------------------------------------------------------------------
    def _run(self):
        while self.is_active:
            # Simulated accelerometer
            ax, ay, az = [round(random.uniform(-9.8, 9.8), 2) for _ in range(3)]

            # Simulated gyroscope
            gx, gy, gz = [round(random.uniform(-3.14, 3.14), 2) for _ in range(3)]

            # Simulated GPS
            latitude = round(43.45 + random.uniform(-0.001, 0.001), 6)
            longitude = round(-80.49 + random.uniform(-0.001, 0.001), 6)

            # Store latest reading (UI pulls this)
            self.latest_data = {
                "accel": (ax, ay, az),
                "gyro": (gx, gy, gz),
                "gps": (latitude, longitude),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

            # OPTIONAL: print to console
            print(f"[{self.latest_data['timestamp']}] "
                  f"Accel={self.latest_data['accel']}  "
                  f"Gyro={self.latest_data['gyro']}  "
                  f"GPS=({latitude}, {longitude})")

            time.sleep(1)
