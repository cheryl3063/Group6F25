from scoring_engine import calculate_score
from mock_backend import save_score
from alert_rules import AlertRules

# shared instance (for Task 55–57)
alert_system = AlertRules()

def compute_summary(samples):
    """
    samples: list of dicts like
      {"speed": 52.3, "brake_events": 1, "harsh_accel": 0, "distance_km": 1.8}
    Returns a summary dict containing distance, speed, events, safety score, and low-score alert.
    """

    # ---------- HANDLE EMPTY OR INVALID ----------
    if not samples:
        return {
            "total_distance_km": 0.0,
            "avg_speed_kmh": 0.0,
            "brake_events": 0,
            "harsh_accel": 0,
            "safety_score": 100,
            "low_score_alert": False
        }

    # Filter out invalid samples
    samples = [s for s in samples if isinstance(s, dict)]
    if not samples:
        return {
            "total_distance_km": 0.0,
            "avg_speed_kmh": 0.0,
            "brake_events": 0,
            "harsh_accel": 0,
            "safety_score": 100,
            "low_score_alert": False
        }

    # ---------- COMPUTE RAW VALUES ----------
    n = len(samples)

    total_dist = sum(float(s.get("distance_km", 0) or 0) for s in samples)
    avg_speed = sum(float(s.get("speed", 0) or 0) for s in samples) / n
    brakes = sum(int(s.get("brake_events", 0) or 0) for s in samples)
    harsh = sum(int(s.get("harsh_accel", 0) or 0) for s in samples)

    # ---------- PREPARE SCORE INPUT ----------
    trip_data = {
        "speeding_events": 0,
        "harsh_brakes": brakes,
        "harsh_accels": harsh,
        "avg_speed": avg_speed,
        "distance_km": total_dist,
        "duration_min": n,
    }

    # Calculate the proper safety score
    score = calculate_score(trip_data)

    # ---------- SAVE TO MOCK BACKEND ----------
    save_score("user123", {
        "score": score,
        "avg_speed": round(avg_speed, 1),
        "distance_km": round(total_dist, 2),
        "brake_events": int(brakes),
        "harsh_accel": int(harsh)
    })

    # ---------- TASK 55–57: LOW SCORE ALERT ----------
    low_score_alert = alert_system.evaluate_score(score)

    # ---------- RETURN COMBINED SUMMARY ----------
    return {
        "total_distance_km": round(total_dist, 2),
        "avg_speed_kmh": round(avg_speed, 1),
        "brake_events": int(brakes),
        "harsh_accel": int(harsh),
        "safety_score": int(score),
        "low_score_alert": low_score_alert
    }
