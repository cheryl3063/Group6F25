def calculate_score(trip_data):
    """
    trip_data example:
    {
        "speeding_events": 3,
        "harsh_brakes": 1,
        "harsh_accels": 2,
        "avg_speed": 85,
        "distance_km": 12.4,
        "duration_min": 18
    }
    """

    # ---------- VALIDATION ----------
    if not isinstance(trip_data, dict):
        return 0

    # Safe extraction
    speeding = trip_data.get("speeding_events", 0) or 0
    harsh_brakes = trip_data.get("harsh_brakes", 0) or 0
    harsh_accels = trip_data.get("harsh_accels", 0) or 0
    avg_speed = trip_data.get("avg_speed", 0) or 0
    distance = trip_data.get("distance_km", 0) or 0
    duration = trip_data.get("duration_min", 0) or 0

    # Convert types safely
    try:
        speeding = int(speeding)
        harsh_brakes = int(harsh_brakes)
        harsh_accels = int(harsh_accels)
        avg_speed = float(avg_speed)
        distance = float(distance)
        duration = float(duration)
    except:
        return 0

    # ---------- BASE SCORE ----------
    score = 100

    # ---------- ALERT-BASED PENALTIES ----------
    score -= speeding * 3            # speeding hurts score moderately
    score -= harsh_brakes * 5        # harsh braking is dangerous
    score -= harsh_accels * 4        # harsh accel is moderately dangerous

    # ---------- SPEED PENALTY ----------
    if avg_speed > 120:
        score -= 25
    elif avg_speed > 110:
        score -= 15
    elif avg_speed > 100:
        score -= 10

    # ---------- OPTIONAL BONUSES ----------
    # Longer trips = more reliable score
    if distance > 10:
        score += 3
    elif distance > 5:
        score += 2

    # Very short trips produce unstable score
    if duration < 5:
        score -= 2

    # ---------- FINAL CLAMP ----------
    return max(0, min(100, int(score)))
