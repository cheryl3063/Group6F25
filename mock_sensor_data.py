# mock_sensor_data.py
"""
Fallback mock sensor data for testing and demos.

Each sample has the same structure Tonse's scoring/summary code expects:
{
    "speed": <km/h>,
    "brake_events": <int>,
    "harsh_accel": <int>,
    "distance_km": <float>
}
"""

import random


def build_mock_trip(num_points: int = 40):
    """
    Build a fake, but realistic, trip made of `num_points` samples.

    We keep speed mostly in a safe range, with a few braking
    and harsh-accel events sprinkled in.
    """
    samples = []

    # base speed around 60–80 km/h
    base_speed = random.randint(60, 75)

    for i in range(num_points):
        # small random variation around base speed
        speed = base_speed + random.randint(-8, 10)

        # every ~10th sample = braking
        brake = 1 if i in (10, 20, 30) else 0

        # a couple of harsh accelerations
        harsh = 1 if i in (15, 28) else 0

        # each sample ~0.2 km
        dist_step = 0.2

        samples.append({
            "speed": float(speed),
            "brake_events": brake,
            "harsh_accel": harsh,
            "distance_km": round(dist_step, 2),
        })

    return samples


if __name__ == "__main__":
    # quick manual smoke test
    from trip_summary_utils import compute_summary

    demo = build_mock_trip()
    print(f"Generated {len(demo)} samples")
    print(compute_summary(demo))
