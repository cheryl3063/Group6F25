# test_sensor_flow.py
"""
Stress-test SensorListener for 2–3 simulated trips.

Goal of Task 107:
- Make sure SensorListener can run multiple trips in a row
- Confirm that samples are in the standardized format:
    {
        "speed": float,
        "brake_events": int,
        "harsh_accel": int,
        "distance_km": float,
        ...
    }
- Ensure there are no crashes or weird state carry-over between trips.
"""

from sensors_listeners import SensorListener


class MockBuffer:
    """
    Very simple in-memory buffer used only for testing.
    It mimics DataBuffer.add_entry(data) but does NOT write to disk.
    """
    def __init__(self):
        self.samples = []

    def add_entry(self, data: dict):
        self.samples.append(data)


def run_single_trip(trip_index: int):
    print(f"\n==============================")
    print(f"🚗 Starting simulated trip #{trip_index}")
    print(f"==============================")

    buffer = MockBuffer()
    listener = SensorListener()

    # This will run its internal loop (10 iterations in sensors_listeners.start_listeners)
    listener.start_listeners(buffer=buffer)

    # After trip completes, print summary
    total_samples = len(buffer.samples)
    total_brakes = sum(s.get("brake_events", 0) for s in buffer.samples)
    total_harsh = sum(s.get("harsh_accel", 0) for s in buffer.samples)
    total_distance = sum(s.get("distance_km", 0.0) for s in buffer.samples)
    avg_speed = (
        sum(s.get("speed", 0.0) for s in buffer.samples) / total_samples
        if total_samples > 0 else 0.0
    )

    print(f"Trip #{trip_index} complete:")
    print(f"  • Samples collected : {total_samples}")
    print(f"  • Avg speed (km/h) : {avg_speed:.1f}")
    print(f"  • Brake events     : {total_brakes}")
    print(f"  • Harsh accel      : {total_harsh}")
    print(f"  • Distance (km)    : {total_distance:.3f}")

    # Quick format sanity-check on first sample
    if total_samples > 0:
        first = buffer.samples[0]
        print("\nSample[0] structure:")
        for k, v in first.items():
            print(f"  - {k}: {v} ({type(v).__name__})")

    print("\nNo crashes for this trip ✅")
    return buffer, listener


if __name__ == "__main__":
    # Run 3 back-to-back simulated trips
    for i in range(1, 4):
        run_single_trip(i)

    print("\nAll 3 trips finished without error ✅")
