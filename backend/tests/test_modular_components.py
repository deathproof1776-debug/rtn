"""
Test suite for modular component verification after frontend refactoring.
Tests: Auth flows, Community Board, Trade Network, Trade Deals, Admin security
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthFlows:
    """Authentication endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.admin_email = "admin@homesteadhub.com"
        self.admin_password = "admin123"
        self.demo_email = "demo@rebeltrade.net"
        self.demo_password = "demo123"
    
    def test_admin_login_success(self):
        """Test admin login returns 200 and sets cookies"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.admin_email,
            "password": self.admin_password
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        # Response returns user data directly (not nested under "user")
        assert "email" in data
        assert data["email"] == self.admin_email
        assert data["role"] == "admin"
        print(f"Admin login successful: {data['email']}")
    
    def test_demo_user_login_success(self):
        """Test demo user login"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.demo_email,
            "password": self.demo_password
        })
        assert response.status_code == 200, f"Demo login failed: {response.text}"
        data = response.json()
        # Response returns user data directly (not nested under "user")
        assert "email" in data
        assert data["email"] == self.demo_email
        print(f"Demo user login successful: {data['email']}")
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password returns 401"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.admin_email,
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("Invalid credentials correctly rejected")
    
    def test_auth_me_without_token(self):
        """Test /auth/me without token returns 401"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("Unauthenticated /auth/me correctly returns 401")
    
    def test_auth_me_with_token(self):
        """Test /auth/me with valid token returns user"""
        # Login first
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": self.admin_email,
            "password": self.admin_password
        })
        assert login_res.status_code == 200
        
        # Get user info
        me_res = self.session.get(f"{BASE_URL}/api/auth/me")
        assert me_res.status_code == 200
        data = me_res.json()
        assert data["email"] == self.admin_email
        print(f"Auth me returned: {data['email']}")


class TestCommunityBoard:
    """Community Board API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login as demo user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        if login_res.status_code != 200:
            pytest.skip("Demo user login failed")
    
    def test_get_community_topics(self):
        """Test fetching community topics"""
        response = self.session.get(f"{BASE_URL}/api/community/topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert len(data["topics"]) > 0
        print(f"Found {len(data['topics'])} community topics")
    
    def test_get_community_posts(self):
        """Test fetching community posts"""
        response = self.session.get(f"{BASE_URL}/api/community")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} community posts")
    
    def test_filter_community_by_topic(self):
        """Test filtering community posts by topic"""
        response = self.session.get(f"{BASE_URL}/api/community?topic=homesteading")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Filtered posts by homesteading: {len(data)} results")
    
    def test_filter_community_by_time_range(self):
        """Test filtering community posts by time range"""
        response = self.session.get(f"{BASE_URL}/api/community?time_range=week")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Filtered posts by week: {len(data)} results")
    
    def test_filter_community_by_sort(self):
        """Test sorting community posts"""
        response = self.session.get(f"{BASE_URL}/api/community?sort_by=popular")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Sorted posts by popular: {len(data)} results")
    
    def test_create_community_post(self):
        """Test creating a community post"""
        response = self.session.post(f"{BASE_URL}/api/community", json={
            "title": "TEST_Modular Component Test Post",
            "content": "Testing the modular component refactoring",
            "topic": "general"
        })
        assert response.status_code in [200, 201], f"Create post failed: {response.text}"
        data = response.json()
        # Response returns {id, message} on success
        assert "id" in data or "message" in data
        print(f"Created community post successfully: {data}")


