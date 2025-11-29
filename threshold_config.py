# threshold_config.py
"""
Central thresholds and penalty configuration for DriveIQ scoring.
Change values here and the whole app will use updated rules.
"""

# ---------- SAFETY SCORE BASE ----------
BASE_SAFETY_SCORE = 100

# ---------- SPEED ----------
# Max safe speed before marking as speeding
SPEED_LIMIT_KMH = 110
PENALTY_SPEEDING = 5

# ---------- BRAKING ----------
# Max "normal" brake events before we consider it harsh overall
BRAKE_EVENT_LIMIT = 2
PENALTY_BRAKING = 5

# ---------- ACCELERATION ----------
# Max "normal" harsh accel events before we consider it aggressive
HARSH_ACCEL_LIMIT = 3
PENALTY_ACCEL = 5
