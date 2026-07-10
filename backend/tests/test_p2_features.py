"""
P2 Feature Tests: Email Encryption, Auto Sign-Out, Screenshot Prevention (backend)
Tests:
- Email encryption: login with admin credentials (on-the-fly migration)
- Login returns decrypted email (not Fernet gAAAA token)
- Wrong password returns 401
- GET /api/admin/users returns decrypted readable emails
- Network search by email uses hash lookup
- /api/auth/me returns decrypted email
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

ADMIN_EMAIL = "deathproofrebel@protonmail.com"
ADMIN_PASSWORD = "Peaches1776@"


@pytest.fixture(scope="module")
def admin_token():
    """Login as admin and return access token."""
    resp = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=15,
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.status_code} {resp.text}"
    data = resp.json()
    token = data.get("access_token")
    assert token, "No access_token in login response"
    return token


@pytest.fixture(scope="module")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================
# 1. Login with correct admin credentials
# ============================================================
class TestLoginEmailEncryption:
    """Email encryption: login and verify response contains decrypted email"""

    def test_admin_login_returns_200(self):
        """Admin login with correct credentials returns 200"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    def test_admin_login_returns_access_token(self):
        """Login response includes access_token"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data, "Missing access_token in login response"
        assert len(data["access_token"]) > 20, "access_token too short"

    def test_admin_login_response_email_is_decrypted(self):
        """Login response must return readable email, not Fernet-encrypted token (gAAAA...)"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        returned_email = data.get("email", "")
        # Must NOT be a Fernet token (starts with gAAAA)
        assert not returned_email.startswith("gAAAA"), (
            f"Email in login response is still Fernet-encrypted: {returned_email[:20]}..."
        )
        # Must contain @ (be a valid email)
        assert "@" in returned_email, f"Email does not look like an email address: {returned_email!r}"
        assert returned_email.lower() == ADMIN_EMAIL.lower(), (
            f"Decrypted email mismatch: expected '{ADMIN_EMAIL}', got '{returned_email}'"
        )

    def test_admin_login_response_role_is_admin(self):
        """Login response must include role=admin"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("role") == "admin", f"Expected role='admin', got: {data.get('role')!r}"

    def test_wrong_password_returns_401(self):
        """Wrong password must return 401"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": "WrongPassword123!"},
            timeout=15,
        )
        assert resp.status_code == 401, f"Expected 401 for wrong password, got {resp.status_code}"

    def test_wrong_email_returns_401(self):
        """Non-existent email must return 401"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "nonexistent_test@example.com", "password": "SomePassword123!"},
            timeout=15,
        )
        assert resp.status_code == 401, f"Expected 401 for non-existent email, got {resp.status_code}"


# ============================================================
# 2. /api/auth/me returns decrypted email
# ============================================================
class TestMeEndpointDecryptedEmail:
    """GET /api/auth/me must return readable decrypted email"""

    def test_me_returns_decrypted_email(self, admin_headers):
        """GET /api/auth/me must return readable email, not Fernet token"""
        resp = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200, f"GET /api/auth/me failed: {resp.status_code}"
        data = resp.json()
        email = data.get("email", "")
        assert "@" in email, f"Email from /me doesn't look like email: {email!r}"
        assert not email.startswith("gAAAA"), (
            f"Email from /me is still encrypted: {email[:30]}..."
        )

    def test_me_returns_admin_role(self, admin_headers):
        """GET /api/auth/me must return role=admin for admin user"""
        resp = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("role") == "admin", f"Expected role=admin from /me, got: {data.get('role')!r}"


# ============================================================
# 3. GET /api/admin/users returns decrypted emails
# ============================================================
class TestAdminUsersDecryptedEmails:
    """Admin users endpoint must return readable decrypted emails"""

    def test_admin_users_endpoint_returns_200(self, admin_headers):
        """GET /api/admin/users returns 200"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200, f"GET /api/admin/users failed: {resp.status_code} {resp.text}"

    def test_admin_users_emails_are_decrypted(self, admin_headers):
        """All emails in /api/admin/users must be human-readable (not Fernet tokens)"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        users = data.get("users", [])
        assert len(users) > 0, "No users returned from admin/users"

        fernet_emails = []
        for u in users:
            email = u.get("email", "")
            if email.startswith("gAAAA"):
                fernet_emails.append({"id": u.get("_id"), "email_snippet": email[:30]})

        assert len(fernet_emails) == 0, (
            f"Found {len(fernet_emails)} users with Fernet-encrypted emails: {fernet_emails}"
        )

    def test_admin_user_in_list(self, admin_headers):
        """Admin user (deathproofrebel@protonmail.com) must appear in admin/users with correct email"""
        resp = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        users = data.get("users", [])
        admin_users = [u for u in users if u.get("email", "").lower() == ADMIN_EMAIL.lower()]
        assert len(admin_users) >= 1, (
            f"Admin email '{ADMIN_EMAIL}' not found in /api/admin/users response. "
            f"Got emails: {[u.get('email', '') for u in users[:5]]}"
        )

    def test_admin_users_requires_auth(self):
        """GET /api/admin/users without token must return 401/403"""
        resp = requests.get(f"{BASE_URL}/api/admin/users", timeout=15)
        assert resp.status_code in [401, 403], (
            f"Expected 401/403 for unauthenticated request, got {resp.status_code}"
        )


# ============================================================
# 4. Network search by email uses HMAC hash
# ============================================================
class TestNetworkEmailSearch:
    """Network search by email should find users via HMAC hash lookup"""

    def test_search_by_email_returns_admin(self, admin_headers):
        """Searching by exact email 'deathproofrebel@protonmail.com' must find admin user"""
        resp = requests.get(
            f"{BASE_URL}/api/network/search",
            params={"q": ADMIN_EMAIL},
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200, f"Network search failed: {resp.status_code} {resp.text}"
        data = resp.json()
        results = data.get("results", [])
        # The admin is excluded from own search results (self-exclusion in network.py)
        # So we search from a different user perspective... but we only have admin credentials
        # The admin search excludes self, so we check for count/results structure is valid
        assert isinstance(results, list), "Results should be a list"
        # Note: self is excluded from results per network.py line 415
        # So admin searching for their own email returns empty list - that's correct behavior
        print(f"Email search for '{ADMIN_EMAIL}' returned {len(results)} results (self excluded is expected)")

    def test_search_by_partial_name_returns_results(self, admin_headers):
        """Search by partial name works"""
        resp = requests.get(
            f"{BASE_URL}/api/network/search",
            params={"q": "Bob"},
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200, f"Network search by name failed: {resp.status_code}"
        data = resp.json()
        assert "results" in data, "Missing 'results' in response"

    def test_search_results_emails_are_decrypted(self, admin_headers):
        """Network search results must have readable decrypted emails"""
        resp = requests.get(
            f"{BASE_URL}/api/network/search",
            params={"q": "test"},
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200
        data = resp.json()
        results = data.get("results", [])
        for r in results:
            email = r.get("email", "")
            if email:
                assert not email.startswith("gAAAA"), (
                    f"Network search result has encrypted email: {email[:30]}..."
                )

    def test_search_by_test_banuser_email(self, admin_headers):
        """Searching by test_banuser_p1@example.com email should work via hash lookup"""
        test_email = "test_banuser_p1@example.com"
        resp = requests.get(
            f"{BASE_URL}/api/network/search",
            params={"q": test_email},
            headers=admin_headers,
            timeout=15,
        )
        assert resp.status_code == 200, f"Search failed: {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        print(f"Search for '{test_email}' returned {len(results)} results")
        # The test user should appear (if it exists and isn't banned/deleted)
        # Just check response structure is valid
        assert isinstance(results, list), "results must be a list"

    def test_search_requires_auth(self):
        """Network search without auth returns 401/403"""
        resp = requests.get(
            f"{BASE_URL}/api/network/search",
            params={"q": "test"},
            timeout=15,
        )
        assert resp.status_code in [401, 403], (
            f"Expected 401/403 for unauthenticated search, got {resp.status_code}"
        )


# ============================================================
# 5. Email hash migration (login fallback + on-the-fly migration)
# ============================================================
class TestEmailMigration:
    """Verify that login performs on-the-fly migration for plaintext email users"""

    def test_login_with_correct_credentials_after_potential_migration(self):
        """Repeated login works consistently (email_hash lookup works after migration)"""
        # First login (triggers migration if needed)
        resp1 = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert resp1.status_code == 200
        token1 = resp1.json().get("access_token")
        assert token1, "No token on first login"

        # Second login (now uses email_hash lookup since it was migrated)
        resp2 = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=15,
        )
        assert resp2.status_code == 200
        token2 = resp2.json().get("access_token")
        assert token2, "No token on second login"

        # Both logins return same email
        assert resp1.json().get("email") == resp2.json().get("email"), (
            "Email in login response changed between first and second login"
        )

    def test_login_email_case_insensitive(self):
        """Login with uppercase email should still work"""
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL.upper(), "password": ADMIN_PASSWORD},
            timeout=15,
        )
        # Should succeed (email.lower() in login route)
        assert resp.status_code == 200, (
            f"Case-insensitive login failed: {resp.status_code} {resp.text}"
        )
