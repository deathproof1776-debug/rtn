"""
Test suite for Invite System feature
Tests: invite creation, validation, registration with invite, my-invites list
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://barter-network-2.preview.emergentagent.com')

class TestInviteSystemPublicEndpoints:
    """Tests for public invite endpoints (no auth required)"""
    
    def test_register_without_invite_token_returns_422(self):
        """POST /api/auth/register without invite_token returns 422 (missing field)"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test@test.com",
            "password": "test123",
            "name": "Test User",
            "location": "Test"
        })
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        # Check that the error mentions invite_token is required
        assert any("invite_token" in str(d) for d in data["detail"])
    
    def test_register_with_invalid_invite_token_returns_403(self):
        """POST /api/auth/register with invalid invite_token returns 403"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": "test@test.com",
            "password": "test123",
            "name": "Test User",
            "location": "Test",
            "invite_token": "INVALID_TOKEN_12345"
        })
        assert response.status_code == 403
        data = response.json()
        assert "Invalid or expired invite link" in data["detail"]
    
    def test_validate_invalid_token_returns_404(self):
        """GET /api/invites/validate/{token} with invalid token returns 404"""
        response = requests.get(f"{BASE_URL}/api/invites/validate/INVALID_TOKEN_12345")
        assert response.status_code == 404
        data = response.json()
        assert "Invalid or already used invite link" in data["detail"]


class TestInviteSystemAuthenticatedEndpoints:
    """Tests for authenticated invite endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Login as demo user and return authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return session
    
    def test_create_invite_requires_auth(self):
        """POST /api/invites/create requires authentication"""
        response = requests.post(f"{BASE_URL}/api/invites/create", json={})
        assert response.status_code == 401
    
    def test_create_invite_success(self, auth_session):
        """POST /api/invites/create creates a new invite token"""
        response = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "message" in data
        assert data["message"] == "Invite created successfully"
        assert len(data["token"]) > 20  # Token should be a reasonable length
    
    def test_validate_active_token(self, auth_session):
        """GET /api/invites/validate/{token} validates active tokens correctly"""
        # Create a new invite
        create_response = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        assert create_response.status_code == 200
        token = create_response.json()["token"]
        
        # Validate the token (public endpoint)
        validate_response = requests.get(f"{BASE_URL}/api/invites/validate/{token}")
        assert validate_response.status_code == 200
        data = validate_response.json()
        assert data["valid"] == True
        assert "invited_by" in data
        assert data["invited_by"] == "Demo Trader"
    
    def test_my_invites_requires_auth(self):
        """GET /api/invites/my-invites requires authentication"""
        response = requests.get(f"{BASE_URL}/api/invites/my-invites")
        assert response.status_code == 401
    
    def test_my_invites_returns_list(self, auth_session):
        """GET /api/invites/my-invites returns list of user's invites"""
        response = auth_session.get(f"{BASE_URL}/api/invites/my-invites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least one invite (we created one in previous test)
        if len(data) > 0:
            invite = data[0]
            assert "token" in invite
            assert "used" in invite
            assert "created_at" in invite
            assert "created_by_name" in invite


class TestInviteRegistrationFlow:
    """Tests for the full invite -> registration flow"""
    
    @pytest.fixture
    def auth_session(self):
        """Login as demo user and return authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert response.status_code == 200
        return session
    
    def test_full_invite_registration_flow(self, auth_session):
        """Full flow: create invite -> validate -> register -> invite marked used"""
        # Step 1: Create invite
        create_response = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        assert create_response.status_code == 200
        token = create_response.json()["token"]
        
        # Step 2: Validate invite (public)
        validate_response = requests.get(f"{BASE_URL}/api/invites/validate/{token}")
        assert validate_response.status_code == 200
        assert validate_response.json()["valid"] == True
        
        # Step 3: Register with invite
        unique_email = f"TEST_invite_user_{int(time.time())}@test.com"
        register_response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "TEST Invite User",
            "location": "Test Location",
            "invite_token": token
        })
        assert register_response.status_code == 200
        data = register_response.json()
        assert "id" in data
        assert data["email"] == unique_email.lower()
        assert data["name"] == "TEST Invite User"
        
        # Step 4: Verify invite is now marked as used
        validate_again = requests.get(f"{BASE_URL}/api/invites/validate/{token}")
        assert validate_again.status_code == 404  # Should be invalid now (used)
    
    def test_used_invite_cannot_be_reused(self, auth_session):
        """Trying to use an already-used invite token for registration fails"""
        # Create and use an invite
        create_response = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        token = create_response.json()["token"]
        
        # First registration
        unique_email1 = f"TEST_first_user_{int(time.time())}@test.com"
        register1 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email1,
            "password": "testpass123",
            "name": "TEST First User",
            "location": "Test",
            "invite_token": token
        })
        assert register1.status_code == 200
        
        # Second registration with same token should fail
        unique_email2 = f"TEST_second_user_{int(time.time())}@test.com"
        register2 = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email2,
            "password": "testpass123",
            "name": "TEST Second User",
            "location": "Test",
            "invite_token": token
        })
        assert register2.status_code == 403
        assert "Invalid or expired invite link" in register2.json()["detail"]
    
    def test_my_invites_shows_used_status(self, auth_session):
        """GET /api/invites/my-invites shows used status and used_by_name"""
        # Create and use an invite
        create_response = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        token = create_response.json()["token"]
        
        # Register with invite
        unique_email = f"TEST_status_user_{int(time.time())}@test.com"
        requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "TEST Status User",
            "location": "Test",
            "invite_token": token
        })
        
        # Check my-invites
        invites_response = auth_session.get(f"{BASE_URL}/api/invites/my-invites")
        assert invites_response.status_code == 200
        invites = invites_response.json()
        
        # Find the used invite
        used_invite = next((inv for inv in invites if inv["token"] == token), None)
        assert used_invite is not None
        assert used_invite["used"] == True
        assert used_invite["used_by_name"] == "TEST Status User"


class TestLoginPageNoRegisterLink:
    """Tests to verify login page doesn't have register link"""
    
    def test_login_endpoint_works(self):
        """Login endpoint works with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == "demo@rebeltrade.net"
