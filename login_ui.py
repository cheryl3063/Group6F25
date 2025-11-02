## -*- coding: utf-8 -*-

import re
import time
import requests
import streamlit as st

# Point to your Flask login route
API_URL = "http://127.0.0.1:5000/login"

st.set_page_config(page_title="Driver Analytics – Login", page_icon="🚗", layout="centered")
st.title("Driver Analytics")
st.subheader("Sign in to continue")

# Show what URL the UI is calling (for debugging)
st.caption(f"Auth API → {API_URL}")

with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email", placeholder="name@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    login_clicked = st.form_submit_button("Login")

def valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", (e or "").strip()))

def toast(msg: str, kind: str = "info"):
    {"success": st.success, "error": st.error}.get(kind, st.info)(msg)

if login_clicked:
    if not email or not password:
        toast("Please enter both email and password.", "error")
    elif not valid_email(email):
        toast("Please enter a valid email address.", "error")
    else:
        with st.spinner("Authenticating…"):
            try:
                resp = requests.post(
                    API_URL,
                    json={"email": email, "password": password},
                    timeout=8,
                )

                # Parse JSON only when the server actually sent JSON
                data = {}
                raw = resp.text
                ctype = (resp.headers.get("Content-Type") or "").lower()
                if "application/json" in ctype:
                    try:
                        data = resp.json()
                    except ValueError:
                        # leave raw as-is for debugging
                        pass

                if resp.ok:
                    uid = data.get("uid")
                    toast(f"Welcome {email}!", "success")
                    st.session_state["user"] = {"email": email, "uid": uid}
                else:
                    # Prefer the backend message, otherwise show raw text or status code
                    msg = data.get("error") or data.get("message") or raw or f"Login failed (HTTP {resp.status_code})."
                    toast(msg, "error")

            except requests.exceptions.ConnectionError:
                toast("Backend not reachable. Is the Flask API running at this URL?", "error")
            except requests.exceptions.Timeout:
                toast("Backend timed out. Please try again.", "error")
            except Exception as e:
                toast(f"Unexpected error: {type(e).__name__}: {e}", "error")
