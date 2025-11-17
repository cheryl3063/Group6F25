# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify

# Optional: only import firebase_admin if the key is present
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

# ---- Resolve absolute path to the Firebase service key ----
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
        # Firebase key exists but init failed (bad key/permissions)
        # Keep FIREBASE_READY = False and allow dev fallback for /login
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

@app.route("/register", methods=["POST"])
def register():
    """
    Creates a new Firebase user (email + password) when Firebase is ready.
    If Firebase is NOT ready, returns 503 to avoid implying users are persisted.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return json_err("email and password are required.", 400)

    if not FIREBASE_READY:
        return json_err("Registration unavailable in dev mode. Add serviceAccountKey.json.", 503)

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"uid": user.uid, "message": "User created"}), 201
    except Exception as e:
        msg = str(e)
        if "already exists" in msg.lower() or "EMAIL_EXISTS" in msg:
            return json_err("Email already registered.", 409)
        return json_err(msg, 400)

@app.route("/login", methods=["POST"])
def login():
    """
    If Firebase is ready: verify the user exists via get_user_by_email.
    (Note: this does not verify password yet — wire password auth later.)
    If Firebase is NOT ready: provide a simple dev fallback that accepts
    any non-empty password for emails ending with @gmail.com.
    """
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
    else:
        # 🔧 Dev fallback for your Kivy demo
        if email.lower().endswith("@gmail.com") and password:
            return jsonify({"uid": "DEV_UID_123", "message": "Login OK (dev mode)"}), 200
        return json_err("Invalid credentials (dev mode expects @gmail.com + any password).", 401)

# ----------------- Entrypoint ----------------
if __name__ == "__main__":
    # Bind to 5050 so your Kivy UI can call http://127.0.0.1:5050/login
    app.run(host="127.0.0.1", port=5050, debug=True)
