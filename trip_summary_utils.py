def compute_summary(samples):
    if not samples:
        return {
            "total_distance_km": 0.0,
            "avg_speed_kmh": 0.0,
            "brake_events": 0,
            "harsh_accel": 0,
            "safety_score": 0
        }

    total_distance = sum(s["distance_km"] for s in samples)
    avg_speed = sum(s["speed"] for s in samples) / len(samples)
    total_brake = sum(s["brake_events"] for s in samples)
    total_harsh = sum(s["harsh_accel"] for s in samples)

    score = max(0, 100 - (total_brake * 5 + total_harsh * 7))

    return {
        "total_distance_km": round(total_distance, 2),
        "avg_speed_kmh": round(avg_speed, 1),
        "brake_events": total_brake,
        "harsh_accel": total_harsh,
        "safety_score": score
    }
