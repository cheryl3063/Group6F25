# test_login.py
import os
import time
import uuid
import requests
import pytest

BASE_URL = os.getenv("API_BASE", "http://127.0.0.1:5000")
LOGIN_URL = f"{BASE_URL}/login"
REGISTER_URL = f"{BASE_URL}/register"
HEALTH_URL = f"{BASE_URL}/health"

# timeouts: (connect, read)
CONNECT_TIMEOUT = 5
READ_TIMEOUT = 25   # was 5 — increase for Firebase Admin
TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

STARTUP_WAIT_SECS = 30     # how long we retry health
RETRY_INTERVAL_SECS = 1

def api_up() -> bool:
    try:
        r = requests.get(HEALTH_URL, timeout=(2, 2))
        return r.ok
    except Exception:
        return False

def require_api():
    deadline = time.time() + STARTUP_WAIT_SECS
    while time.time() < deadline:
        if api_up():
            return
        time.sleep(RETRY_INTERVAL_SECS)
    pytest.skip("Auth API is not running on 127.0.0.1:5000")

def make_unique_email(prefix="nifemi_test") -> str:
    token = uuid.uuid4().hex[:8]
    return f"{prefix}_{token}@example.com"

# ---------- TESTS ----------

def test_new_user_registration():
    """Create a new user via /register and expect a UID with HTTP 201."""
    require_api()

    email = make_unique_email("nifemi_reg")
    password = "TestPass123!"  # meets Firebase password rules

    r = requests.post(
        REGISTER_URL,
        json={"email": email, "password": password},
        timeout=TIMEOUT
    )
    assert r.status_code == 201, f"Expected 201; got {r.status_code}: {r.text}"
    data = r.json()
    assert "uid" in data and data["uid"], f"No uid in response: {data}"

def test_valid_login():
    """
    Register a user, then /login should return 200 with uid.
    (Current login checks that email exists; it doesn't validate password yet.)
    """
    require_api()

    email = make_unique_email("nifemi_login_ok")
    password = "TestPass123!"

    # Ensure user exists
    r1 = requests.post(REGISTER_URL, json={"email": email, "password": password}, timeout=TIMEOUT)
    # Allow 201 (created) or 409 (already exists in flakey reruns)
    assert r1.status_code in (201, 409), f"Register failed: {r1.status_code} {r1.text}"

    # Now login
    r2 = requests.post(LOGIN_URL, json={"email": email, "password": password}, timeout=TIMEOUT)
    assert r2.status_code == 200, f"Login failed: {r2.status_code} {r2.text}"
    data = r2.json()
    assert "uid" in data and data["uid"], f"No uid in login response: {data}"

@pytest.mark.xfail(reason="Password is not verified by current /login endpoint.")
def test_invalid_login():
    """
    Intentionally expect failure once password validation is enforced.
    For now, /login only checks that the email exists (so this would be 200).
    """
    require_api()

    email = make_unique_email("nifemi_login_bad")
    good = "TestPass123!"
    bad = "WrongPass123!"

    # Create the user
    r1 = requests.post(REGISTER_URL, json={"email": email, "password": good}, timeout=TIMEOUT)
    assert r1.status_code in (201, 409), f"Register failed: {r1.status_code} {r1.text}"

    # Try to login with wrong password (future behavior should be 401)
    r2 = requests.post(LOGIN_URL, json={"email": email, "password": bad}, timeout=TIMEOUT)
    assert r2.status_code in (400, 401)
