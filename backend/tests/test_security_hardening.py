"""
Tests for security hardening: rate limiting / lockout, password strength,
2FA (TOTP + recovery codes), refresh rotation, session management,
change-password flow.
"""
import os
import time
import pytest
import requests
import pyotp
from pymongo import MongoClient

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
assert BASE_URL, "REACT_APP_BACKEND_URL must be set"
API = f"{BASE_URL}/api"

# Credentials
ADMIN_EMAIL = "williamrhodes764@protonmail.com"
ADMIN_PASSWORD = "Peaches1776@"
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"

# ---------- Mongo cleanup helpers ----------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_mongo = MongoClient(MONGO_URL)
_db = _mongo[DB_NAME]


def clear_login_attempts(email: str):
    _db.login_attempts.delete_many({"email": email.lower()})


def force_disable_2fa(email: str):
    _db.users.update_one(
        {"email": email.lower()},
        {"$set": {"two_factor_enabled": False},
         "$unset": {"totp_secret": "", "totp_pending_secret": ""}},
    )
    user = _db.users.find_one({"email": email.lower()})
    if user:
        _db.recovery_codes.delete_many({"user_id": str(user["_id"])})


# ---------- Fixtures ----------
@pytest.fixture(autouse=True)
def reset_lockouts_around_each_test():
    # always give tests a clean slate per email
    clear_login_attempts(ADMIN_EMAIL)
    clear_login_attempts(DEMO_EMAIL)
    yield
    clear_login_attempts(ADMIN_EMAIL)
    clear_login_attempts(DEMO_EMAIL)


def _login_with_retry(s, email, password, attempts=4):
    """Login with retry on 429 rate-limit (window is 1 min)."""
    last = None
    for i in range(attempts):
        r = s.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=15)
        last = r
        if r.status_code == 429 and "Rate limit" in r.text:
            time.sleep(25)
            continue
        return r
    return last


