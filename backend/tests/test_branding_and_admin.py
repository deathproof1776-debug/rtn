"""
Test suite for Rebel Trade Network - Branding and Admin Features
Tests:
1. Login endpoint returns is_verified and role fields
2. Admin verify-trader endpoint
3. Admin users list endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLoginResponse:
    """Test login endpoint returns is_verified and role fields"""
    
    def test_login_returns_verification_fields(self):
        """Test that login response includes is_verified and role"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@homesteadhub.com",
                "password": "admin123"
            }
        )
        
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        
        # Verify required fields exist
        assert "is_verified" in data, "is_verified field missing from login response"
        assert "role" in data, "role field missing from login response"
        assert "id" in data, "id field missing from login response"
        assert "email" in data, "email field missing from login response"
        assert "name" in data, "name field missing from login response"
        
        # Verify admin user has correct values
        assert data["role"] == "admin", f"Expected role 'admin', got '{data['role']}'"
        assert data["is_verified"] == True, f"Expected is_verified True, got {data['is_verified']}"
        
        print(f"Login response: {data}")
        return response.cookies


class TestAdminEndpoints:
    """Test admin endpoints for user verification"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@homesteadhub.com",
                "password": "admin123"
            }
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    def test_admin_get_users(self, admin_session):
        """Test GET /api/admin/users returns user list with verification status"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users")
        
        assert response.status_code == 200, f"Admin users endpoint failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "users" in data, "users field missing from response"
        assert "total" in data, "total field missing from response"
        assert isinstance(data["users"], list), "users should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        
        # Check that users have verification fields
        if len(data["users"]) > 0:
            user = data["users"][0]
            # These fields should exist (may be None/False for non-verified users)
            assert "_id" in user, "_id field missing from user"
            assert "email" in user, "email field missing from user"
            print(f"Found {data['total']} users")
            print(f"First user: {user.get('email')}, verified: {user.get('is_verified')}, role: {user.get('role')}")
    
    def test_admin_users_requires_auth(self):
        """Test that admin users endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_admin_verify_trader_requires_admin_role(self):
        """Test that verify-trader endpoint requires admin role"""
        # First, create a regular user session (if possible)
        # For now, test without auth
        response = requests.post(
            f"{BASE_URL}/api/admin/verify-trader",
            json={"user_id": "test123", "is_verified": True}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_admin_verify_trader_invalid_user(self, admin_session):
        """Test verify-trader with invalid user ID"""
        response = admin_session.post(
            f"{BASE_URL}/api/admin/verify-trader",
            json={"user_id": "000000000000000000000000", "is_verified": True}
        )
        assert response.status_code == 404, f"Expected 404 for invalid user, got {response.status_code}"


class TestAuthMe:
    """Test /api/auth/me endpoint returns verification fields"""
    
    def test_auth_me_returns_verification_fields(self):
        """Test that /api/auth/me returns is_verified and role"""
        session = requests.Session()
        
        # Login first
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@homesteadhub.com",
                "password": "admin123"
            }
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        # Get current user
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200, f"Auth/me failed: {me_response.text}"
        
        data = me_response.json()
        assert "is_verified" in data, "is_verified field missing from /auth/me response"
        assert "role" in data, "role field missing from /auth/me response"
        
        print(f"Auth/me response: email={data.get('email')}, is_verified={data.get('is_verified')}, role={data.get('role')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
