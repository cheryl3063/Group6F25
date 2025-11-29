# threshold_config.py

# ---------- SPEED THRESHOLD ----------
SPEED_LIMIT_KMH = 110         # max safe speed before speeding event

# ---------- BRAKING THRESHOLD ----------
BRAKE_SENSITIVITY = 2         # count brake event if braking > threshold

# ---------- ACCEL THRESHOLD ----------
ACCEL_SENSITIVITY = 3         # count harsh accel event if accel > threshold

# ---------- SAFETY SCORE BASE ----------
SCORE_START = 100             # starting score before penalties

# ---------- PENALTY VALUES ----------
SPEED_PENALTY = 5             # score -5 per speeding event
BRAKE_PENALTY = 5             # score -5 per harsh brake event
ACCEL_PENALTY = 5             # score -5 per harsh accel event

# dictionary used in imports
THRESHOLDS = {
    "SPEED_LIMIT_KMH": SPEED_LIMIT_KMH,
    "BRAKE_SENSITIVITY": BRAKE_SENSITIVITY,
    "ACCEL_SENSITIVITY": ACCEL_SENSITIVITY,
    "SCORE_START": SCORE_START,
    "SPEED_PENALTY": SPEED_PENALTY,
    "BRAKE_PENALTY": BRAKE_PENALTY,
    "ACCEL_PENALTY": ACCEL_PENALTY
}
