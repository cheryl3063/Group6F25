# threshold_config.py

# ---------- SPEED THRESHOLD ----------
# Max safe speed before marking as speeding event
SPEED_LIMIT_KMH = 110

# ---------- BRAKING THRESHOLD ----------
# Max acceptable brake events across a full trip
BRAKE_EVENT_LIMIT = 2

# ---------- ACCEL THRESHOLD ----------
# Max acceptable harsh acceleration events across a full trip
HARSH_ACCEL_LIMIT = 3

# ---------- SAFETY SCORE BASE ----------
# Default score to start from before deducting penalties
BASE_SAFETY_SCORE = 100

# ---------- PENALTY VALUES ----------
# How much to subtract for each type of bad event
PENALTY_SPEEDING = 5
PENALTY_BRAKING = 5
PENALTY_ACCEL = 5

# ---------- NEW FOR SENSOR DETECTION ----------
# Sensitivity determines how strong a change triggers the event
# (not total limit — this is used during trip to detect events)
BRAKE_SENSITIVITY = 2.5         # If accelZ drops more than this → harsh braking
ACCEL_SENSITIVITY = 2.5         # If accelZ rises more than this → harsh acceleration

# ---------- MASTER DICT for easy access ----------
THRESHOLDS = {
    "SPEED_LIMIT_KMH": SPEED_LIMIT_KMH,

    # Total event limits (used in scoring after trip)
    "BRAKE_EVENT_LIMIT": BRAKE_EVENT_LIMIT,
    "HARSH_ACCEL_LIMIT": HARSH_ACCEL_LIMIT,

    # Sensitivity thresholds (used in live SensorListener detection)
    "BRAKE_SENSITIVITY": BRAKE_SENSITIVITY,
    "ACCEL_SENSITIVITY": ACCEL_SENSITIVITY,

    # Scoring system
    "BASE_SAFETY_SCORE": BASE_SAFETY_SCORE,
    "PENALTY_SPEEDING": PENALTY_SPEEDING,
    "PENALTY_BRAKING": PENALTY_BRAKING,
    "PENALTY_ACCEL": PENALTY_ACCEL,
}
