# -*- coding: utf-8 -*-
import re
import time
import requests
import streamlit as st

# Flask backend endpoint
API_URL = "http://127.0.0.1:5000/login"

# Streamlit page setup
st.set_page_config(page_title="Driver Analytics – Login", page_icon="🚗", layout="centered")
st.title("Driver Analytics")
st.subheader("Sign in to continue")

# Show API endpoint for debugging
st.caption(f"Auth API → {API_URL}")

# -------------------------------------------------------------------
# Email validation helper
# -------------------------------------------------------------------
def valid_email(e: str) -> bool:
    """Return True only if email looks valid AND ends with @gmail.com"""
    e = (e or "").strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
        return False
    return e.endswith("@gmail.com")

# -------------------------------------------------------------------
# Notification helper
# -------------------------------------------------------------------
def toast(msg: str, kind: str = "info"):
    {"success": st.success, "error": st.error}.get(kind, st.info)(msg)

# -------------------------------------------------------------------
# Login form UI
# -------------------------------------------------------------------
with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email", placeholder="name@gmail.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    login_clicked = st.form_submit_button("Login")

# -------------------------------------------------------------------
# Handle form submission
# -------------------------------------------------------------------
if login_clicked:
    email = email.strip().lower()
    password = password.strip()

    if not email or not password:
        toast("Please enter both email and password.", "error")
    elif not valid_email(email):
        toast("Please enter a valid Gmail address ending with '@gmail.com'.", "error")
    else:
        with st.spinner("Authenticating…"):
            try:
                resp = requests.post(
                    API_URL,
                    json={"email": email, "password": password},
                    timeout=8,
                )

                # Parse JSON if available
                data = {}
                raw = resp.text
                ctype = (resp.headers.get("Content-Type") or "").lower()
                if "application/json" in ctype:
                    try:
                        data = resp.json()
                    except ValueError:
                        pass  # fallback to raw

                # Handle backend responses
                if resp.ok:
                    uid = data.get("uid")
                    toast(f"Welcome {email}!", "success")
                    st.session_state["user"] = {"email": email, "uid": uid}
                else:
                    msg = data.get("error") or data.get("message") or raw or f"Login failed (HTTP {resp.status_code})."
                    toast(msg, "error")

            except requests.exceptions.ConnectionError:
                toast("Backend not reachable. Is the Flask API running at this URL?", "error")
            except requests.exceptions.Timeout:
                toast("Backend timed out. Please try again.", "error")
            except Exception as e:
                toast(f"Unexpected error: {type(e).__name__}: {e}", "error")
