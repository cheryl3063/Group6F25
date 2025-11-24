def calculate_score(trip_data):
    """
    trip_data structure example:
    {
        "speeding_events": 3,
        "harsh_brakes": 1,
        "harsh_accels": 2,
        "avg_speed": 85,
        "distance_km": 12.4,
        "duration_min": 18
    }
    """

    # ---------- BASIC VALIDATION ----------
    if not isinstance(trip_data, dict):
        return 0

    # Safe extraction (avoids None, missing keys)
    speeding = trip_data.get("speeding_events", 0) or 0
    harsh_brakes = trip_data.get("harsh_brakes", 0) or 0
    harsh_accels = trip_data.get("harsh_accels", 0) or 0
    avg_speed = trip_data.get("avg_speed", 0) or 0
    distance = trip_data.get("distance_km", 0) or 0
    duration = trip_data.get("duration_min", 0) or 0

    # Ensure all values are numbers
    try:
        speeding = int(speeding)
        harsh_brakes = int(harsh_brakes)
        harsh_accels = int(harsh_accels)
        avg_speed = float(avg_speed)
    except:
        return 0  # fallback safety

    # ---------- SCORING LOGIC ----------
    base_score = 100

    speeding_penalty = speeding * 2
    harsh_brake_penalty = harsh_brakes * 4
    accel_penalty = harsh_accels * 3

    # Avg speed penalty
    if avg_speed > 120:
        speed_penalty = 20
    elif avg_speed > 100:
        speed_penalty = 10
    else:
        speed_penalty = 0

    final_score = base_score - (
        speeding_penalty
        + harsh_brake_penalty
        + accel_penalty
        + speed_penalty
    )

    # Keep score between 0–100
    return max(0, min(100, int(final_score)))
