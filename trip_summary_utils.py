# trip_summary_utils.py

from scoring_engine import calculate_score


def compute_summary(samples):
    """
    Compute aggregated metrics and safety score from raw samples.

    samples: list of dicts like
      {"speed": 52.3, "brake_events": 1, "harsh_accel": 0, "distance_km": 1.8}

    Returns a summary dict:
      {
        "total_distance_km": float,
        "avg_speed_kmh": float,
        "brake_events": int,
        "harsh_accel": int,
        "safety_score": int
      }
    """
    if not samples:
        return {
            "total_distance_km": 0.0,
            "avg_speed_kmh": 0.0,
            "brake_events": 0,
            "harsh_accel": 0,
            "safety_score": 100,   # best possible if nothing recorded
        }

    n = len(samples)

    total_dist = sum(s.get("distance_km", 0.0) for s in samples)
    avg_speed = sum(s.get("speed", 0.0) for s in samples) / n
    brakes = sum(s.get("brake_events", 0) for s in samples)
    harsh = sum(s.get("harsh_accel", 0) for s in samples)

    # Delegate scoring to scoring_engine using configured thresholds
    safety_score = calculate_score(
        avg_speed_kmh=avg_speed,
        brake_events=brakes,
        harsh_accel_events=harsh,
        distance_km=total_dist,
    )

    return {
        "total_distance_km": round(total_dist, 2),
        "avg_speed_kmh": round(avg_speed, 1),
        "brake_events": int(brakes),
        "harsh_accel": int(harsh),
        "safety_score": int(safety_score),
    }