class TestTradeNetwork:
    """Trade Network API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login as demo user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        if login_res.status_code != 200:
            pytest.skip("Demo user login failed")
    
    def test_get_connections(self):
        """Test fetching network connections"""
        response = self.session.get(f"{BASE_URL}/api/network/connections")
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        print(f"Found {len(data['connections'])} connections")
    
    def test_get_pending_requests(self):
        """Test fetching pending network requests"""
        response = self.session.get(f"{BASE_URL}/api/network/requests/pending")
        assert response.status_code == 200
        data = response.json()
        assert "incoming" in data
        assert "outgoing" in data
        print(f"Pending requests - incoming: {len(data['incoming'])}, outgoing: {len(data['outgoing'])}")
    
    def test_get_recommended_traders(self):
        """Test fetching recommended traders"""
        response = self.session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        print(f"Found {len(data['recommendations'])} recommended traders")


class TestTradeDeals:
    """Trade Deals API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login as demo user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        if login_res.status_code != 200:
            pytest.skip("Demo user login failed")
    
    def test_get_incoming_trades(self):
        """Test fetching incoming trade offers"""
        response = self.session.get(f"{BASE_URL}/api/trades/incoming")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} incoming trades")
    
    def test_get_outgoing_trades(self):
        """Test fetching outgoing trade offers"""
        response = self.session.get(f"{BASE_URL}/api/trades/outgoing")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} outgoing trades")
    
    def test_get_trade_history(self):
        """Test fetching trade history"""
        response = self.session.get(f"{BASE_URL}/api/trades/history")
        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert "total" in data
        print(f"Trade history: {data['total']} total trades")
    
    def test_get_active_trade_count(self):
        """Test fetching active trade count"""
        response = self.session.get(f"{BASE_URL}/api/trades/active-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        print(f"Active trade count: {data['count']}")


class TestSystemAnnouncements:
    """System announcements/banner tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login as demo user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        if login_res.status_code != 200:
            pytest.skip("Demo user login failed")
    
    def test_get_active_system_messages(self):
        """Test fetching active system messages"""
        response = self.session.get(f"{BASE_URL}/api/admin/system-messages/active")
        assert response.status_code == 200
        data = response.json()
        # Response returns {messages: [...]}
        assert "messages" in data
        assert isinstance(data["messages"], list)
        print(f"Found {len(data['messages'])} active system messages")


class TestAdminSecurity:
    """Admin endpoint security tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
    
    def test_admin_endpoints_require_auth(self):
        """Test admin endpoints require authentication"""
        # Try without auth
        response = requests.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 401, "Admin endpoint should require auth"
        print("Admin /users endpoint correctly requires auth")
    
    def test_admin_endpoints_require_admin_role(self):
        """Test admin endpoints require admin role"""
        # Login as demo user (non-admin)
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert login_res.status_code == 200
        
        # Try to access admin endpoint
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 403, f"Non-admin should get 403, got {response.status_code}"
        print("Admin endpoint correctly rejects non-admin user")
    
    def test_admin_can_access_admin_endpoints(self):
        """Test admin user can access admin endpoints"""
        # Login as admin
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        assert login_res.status_code == 200
        
        # Access admin endpoint
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"Admin should access /admin/users, got {response.status_code}"
        data = response.json()
        # Response returns {users: [...], total: N}
        assert "users" in data
        assert isinstance(data["users"], list)
        print(f"Admin accessed /admin/users: {len(data['users'])} users")


class TestBarterFeed:
    """Barter Feed (posts) API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login as demo user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        if login_res.status_code != 200:
            pytest.skip("Demo user login failed")
    
    def test_get_posts(self):
        """Test fetching barter posts"""
        response = self.session.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} barter posts")
    
    def test_filter_posts_by_time_range(self):
        """Test filtering posts by time range"""
        response = self.session.get(f"{BASE_URL}/api/posts?time_range=week")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Filtered posts by week: {len(data)} results")
    
    def test_filter_posts_by_has_media(self):
        """Test filtering posts by has_media"""
        response = self.session.get(f"{BASE_URL}/api/posts?has_media=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Filtered posts with media: {len(data)} results")
    
    def test_sort_posts_by_popular(self):
        """Test sorting posts by popular"""
        response = self.session.get(f"{BASE_URL}/api/posts?sort_by=popular")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Sorted posts by popular: {len(data)} results")


class TestGallery:
    """Gallery API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        # Login as demo user
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        if login_res.status_code != 200:
            pytest.skip("Demo user login failed")
    
    def test_get_gallery(self):
        """Test fetching gallery items"""
        response = self.session.get(f"{BASE_URL}/api/gallery")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} gallery items")


class TestProtectedEndpoints:
    """Test that protected endpoints require authentication"""
    
    def test_posts_require_auth(self):
        """Test posts endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 401
        print("Posts endpoint correctly requires auth")
    
    def test_community_requires_auth(self):
        """Test community endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/community")
        assert response.status_code == 401
        print("Community endpoint correctly requires auth")
    
    def test_network_requires_auth(self):
        """Test network endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/network/connections")
        assert response.status_code == 401
        print("Network endpoint correctly requires auth")
    
    def test_trades_require_auth(self):
        """Test trades endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/trades/incoming")
        assert response.status_code == 401
        print("Trades endpoint correctly requires auth")
    
    def test_gallery_requires_auth(self):
        """Test gallery endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/gallery")
        assert response.status_code == 401
        print("Gallery endpoint correctly requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
