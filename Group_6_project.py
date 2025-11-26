# -*- coding: utf-8 -*-
import os
import json
from flask import Flask, request, jsonify

# Optional Firebase imports
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

# ------- Firebase Setup -------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

FIREBASE_READY = False
if os.path.exists(KEY_PATH):
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(KEY_PATH)
            firebase_admin.initialize_app(cred)
        FIREBASE_READY = True
    except Exception as e:
        print(f"[WARN] Firebase init failed: {e}")
else:
    print(f"[WARN] Firebase key not found at: {KEY_PATH}. Using dev fallback for /login.")

# ----------------- Helpers -----------------
def json_err(msg, code=400):
    return jsonify({"error": msg}), code

# ----------------- Routes ------------------

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "firebase_ready": FIREBASE_READY
    }), 200


# ---------- Register ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return json_err("email and password are required.", 400)

    if not FIREBASE_READY:
        return json_err("Registration unavailable in dev mode.", 503)

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"uid": user.uid, "message": "User created"}), 201
    except Exception as e:
        msg = str(e)
        if "already exists" in msg.lower():
            return json_err("Email already registered.", 409)
        return json_err(msg, 400)


# ---------- Login ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return json_err("email and password are required.", 400)

    # Firebase real login
    if FIREBASE_READY:
        try:
            user = auth.get_user_by_email(email)
            return jsonify({
                "message": f"User {user.email} authenticated successfully!",
                "uid": user.uid
            }), 200
        except Exception as e:
            return json_err(str(e), 404)

    # Dev-mode login
    if email.endswith("@gmail.com") and password:
        return jsonify({"uid": "DEV_UID_123", "message": "Login OK (dev mode)"}), 200

    return json_err("Invalid credentials (dev mode expects @gmail.com + any password).", 401)


# ------------------------------------------------------
# ⭐ NEW ROUTE — SAVE TRIP DATA FROM KIVY
# ------------------------------------------------------
@app.route("/save_trip", methods=["POST"])
def save_trip():
    print("\n📥 Received trip data request...")

    data = request.get_json(silent=True)
    if not data:
        return json_err("No JSON body received.", 400)

    print(f"→ Trip Payload: {data}")

    # Save trip data to local file
    save_path = os.path.join(BASE_DIR, "saved_trips.json")

    # Load previous data
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            try:
                db = json.load(f)
            except:
                db = []
    else:
        db = []

    # Append new trip
    db.append(data)

    with open(save_path, "w") as f:
        json.dump(db, f, indent=4)

    print("✔ Trip saved successfully.")

    return jsonify({"status": "saved", "entries": len(db)}), 200


# ----------------- Entrypoint ----------------
if __name__ == "__main__":
    print("🚀 Starting Flask backend on http://127.0.0.1:5050 ...")
    app.run(host="127.0.0.1", port=5050, debug=True)
