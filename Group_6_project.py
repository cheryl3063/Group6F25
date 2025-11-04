# -*- coding: utf-8 -*-
#  from flask import Flask, request, jsonify
# import os
# import firebase_admin
# from firebase_admin import credentials, auth
#
# app = Flask(__name__)
#
# # --- Resolve absolute path to the key, and init Firebase safely ---
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# SERVICE_KEY = os.path.join(BASE_DIR, "serviceAccountKey.json")
#
# if not os.path.exists(SERVICE_KEY):
#     raise FileNotFoundError(f"serviceAccountKey.json not found at: {SERVICE_KEY}")
#
# if not firebase_admin._apps:
#     cred = credentials.Certificate(SERVICE_KEY)
#     firebase_admin.initialize_app(cred)
#
# @app.route("/ping", methods=["GET"])
# def ping():
#     return jsonify({"ok": True}), 200
#
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json(silent=True) or {}
#     email = data.get("email")
#     password = data.get("password")  # not verified here; demo only
#
#     if not email:
#         return jsonify({"error": "Email is required."}), 400
#
#     try:
#         user = auth.get_user_by_email(email)
#         return jsonify({
#             "message": f"User {user.email} authenticated successfully!",
#             "uid": user.uid
#         }), 200
#     except Exception as e:
#         # e.g., No user record found…
#         return jsonify({"error": str(e)}), 404
#
#
#
# if __name__ == "__main__":
#     # Pin host/port so they match your UI
#     app.run(host="127.0.0.1", port=5000, debug=True)


# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
import os

app = Flask(__name__)

# --- Firebase Admin init ---
# Make sure the file name exactly matches your file on disk!
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

def json_err(msg, code=400):
    return jsonify({"error": msg}), code

@app.route("/register", methods=["POST"])
def register():
    """Create a new user (email + password) and return uid with 201."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return json_err("email and password are required.", 400)

    try:
        user = auth.create_user(email=email, password=password)
        return jsonify({"uid": user.uid, "message": "User created"}), 201
    except Exception as e:
        # If user exists or any Firebase error, report nicely
        msg = str(e)
        # Optional: turn specific cases into 409
        if "already exists" in msg.lower() or "EMAIL_EXISTS" in msg:
            return json_err("Email already registered.", 409)
        return json_err(msg, 400)

@app.route("/login", methods=["POST"])
def login():
    """
    Current behavior: 'login' verifies that the email exists in Firebase.
    NOTE: This does NOT validate the password yet.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return json_err("email and password are required.", 400)

    try:
        user = auth.get_user_by_email(email)
        return jsonify({
            "message": f"User {user.email} authenticated successfully!",
            "uid": user.uid
        }), 200
    except Exception as e:
        return json_err(str(e), 404)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Bind explicitly to 127.0.0.1:5000 to match your UI/tests
    app.run(host="127.0.0.1", port=5000, debug=True)