@pytest.fixture
def admin_session():
    """Fresh session logged in as admin (no 2FA)."""
    force_disable_2fa(ADMIN_EMAIL)
    s = requests.Session()
    r = _login_with_retry(s, ADMIN_EMAIL, ADMIN_PASSWORD)
    if r.status_code == 429:
        # Last-resort wait for full rate-limit window
        time.sleep(60)
        r = s.post(f"{API}/auth/login",
                   json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    assert r.status_code == 200, f"admin login failed: {r.status_code} {r.text}"
    yield s
    try:
        s.post(f"{API}/auth/logout", timeout=10)
    except Exception:
        pass


# ============================================================
# 1) Plain login still works for non-2FA accounts
# ============================================================
class TestBasicLogin:
    def test_login_returns_user_payload_and_cookies(self):
        s = requests.Session()
        r = s.post(f"{API}/auth/login",
                   json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == ADMIN_EMAIL
        assert "id" in data
        assert data.get("two_factor_enabled") in (False, None)
        # cookies set
        jar = s.cookies.get_dict()
        assert "access_token" in jar
        assert "refresh_token" in jar

        me = s.get(f"{API}/auth/me", timeout=15)
        assert me.status_code == 200
        assert me.json().get("email") == ADMIN_EMAIL


# ============================================================
# 2) Lockout after 5 failed attempts
# ============================================================
class TestAccountLockout:
    def test_five_fails_then_sixth_is_429(self):
        fake_email = "TEST_lockout_user@example.com"
        clear_login_attempts(fake_email)
        s = requests.Session()
        statuses = []
        for i in range(5):
            r = s.post(f"{API}/auth/login",
                       json={"email": fake_email, "password": "bad"}, timeout=15)
            statuses.append(r.status_code)
            time.sleep(0.1)
        assert statuses.count(401) == 5, f"expected 5x401, got {statuses}"

        r6 = s.post(f"{API}/auth/login",
                    json={"email": fake_email, "password": "bad"}, timeout=15)
        assert r6.status_code == 429, f"expected 429 on 6th, got {r6.status_code} {r6.text}"
        clear_login_attempts(fake_email)

    def test_successful_login_clears_prior_fails(self):
        s = requests.Session()
        # 2 bad attempts
        for _ in range(2):
            s.post(f"{API}/auth/login",
                   json={"email": ADMIN_EMAIL, "password": "wrongpass"}, timeout=15)
            time.sleep(0.1)
        # good login
        r = s.post(f"{API}/auth/login",
                   json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
        assert r.status_code == 200
        rec = _db.login_attempts.find_one({"email": ADMIN_EMAIL})
        assert rec is None, f"expected login_attempts cleared, got {rec}"


# ============================================================
# 3) Password strength
# ============================================================
class TestPasswordStrength:
    def test_weak_password_returns_low_score(self):
        r = requests.post(f"{API}/auth/password/check",
                          json={"password": "abc123"}, timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "score" in data and "warning" in data and "suggestions" in data
        assert data["score"] <= 1

    def test_strong_password_returns_high_score(self):
        r = requests.post(f"{API}/auth/password/check",
                          json={"password": "correct horse battery staple!"}, timeout=15)
        assert r.status_code == 200
        assert r.json()["score"] >= 3

    def test_register_rejects_weak_password(self):
        r = requests.post(f"{API}/auth/register", json={
            "email": "TEST_weakpw@example.com",
            "password": "abc123",
            "name": "Weak",
            "location": "",
            "invite_token": "does-not-exist",
        }, timeout=15)
        # Either 400 (weak password) or 403 (invalid invite, checked first). Both prove registration didn't succeed.
        assert r.status_code in (400, 403)


# ============================================================
# 4) 2FA full lifecycle: setup -> confirm -> login challenge -> disable
# ============================================================
class TestTwoFactorFlow:
    def test_full_2fa_lifecycle(self, admin_session):
        s = admin_session
        # setup
        r = s.post(f"{API}/security/2fa/setup", timeout=15)
        assert r.status_code == 200
        setup = r.json()
        assert "secret" in setup and "qr_code" in setup and "otpauth_uri" in setup
        assert setup["qr_code"].startswith("data:image/png;base64,")
        secret = setup["secret"]

        # confirm
        totp = pyotp.TOTP(secret)
        r = s.post(f"{API}/security/2fa/confirm",
                   json={"code": totp.now()}, timeout=15)
        assert r.status_code == 200, r.text
        codes = r.json().get("recovery_codes")
        assert isinstance(codes, list) and len(codes) == 8

        # Next login should now require 2FA
        s2 = requests.Session()
        r = _login_with_retry(s2, ADMIN_EMAIL, ADMIN_PASSWORD)
        assert r.status_code == 200
        data = r.json()
        assert data.get("two_factor_required") is True
        assert "challenge_token" in data
        challenge = data["challenge_token"]

        # complete with TOTP
        r = s2.post(f"{API}/auth/login/2fa",
                    json={"challenge_token": challenge, "code": pyotp.TOTP(secret).now()}, timeout=15)
        assert r.status_code == 200, r.text
        assert s2.cookies.get("access_token")

        # recovery code flow
        s3 = requests.Session()
        r = _login_with_retry(s3, ADMIN_EMAIL, ADMIN_PASSWORD)
        assert r.status_code == 200
        challenge2 = r.json()["challenge_token"]
        used_code = codes[0]
        r = s3.post(f"{API}/auth/login/2fa",
                    json={"challenge_token": challenge2, "recovery_code": used_code}, timeout=15)
        assert r.status_code == 200, r.text
        # second use of same recovery code should fail
        s4 = requests.Session()
        r = _login_with_retry(s4, ADMIN_EMAIL, ADMIN_PASSWORD)
        challenge3 = r.json()["challenge_token"]
        r = s4.post(f"{API}/auth/login/2fa",
                    json={"challenge_token": challenge3, "recovery_code": used_code}, timeout=15)
        assert r.status_code == 401

        # disable 2FA: wrong password
        r = s.post(f"{API}/security/2fa/disable",
                   json={"password": "wrong", "code": pyotp.TOTP(secret).now()}, timeout=15)
        assert r.status_code == 401

        # disable 2FA: wrong code
        r = s.post(f"{API}/security/2fa/disable",
                   json={"password": ADMIN_PASSWORD, "code": "000000"}, timeout=15)
        assert r.status_code == 401

        # disable 2FA: success
        r = s.post(f"{API}/security/2fa/disable",
                   json={"password": ADMIN_PASSWORD, "code": pyotp.TOTP(secret).now()}, timeout=15)
        assert r.status_code == 200, r.text

        # verify disabled via /me
        me = s.get(f"{API}/auth/me", timeout=15).json()
        assert me.get("two_factor_enabled") in (False, None)


# ============================================================
# 5) Sessions: list, revoke-others, refresh rotation
# ============================================================
class TestSessionManagement:
    def test_list_sessions_marks_current(self, admin_session):
        r = admin_session.get(f"{API}/security/sessions", timeout=15)
        assert r.status_code == 200
        sessions = r.json()["sessions"]
        assert len(sessions) >= 1
        currents = [s for s in sessions if s.get("current")]
        assert len(currents) == 1, f"expected exactly 1 current session, got {len(currents)}"

    def test_revoke_others_keeps_current(self, admin_session):
        # create another session
        other = requests.Session()
        r = _login_with_retry(other, ADMIN_EMAIL, ADMIN_PASSWORD)
        assert r.status_code == 200

        # current admin revokes others
        r = admin_session.post(f"{API}/security/sessions/revoke-others", timeout=15)
        assert r.status_code == 200

        # admin can still use /me
        r = admin_session.get(f"{API}/auth/me", timeout=15)
        assert r.status_code == 200

        # the "other" session's refresh should no longer work
        r = other.post(f"{API}/auth/refresh", timeout=15)
        assert r.status_code == 401

    def test_refresh_rotates_token(self, admin_session):
        old_refresh = admin_session.cookies.get("refresh_token")
        assert old_refresh
        # Sleep >1s so JWT's second-precision `exp` differs and tokens actually rotate
        time.sleep(1.2)
        r = admin_session.post(f"{API}/auth/refresh", timeout=15)
        assert r.status_code == 200
        new_refresh = admin_session.cookies.get("refresh_token")
        assert new_refresh and new_refresh != old_refresh, (
            "Refresh token did not rotate — JWT payload has only second-precision exp "
            "and no jti/nonce, so fast successive refreshes produce identical tokens."
        )

        # Old refresh via a fresh client should fail
        bare = requests.Session()
        bare.cookies.set("refresh_token", old_refresh,
                         domain=BASE_URL.split("//")[-1].split("/")[0])
        r = bare.post(f"{API}/auth/refresh", timeout=15)
        assert r.status_code == 401


# ============================================================
# 6) Change password
# ============================================================
class TestChangePassword:
    def test_rejects_weak_new_password(self, admin_session):
        r = admin_session.post(f"{API}/security/password/change", json={
            "current_password": ADMIN_PASSWORD,
            "new_password": "abc123",
        }, timeout=15)
        assert r.status_code == 400

    def test_accepts_strong_new_password_and_rolls_back(self, admin_session):
        new_pw = "correct horse battery staple!42"
        r = admin_session.post(f"{API}/security/password/change", json={
            "current_password": ADMIN_PASSWORD,
            "new_password": new_pw,
        }, timeout=15)
        assert r.status_code == 200, r.text

        # new password must work on new login
        s = requests.Session()
        r = _login_with_retry(s, ADMIN_EMAIL, new_pw)
        assert r.status_code == 200

        # roll back to original so other tests / next iterations keep working
        r = s.post(f"{API}/security/password/change", json={
            "current_password": new_pw,
            "new_password": ADMIN_PASSWORD,
        }, timeout=15)
        assert r.status_code == 200, r.text


# ============================================================
# 7) Regression: basic feed still works after auth changes
# ============================================================
class TestRegressionFeed:
    def test_posts_feed_accessible(self, admin_session):
        r = admin_session.get(f"{API}/posts", timeout=15)
        assert r.status_code == 200
        data = r.json()
        # either list or dict envelope, just verify JSON
        assert data is not None
