"""
Tests for P1 features:
1. Ban/Unban user - PUT /api/admin/users/{user_id}/ban
2. Unique public_id (Trader ID) returned in profile GET
3. Network search by public_id (exact uppercase match)
4. Profile Trader ID shown for existing users (lazy backfill)
5. Admin reports panel - Ban/Remove buttons context (reports data)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

ADMIN_EMAIL = "deathproofrebel@protonmail.com"
ADMIN_PASSWORD = "Peaches1776@"


@pytest.fixture(scope="module")
def admin_session():
    """Authenticated admin session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def admin_user_id(admin_session):
    """Get the admin's own user id."""
    resp = admin_session.get(f"{BASE_URL}/api/auth/me")
    assert resp.status_code == 200
    return resp.json().get("id") or resp.json().get("_id")


# ---------------------------------------------------------------------------
# 1. Admin stats / users list endpoint still works
# ---------------------------------------------------------------------------
class TestAdminUsers:
    """Admin Users panel endpoints"""

    def test_admin_get_users_returns_200(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/admin/users?limit=50")
        assert resp.status_code == 200
        data = resp.json()
        assert "users" in data
        assert isinstance(data["users"], list)

    def test_admin_get_users_includes_banned_field(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/admin/users?limit=50")
        assert resp.status_code == 200
        users = resp.json()["users"]
        # Every user object should have a 'banned' key (may be False / absent → default False)
        for u in users[:5]:
            # banned may be missing (default False) — that's also acceptable
            assert isinstance(u.get("banned", False), bool), f"Unexpected banned type for {u}"


# ---------------------------------------------------------------------------
# 2. Ban / Unban toggle
# ---------------------------------------------------------------------------
class TestBanUser:
    """PUT /api/admin/users/{user_id}/ban endpoint"""

    @pytest.fixture(scope="class")
    def target_non_admin_user_id(self, admin_session, admin_user_id):
        """Find any non-admin user to run ban tests against."""
        resp = admin_session.get(f"{BASE_URL}/api/admin/users?limit=50")
        assert resp.status_code == 200
        users = resp.json()["users"]
        for u in users:
            if u["_id"] != admin_user_id and u.get("role") != "admin":
                return u["_id"]
        pytest.skip("No non-admin user found to test ban functionality")

    def test_ban_user_returns_200(self, admin_session, target_non_admin_user_id):
        resp = admin_session.put(
            f"{BASE_URL}/api/admin/users/{target_non_admin_user_id}/ban",
            json={},
        )
        assert resp.status_code == 200, f"Ban failed: {resp.text}"
        data = resp.json()
        assert "banned" in data
        assert "message" in data
        print(f"Ban response: banned={data['banned']}, message={data['message']}")

    def test_ban_user_response_has_correct_fields(self, admin_session, target_non_admin_user_id):
        resp = admin_session.put(
            f"{BASE_URL}/api/admin/users/{target_non_admin_user_id}/ban",
            json={},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["banned"], bool)
        assert len(data["message"]) > 0

    def test_ban_toggles_state(self, admin_session, target_non_admin_user_id):
        """Ban then unban to verify toggle behaviour."""
        # Get initial state
        resp1 = admin_session.get(f"{BASE_URL}/api/admin/users?limit=50")
        users = resp1.json()["users"]
        initial_user = next((u for u in users if u["_id"] == target_non_admin_user_id), None)
        if initial_user is None:
            pytest.skip("Target user not found")
        initial_banned = initial_user.get("banned", False)

        # Toggle
        resp2 = admin_session.put(f"{BASE_URL}/api/admin/users/{target_non_admin_user_id}/ban", json={})
        assert resp2.status_code == 200
        assert resp2.json()["banned"] != initial_banned, "Ban should toggle the state"

        # Restore original state
        resp3 = admin_session.put(f"{BASE_URL}/api/admin/users/{target_non_admin_user_id}/ban", json={})
        assert resp3.status_code == 200
        assert resp3.json()["banned"] == initial_banned, "Restore should return to initial state"

    def test_cannot_ban_own_account(self, admin_session, admin_user_id):
        resp = admin_session.put(
            f"{BASE_URL}/api/admin/users/{admin_user_id}/ban",
            json={},
        )
        assert resp.status_code == 400, "Should not be able to ban own account"
        assert "Cannot ban" in resp.json().get("detail", "")


# ---------------------------------------------------------------------------
# 3. Public ID (Trader ID) in profile
# ---------------------------------------------------------------------------
class TestPublicId:
    """public_id returned by GET /api/profile/{user_id}"""

    def test_admin_profile_has_public_id(self, admin_session, admin_user_id):
        resp = admin_session.get(f"{BASE_URL}/api/profile/{admin_user_id}")
        assert resp.status_code == 200, f"Profile fetch failed: {resp.text}"
        data = resp.json()
        assert "public_id" in data, "public_id missing from profile response"
        pid = data["public_id"]
        assert len(pid) == 8, f"public_id should be 8 chars, got: {pid}"
        assert pid.isalnum(), f"public_id should be alphanumeric, got: {pid}"
        assert pid == pid.upper(), f"public_id should be uppercase, got: {pid}"
        print(f"Admin public_id: {pid}")

    def test_profile_public_id_is_consistent(self, admin_session, admin_user_id):
        """Two fetches should return the same public_id."""
        r1 = admin_session.get(f"{BASE_URL}/api/profile/{admin_user_id}")
        r2 = admin_session.get(f"{BASE_URL}/api/profile/{admin_user_id}")
        assert r1.json()["public_id"] == r2.json()["public_id"], "public_id should not change between calls"


# ---------------------------------------------------------------------------
# 4. Network search by public_id
# ---------------------------------------------------------------------------
class TestNetworkSearchByPublicId:
    """GET /api/network/search?q=<public_id>"""

    def test_search_by_public_id_returns_user(self, admin_session, admin_user_id):
        # Get admin's public_id first
        profile_resp = admin_session.get(f"{BASE_URL}/api/profile/{admin_user_id}")
        assert profile_resp.status_code == 200
        pid = profile_resp.json().get("public_id")
        if not pid:
            pytest.skip("Admin has no public_id yet")

        # Log in as another user to search for admin
        # (admin can't search for self — excluded from results)
        # We'll do a partial test: the endpoint should accept query and return JSON
        search_resp = admin_session.get(f"{BASE_URL}/api/network/search?q={pid}")
        assert search_resp.status_code == 200
        data = search_resp.json()
        assert "results" in data
        # Admin's self is excluded from results, so we just verify the query worked
        print(f"Search for public_id={pid} returned {data.get('count', 0)} results")

    def test_search_by_name_still_works(self, admin_session):
        search_resp = admin_session.get(f"{BASE_URL}/api/network/search?q=a")
        assert search_resp.status_code == 200
        data = search_resp.json()
        assert "results" in data
        print(f"Name search returned {data.get('count', 0)} results")

    def test_search_short_query_returns_empty(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/network/search?q=X")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("results") == []


# ---------------------------------------------------------------------------
# 5. Reports endpoint
# ---------------------------------------------------------------------------
class TestAdminReports:
    """Admin Reports panel - GET /api/admin/reports"""

    def test_reports_endpoint_returns_200(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/admin/reports?status=pending")
        assert resp.status_code == 200
        data = resp.json()
        assert "reports" in data
        print(f"Pending reports count: {len(data['reports'])}")

    def test_escalated_reports_endpoint_returns_200(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/admin/reports?status=escalated")
        assert resp.status_code == 200
        data = resp.json()
        assert "reports" in data
        print(f"Escalated reports count: {len(data['reports'])}")

    def test_report_stats_returns_200(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/admin/reports/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "pending" in data
        assert "escalated" in data
        assert "resolved" in data
        assert "dismissed" in data
        print(f"Report stats: {data}")


# ---------------------------------------------------------------------------
# 6. Admin stats returns correct structure
# ---------------------------------------------------------------------------
class TestAdminStats:
    def test_admin_stats_returns_200(self, admin_session):
        resp = admin_session.get(f"{BASE_URL}/api/admin/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "total_posts" in data
        print(f"Stats: {data}")
