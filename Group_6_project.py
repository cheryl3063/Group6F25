# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
import os

app = Flask(__name__)

# Load Firebase credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        # (In real apps, you'd verify password with Firebase Auth REST API)
        user = auth.get_user_by_email(email)
        return jsonify({
            "message": f"User {user.email} authenticated successfully!",
            "uid": user.uid
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
