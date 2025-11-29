# driving_thresholds.py
"""
Central place for all driving-related thresholds.
You can tweak these values without changing the logic everywhere else.
"""

# Speeds in km/h
SPEED_LIMIT = 110          # above this counts as speeding
SPEEDING_TOLERANCE = 5     # grace zone before we mark it as speeding

# Acceleration thresholds (example values, in m/s^2)
# In our simulation we just reuse the accelerometer X value as "longitudinal accel".
HARSH_BRAKE_THRESHOLD = -4.0   # strong deceleration
HARSH_ACCEL_THRESHOLD = 3.5    # strong acceleration
