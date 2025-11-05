# display_live_measurement_ui.py
# - Starts your existing SensorListener()
# - Intercepts its printed lines, parses Accelerometer/Gyro/GPS
# - Computes duration + distance (via haversine) + approximate speed (km/h)
# - Displays live metrics + simple charts in Streamlit

import io
import re
import math
import time
import threading
from datetime import datetime
from contextlib import redirect_stdout
from typing import Optional, Tuple, Dict, List

import streamlit as st
import pandas as pd

# --- Import your team's SensorListener without modifying their code ---
try:
    from sensors_listeners import SensorListener  # if file is sensors_listeners.py
except Exception:
    from Sensor_listener import SensorListener    # fallback to Sensor_listener.py (as provided)

# -----------------------
# Helpers
# -----------------------

GPS_RE = re.compile(
    r"GPS\s*→\s*Lat\s*=\s*([-\d\.]+)\s*,\s*Lon\s*=\s*([-\d\.]+)",
    re.IGNORECASE,
)
ACC_RE = re.compile(
    r"Accelerometer\s*→\s*X\s*=\s*([-\d\.]+)\s*,\s*Y\s*=\s*([-\d\.]+)\s*,\s*Z\s*=\s*([-\d\.]+)",
    re.IGNORECASE,
)
GYR_RE = re.compile(
    r"Gyroscope\s*→\s*X\s*=\s*([-\d\.]+)\s*,\s*Y\s*=\s*([-\d\.]+)\s*,\s*Z\s*=\s*([-\d\.]+)",
    re.IGNORECASE,
)

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Great-circle distance in kilometers."""
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dlmb/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# -----------------------
# Streamlit App State
# -----------------------
st.set_page_config(page_title="Live Telemetry", layout="centered")
st.title("🚗 Live Telemetry UI (Streamlit)")

if "running" not in st.session_state:
    st.session_state.running = False
if "start_time" not in st.session_state:
    st.session_state.start_time: Optional[float] = None
if "total_km" not in st.session_state:
    st.session_state.total_km = 0.0
if "last_gps" not in st.session_state:
    st.session_state.last_gps: Optional[Tuple[float, float, float]] = None  # (lat, lon, ts)
if "speed_series" not in st.session_state:
    st.session_state.speed_series: List[Tuple[float, float]] = []  # (ts, kmh)
if "acc_series" not in st.session_state:
    st.session_state.acc_series: List[Tuple[float, float]] = []   # (ts, |a|)
if "sensor_thread" not in st.session_state:
    st.session_state.sensor_thread: Optional[threading.Thread] = None
if "sensor_obj" not in st.session_state:
    st.session_state.sensor_obj: Optional[SensorListener] = None
if "lock" not in st.session_state:
    st.session_state.lock = threading.Lock()

# This dict holds latest parsed values
if "latest" not in st.session_state:
    st.session_state.latest: Dict[str, float] = {
        "lat": 0.0, "lon": 0.0, "ax": 0.0, "ay": 0.0, "az": 0.0,
        "gx": 0.0, "gy": 0.0, "gz": 0.0, "speed_kmh": 0.0
    }

# -----------------------
# Output tap to parse SensorListener prints without changing their code
# -----------------------
class LineParser(io.TextIOBase):
    """
    File-like object that receives text from prints inside SensorListener.
    We forward to real stdout (so devs still see logs), and parse lines to update UI state.
    """
    def __init__(self, real_stdout):
        self.real_stdout = real_stdout
        self.buf = ""

    def writable(self): return True

    def write(self, s: str):
        # forward to console
        self.real_stdout.write(s)
        # accumulate for line parsing
        self.buf += s
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            self.process_line(line.strip())
        return len(s)

    def process_line(self, line: str):
        ts = time.time()
        # Accelerometer
        m = ACC_RE.search(line)
        if m:
            ax, ay, az = map(float, m.groups())
            with st.session_state.lock:
                st.session_state.latest.update({"ax": ax, "ay": ay, "az": az})
                amag = (ax**2 + ay**2 + az**2) ** 0.5  # |a|
                st.session_state.acc_series.append((ts, amag))
                # keep last 300 points
                st.session_state.acc_series = st.session_state.acc_series[-300:]
            return

        # Gyro
        m = GYR_RE.search(line)
        if m:
            gx, gy, gz = map(float, m.groups())
            with st.session_state.lock:
                st.session_state.latest.update({"gx": gx, "gy": gy, "gz": gz})
            return

        # GPS → compute distance & speed
        m = GPS_RE.search(line)
        if m:
            lat, lon = map(float, m.groups())
            with st.session_state.lock:
                st.session_state.latest.update({"lat": lat, "lon": lon})
                # distance & speed from last GPS
                now = ts
                if st.session_state.last_gps:
                    plat, plon, pts = st.session_state.last_gps
                    dt = max(1e-6, now - pts)
                    dk = haversine_km(plat, plon, lat, lon)
                    st.session_state.total_km += dk
                    kmh = (dk / dt) * 3600.0
                    # clamp unrealistic jumps (since your SensorListener jitters)
                    kmh = max(0.0, min(120.0, kmh))
                    st.session_state.latest["speed_kmh"] = kmh
                    st.session_state.speed_series.append((now, kmh))
                    st.session_state.speed_series = st.session_state.speed_series[-300:]
                st.session_state.last_gps = (lat, lon, now)

# -----------------------
# Worker that runs your SensorListener and lets us parse its prints
# -----------------------
def run_sensors():
    st.session_state.sensor_obj = SensorListener()
    # redirect SensorListener prints through our LineParser
    parser = LineParser(real_stdout=io.TextIOWrapper(io.BufferedWriter(io.FileIO(1, 'w')), write_through=True))
    with redirect_stdout(parser):
        st.session_state.sensor_obj.start_listeners()

# -----------------------
# Controls
# -----------------------
c1, c2, c3 = st.columns(3)
start_btn = c1.button("Start Live View", type="primary", disabled=st.session_state.running)
stop_btn  = c2.button("Stop", disabled=not st.session_state.running)
reset_btn = c3.button("Reset")

if start_btn and not st.session_state.running:
    st.session_state.running = True
    st.session_state.start_time = time.time()
    # reset live data for a fresh run
    st.session_state.total_km = 0.0
    st.session_state.last_gps = None
    st.session_state.speed_series.clear()
    st.session_state.acc_series.clear()
    # start background sensor thread
    t = threading.Thread(target=run_sensors, daemon=True)
    st.session_state.sensor_thread = t
    t.start()

if stop_btn and st.session_state.running:
    st.session_state.running = False
    try:
        if st.session_state.sensor_obj:
            st.session_state.sensor_obj.stop_listeners()
    except Exception:
        pass

if reset_btn:
    st.session_state.running = False
    try:
        if st.session_state.sensor_obj:
            st.session_state.sensor_obj.stop_listeners()
    except Exception:
        pass
    st.session_state.start_time = None
    st.session_state.total_km = 0.0
    st.session_state.last_gps = None
    st.session_state.speed_series.clear()
    st.session_state.acc_series.clear()
    st.rerun()

# -----------------------
# Live Widgets
# -----------------------
m1, m2, m3 = st.columns(3)
with st.session_state.lock:
    speed_now = st.session_state.latest.get("speed_kmh", 0.0)
    total_km = st.session_state.total_km
    elapsed = 0
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)

m1.metric("Speed (km/h)", f"{speed_now:.1f}")
m2.metric("Distance (km)", f"{total_km:.2f}")
m3.metric("Duration", f"{elapsed//60:02d}:{elapsed%60:02d}")

# charts (last 60 points)
with st.session_state.lock:
    sp_df = pd.DataFrame(st.session_state.speed_series[-60:], columns=["ts", "kmh"]).set_index("ts")
    ac_df = pd.DataFrame(st.session_state.acc_series[-60:], columns=["ts", "amag"]).set_index("ts")

st.subheader("Speed (last 60s)")
if not sp_df.empty:
    st.line_chart(sp_df)
else:
    st.caption("Waiting for GPS updates…")

st.subheader("Accel Magnitude |a| (last 60s)")
if not ac_df.empty:
    st.line_chart(ac_df)
else:
    st.caption("Waiting for accelerometer updates…")

st.caption("This UI uses your existing SensorListener and parses its logs in real time (no code changes to teammates' files).")
