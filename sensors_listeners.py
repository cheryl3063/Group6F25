# sensors_listeners.py
import random
import time
from datetime import datetime
from threshold_config import THRESHOLDS


class SensorListener:
    def __init__(self):
        self.is_active = False
        self.brake_events = 0          # cumulative count
        self.harsh_accel_events = 0    # cumulative count
        self.speeding_events = 0       # cumulative count
        self.prev_accel_z = None

    def start_listeners(self, buffer=None):
        """
        Start collecting simulated sensor data.

        If a buffer is provided, we now push samples in the SAME format
        that the rest of the app expects, i.e.:

            {
                "speed": <float>,          # km/h
                "brake_events": <int>,     # 0 or 1 per sample
                "harsh_accel": <int>,      # 0 or 1 per sample
                "distance_km": <float>,    # distance covered in this sample
            }

        This satisfies Sprint 5 Task 106: "Standardize sensor output format".
        """
        self.is_active = True
        self.brake_events = 0
        self.harsh_accel_events = 0
        self.speeding_events = 0
        self.prev_accel_z = None

        print("\n=== Sensors Initialized ===\n")

        # Simulate 10 samples (1 per second)
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

            # Per-sample flags (0/1) for this iteration
            brake_flag = 0
            harsh_flag = 0
            speeding_flag = 0

            # -------------- SPEEDING DETECTION --------------
            if speed_kmh > THRESHOLDS["SPEED_LIMIT_KMH"]:
                self.speeding_events += 1
                speeding_flag = 1
                print(f"⚠ SPEEDING DETECTED — {speed_kmh} km/h")

            # -------------- BRAKING / ACCEL DETECTION --------------
            if self.prev_accel_z is not None:
                diff = az - self.prev_accel_z

                if diff < -THRESHOLDS["BRAKE_SENSITIVITY"]:
                    self.brake_events += 1
                    brake_flag = 1
                    print("⚠ HARSH BRAKING DETECTED")

                elif diff > THRESHOLDS["ACCEL_SENSITIVITY"]:
                    self.harsh_accel_events += 1
                    harsh_flag = 1
                    print("⚠ HARSH ACCELERATION DETECTED")

            self.prev_accel_z = az

            # Estimate distance for this 1-second sample:
            #   distance (km) = speed(km/h) * (seconds / 3600)
            distance_step_km = round(speed_kmh * (1.0 / 3600.0), 4)

            # --------- STANDARDIZED SAMPLE FOR THE REST OF THE APP ---------
            standardized_sample = {
                "speed": float(speed_kmh),
                "brake_events": int(brake_flag),
                "harsh_accel": int(harsh_flag),
                "distance_km": distance_step_km,
                # You still have access to richer data if needed later
                "timestamp": timestamp,
                "gps_lat": latitude,
                "gps_lon": longitude,
                "accel_x": ax,
                "accel_y": ay,
                "accel_z": az,
                "speeding_flag": int(speeding_flag),
            }

            # If a buffer is provided, push this standardized sample.
            if buffer:
                try:
                    # Prefer DataBuffer-style API
                    if hasattr(buffer, "add_entry"):
                        buffer.add_entry(standardized_sample)
                    # Backward-compat: some older code might use add_sample()
                    elif hasattr(buffer, "add_sample"):
                        buffer.add_sample(standardized_sample)
                except Exception as e:
                    print(f"[SensorListener] Buffer write error: {e}")

            # Console debug log (used by Streamlit display_live_measurement_ui.py)
            print(
                f"[{timestamp}] "
                f"Speed={speed_kmh} | AccelZ={az} | GPS=({latitude}, {longitude})"
            )
            time.sleep(1)

        print("\n=== Sensor Session Complete ===\n")

    def stop_listeners(self):
        """Stop collecting sensor data"""
        self.is_active = False
        print("\n=== Sensors Stopped ===\n")
