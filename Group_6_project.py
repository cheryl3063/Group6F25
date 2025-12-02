# -*- coding: utf-8 -*-
import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")
SAVE_PATH = os.path.join(BASE_DIR, "saved_trips.json")

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


def json_err(msg, code=400):
    return jsonify({"error": msg}), code


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

    if FIREBASE_READY:
        try:
            user = auth.get_user_by_email(email)
            return jsonify({
                "message": f"User {user.email} authenticated successfully!",
                "uid": user.uid
            }), 200
        except Exception as e:
            return json_err(str(e), 404)

    if email.endswith("@gmail.com") and password:
        return jsonify({"uid": "DEV_UID_123", "message": "Login OK (dev mode)"}), 200

    return json_err("Invalid credentials (dev mode expects @gmail.com + any password).", 401)


# ---------- Save Trip ----------
@app.route("/save_trip", methods=["POST"])
def save_trip():
    print("\n📥 Received trip data request...")

    data = request.get_json(silent=True)
    if not data:
        return json_err("No JSON body received.", 400)

    print(f"→ Trip Payload: {data}")

    # Load existing file
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH, "r") as f:
                db = json.load(f)
            if isinstance(db, list):
                print("⚠ Converting old list-format backend into dict-format.")
                db = {"user123": db}
        except Exception:
            db = {}
    else:
        db = {}

    user_id = "user123"
    if user_id not in db:
        db[user_id] = []

    new_trip = {
        "trip_id": str(uuid.uuid4()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "samples": data.get("samples", []),
        "summary": data.get("summary", {})
    }

    db[user_id].append(new_trip)

    with open(SAVE_PATH, "w") as f:
        json.dump(db, f, indent=4)

    print("✔ Trip saved successfully.")
    return jsonify({"status": "saved", "trip": new_trip}), 200


if __name__ == "__main__":
    print("🚀 Starting Flask backend on http://127.0.0.1:5050 ...")
    app.run(host="127.0.0.1", port=5050, debug=True)
