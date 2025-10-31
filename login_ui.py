# -*- coding: utf-8 -*-
import re, time, requests, streamlit as st

API_URL = "http://127.0.0.1:5000/login"  # backend endpoint (Tonse's Flask API)

st.set_page_config(page_title="Driver Analytics – Login", page_icon="🚗", layout="centered")
st.title("Driver Analytics")
st.subheader("Sign in to continue")

with st.form("login_form", clear_on_submit=False):
    email = st.text_input("Email", placeholder="name@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    login_clicked = st.form_submit_button("Login")

def valid_email(e: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e.strip()))

def toast(msg: str, kind: str = "info"):
    {"success": st.success, "error": st.error}.get(kind, st.info)(msg)

if login_clicked:
    if not email or not password:
        toast("Please enter both email and password.", "error")
    elif not valid_email(email):
        toast("Please enter a valid email address.", "error")
    else:
        with st.spinner("Authenticating…"):
            time.sleep(0.4)
            try:
                r = requests.post(API_URL, json={"email": email, "password": password}, timeout=6)
                data = r.json()
                if r.status_code == 200:
                    toast(f"Welcome {email}!", "success")
                    st.session_state["user"] = {"email": email, "uid": data.get("uid")}
                else:
                    toast(data.get("error", "Login failed."), "error")
            except Exception:
                toast("Backend not reachable. UI is working; waiting on API hookup.", "info")
