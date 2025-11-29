# scoring_engine.py
"""
Score calculation for DriveIQ trips.

Takes high-level trip metrics (avg speed, events, distance)
and returns a safety score between 0 and 100.
"""

from threshold_config import (
    BASE_SAFETY_SCORE,
    SPEED_LIMIT_KMH, PENALTY_SPEEDING,
    BRAKE_EVENT_LIMIT, PENALTY_BRAKING,
    HARSH_ACCEL_LIMIT, PENALTY_ACCEL,
)


def calculate_score(avg_speed_kmh: float,
                    brake_events: int,
                    harsh_accel_events: int,
                    distance_km: float) -> int:
    """
    Compute a simple safety score using threshold_config values.

    Parameters
    ----------
    avg_speed_kmh : float
        Average speed for the trip in km/h.
    brake_events : int
        Count of brake events recorded.
    harsh_accel_events : int
        Count of harsh acceleration events.
    distance_km : float
        Total distance of the trip in km (currently not used in penalties,
        but kept for future normalization if needed).

    Returns
    -------
    int
        Safety score clamped between 0 and 100.
    """

    # Start from base score
    score = float(BASE_SAFETY_SCORE)

    # ---------- SPEEDING ----------
    # Simple rule: if avg speed exceeds limit, apply one speeding penalty.
    if avg_speed_kmh > SPEED_LIMIT_KMH:
        score -= PENALTY_SPEEDING

    # ---------- BRAKING ----------
    # Only penalize braking ABOVE the allowed limit.
    extra_brakes = max(0, brake_events - BRAKE_EVENT_LIMIT)
    score -= extra_brakes * PENALTY_BRAKING

    # ---------- HARSH ACCEL ----------
    extra_accel = max(0, harsh_accel_events - HARSH_ACCEL_LIMIT)
    score -= extra_accel * PENALTY_ACCEL

    # Clamp between 0 and 100
    score = max(0, min(100, round(score)))

    return int(score)
