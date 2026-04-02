"""
Test Admin Dashboard API Endpoints
Tests: admin stats, admin posts, admin users, role management, user deletion
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "demo@rebeltrade.net"
ADMIN_PASSWORD = "demo123"
REGULAR_USER_EMAIL = "sarah.meadow@example.com"
REGULAR_USER_PASSWORD = "homestead123"


class TestAdminAuth:
    """Test admin authentication and access control"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    @pytest.fixture(scope="class")
    def regular_session(self):
        """Get authenticated regular user session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Regular user login failed: {response.text}")
        return session
    
    def test_admin_login_returns_admin_role(self, admin_session):
        """Verify admin user has role=admin in auth response"""
        response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "admin", f"Expected role=admin, got {data.get('role')}"
        print(f"PASS: Admin user {data.get('email')} has role=admin")
    
    def test_regular_user_not_admin(self, regular_session):
        """Verify regular user does not have admin role"""
        response = regular_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") != "admin", f"Regular user should not have admin role"
        print(f"PASS: Regular user {data.get('email')} has role={data.get('role')}")


class TestAdminStats:
    """Test GET /api/admin/stats endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    @pytest.fixture(scope="class")
    def regular_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Regular user login failed: {response.text}")
        return session
    
    def test_admin_stats_success(self, admin_session):
        """Admin can access platform stats"""
        response = admin_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify all expected stat fields are present
        expected_fields = [
            "total_users", "verified_users", "total_posts", 
            "total_messages", "total_connections", "pending_requests",
            "total_invites", "used_invites", "new_users_week", "new_posts_week"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], int), f"Field {field} should be int, got {type(data[field])}"
        
        print(f"PASS: Admin stats returned all fields: {data}")
    
    def test_admin_stats_forbidden_for_regular_user(self, regular_session):
        """Regular user cannot access admin stats"""
        response = regular_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("PASS: Regular user blocked from admin stats (403)")


class TestAdminPosts:
    """Test admin posts management endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    @pytest.fixture(scope="class")
    def regular_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Regular user login failed: {response.text}")
        return session
    
    def test_admin_get_posts_success(self, admin_session):
        """Admin can get all posts"""
        response = admin_session.get(f"{BASE_URL}/api/admin/posts")
        assert response.status_code == 200
        data = response.json()
        
        assert "posts" in data, "Response should have 'posts' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["posts"], list), "posts should be a list"
        assert isinstance(data["total"], int), "total should be int"
        
        # Verify post structure if posts exist
        if data["posts"]:
            post = data["posts"][0]
            assert "_id" in post, "Post should have _id"
            assert "title" in post, "Post should have title"
            assert "user_name" in post, "Post should have user_name"
            assert "category" in post, "Post should have category"
        
        print(f"PASS: Admin posts returned {len(data['posts'])} posts, total={data['total']}")
    
    def test_admin_posts_forbidden_for_regular_user(self, regular_session):
        """Regular user cannot access admin posts"""
        response = regular_session.get(f"{BASE_URL}/api/admin/posts")
        assert response.status_code == 403
        print("PASS: Regular user blocked from admin posts (403)")


class TestAdminUsers:
    """Test admin user management endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    @pytest.fixture(scope="class")
    def regular_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": REGULAR_USER_EMAIL,
            "password": REGULAR_USER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Regular user login failed: {response.text}")
        return session
    
    def test_admin_get_users_success(self, admin_session):
        """Admin can get all users"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data, "Response should have 'users' field"
        assert "total" in data, "Response should have 'total' field"
        assert isinstance(data["users"], list), "users should be a list"
        
        # Verify user structure
        if data["users"]:
            user = data["users"][0]
            assert "_id" in user, "User should have _id"
            assert "email" in user, "User should have email"
            assert "name" in user, "User should have name"
            assert "password_hash" not in user, "Password hash should not be exposed"
        
        print(f"PASS: Admin users returned {len(data['users'])} users, total={data['total']}")
    
    def test_admin_users_forbidden_for_regular_user(self, regular_session):
        """Regular user cannot access admin users"""
        response = regular_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 403
        print("PASS: Regular user blocked from admin users (403)")


class TestAdminVerifyTrader:
    """Test admin verify/unverify trader endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    def test_admin_verify_trader(self, admin_session):
        """Admin can verify a trader"""
        # First get a user to verify
        users_response = admin_session.get(f"{BASE_URL}/api/admin/users")
        assert users_response.status_code == 200
        users = users_response.json()["users"]
        
        # Find a non-admin user to test with
        test_user = None
        for u in users:
            if u.get("role") != "admin" and u.get("email") != ADMIN_EMAIL:
                test_user = u
                break
        
        if not test_user:
            pytest.skip("No non-admin user found to test verification")
        
        user_id = test_user["_id"]
        original_verified = test_user.get("is_verified", False)
        
        # Toggle verification
        response = admin_session.post(f"{BASE_URL}/api/admin/verify-trader", json={
            "user_id": user_id,
            "is_verified": not original_verified
        })
        assert response.status_code == 200
        data = response.json()
        assert data["is_verified"] == (not original_verified)
        
        # Restore original state
        admin_session.post(f"{BASE_URL}/api/admin/verify-trader", json={
            "user_id": user_id,
            "is_verified": original_verified
        })
        
        print(f"PASS: Admin can verify/unverify trader {user_id}")


class TestAdminRoleChange:
    """Test admin role change endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    def test_admin_change_role_invalid_role(self, admin_session):
        """Admin cannot set invalid role"""
        # Get a user
        users_response = admin_session.get(f"{BASE_URL}/api/admin/users")
        users = users_response.json()["users"]
        test_user = users[0]
        
        response = admin_session.put(f"{BASE_URL}/api/admin/users/{test_user['_id']}/role", json={
            "role": "superadmin"  # Invalid role
        })
        assert response.status_code == 400
        print("PASS: Invalid role rejected with 400")
    
    def test_admin_change_role_user_not_found(self, admin_session):
        """Admin gets 404 for non-existent user"""
        fake_id = "000000000000000000000000"
        response = admin_session.put(f"{BASE_URL}/api/admin/users/{fake_id}/role", json={
            "role": "admin"
        })
        assert response.status_code == 404
        print("PASS: Non-existent user returns 404")


class TestAdminDeletePost:
    """Test admin delete post endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    def test_admin_delete_post_not_found(self, admin_session):
        """Admin gets 404 for non-existent post"""
        fake_id = "000000000000000000000000"
        response = admin_session.delete(f"{BASE_URL}/api/admin/posts/{fake_id}")
        assert response.status_code == 404
        print("PASS: Non-existent post returns 404")


class TestAdminDeleteUser:
    """Test admin delete user endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip(f"Admin login failed: {response.text}")
        return session
    
    def test_admin_cannot_delete_self(self, admin_session):
        """Admin cannot delete their own account"""
        # Get current admin user ID
        me_response = admin_session.get(f"{BASE_URL}/api/auth/me")
        admin_id = me_response.json()["id"]
        
        response = admin_session.delete(f"{BASE_URL}/api/admin/users/{admin_id}")
        assert response.status_code == 400
        print("PASS: Admin cannot delete self (400)")
    
    def test_admin_delete_user_not_found(self, admin_session):
        """Admin gets 404 for non-existent user"""
        fake_id = "000000000000000000000000"
        response = admin_session.delete(f"{BASE_URL}/api/admin/users/{fake_id}")
        assert response.status_code == 404
        print("PASS: Non-existent user returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
