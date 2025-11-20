from scoring_engine import calculate_score
from trip_summary_utils import compute_summary

# ---------- TEST 1: SAFE DRIVER ----------
samples_safe = [
    {"speed": 50, "brake_events": 0, "harsh_accel": 0, "distance_km": 1.2},
    {"speed": 55, "brake_events": 0, "harsh_accel": 0, "distance_km": 1.0},
    {"speed": 60, "brake_events": 0, "harsh_accel": 0, "distance_km": 0.8},
]

print("\nTEST 1 — Safe Driver")
print(compute_summary(samples_safe))


# ---------- TEST 2: AGGRESSIVE DRIVER ----------
samples_aggressive = [
    {"speed": 110, "brake_events": 1, "harsh_accel": 2, "distance_km": 1.5},
    {"speed": 120, "brake_events": 2, "harsh_accel": 1, "distance_km": 1.2},
]

print("\nTEST 2 — Aggressive Driver")
print(compute_summary(samples_aggressive))


# ---------- TEST 3: TERRIBLE DRIVER ----------
samples_terrible = [
    {"speed": 130, "brake_events": 3, "harsh_accel": 4, "distance_km": 1.0},
    {"speed": 140, "brake_events": 4, "harsh_accel": 5, "distance_km": 1.0},
]

print("\nTEST 3 — Terrible Driver")
print(compute_summary(samples_terrible))
