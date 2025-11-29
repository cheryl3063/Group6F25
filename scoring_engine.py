# scoring_engine.py

"""
Simple scoring engine for a single trip.

We start from BASE_SAFETY_SCORE, then subtract penalties for:
- speeding (if average speed above limit)
- brake events
- harsh acceleration events
"""

from threshold_config import (
    BASE_SAFETY_SCORE,
    PENALTY_SPEEDING,
    PENALTY_BRAKING,
    PENALTY_ACCEL,
    SPEED_LIMIT_KMH,
)


def calculate_score(avg_speed_kmh: float,
                    brake_events: int,
                    harsh_accel_events: int,
                    distance_km: float) -> int:
    """
    Calculate a safety score for one trip.

    Args:
        avg_speed_kmh: average speed over the trip
        brake_events: total brake events
        harsh_accel_events: total harsh accel events
        distance_km: total distance (not heavily used yet, but kept for future rules)

    Returns:
        Integer score between 0 and 100.
    """
    score = BASE_SAFETY_SCORE

    # Simple speeding rule: 1 speeding event if avg speed above limit
    speeding_events = 1 if avg_speed_kmh > SPEED_LIMIT_KMH else 0

    score -= speeding_events * PENALTY_SPEEDING
    score -= brake_events * PENALTY_BRAKING
    score -= harsh_accel_events * PENALTY_ACCEL

    # Clamp to [0, 100]
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return int(score)
