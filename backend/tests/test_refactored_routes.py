"""
Test suite for refactored modular routes in Rebel Trade Network.
Tests all API endpoints after backend refactoring from monolithic server.py to modular routes.
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@homesteadhub.com"
ADMIN_PASSWORD = "admin123"
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"


class TestAPIRoot:
    """Test API root endpoint"""
    
    def test_api_root_returns_status(self):
        """API root should return running status"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "Rebel Trade Network" in data["message"]
        print("✓ API root endpoint working")


class TestAuthRoutes:
    """Test /api/auth/* endpoints"""
    
    def test_login_with_admin_credentials(self):
        """Login with admin credentials should succeed"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == ADMIN_EMAIL
        assert data["message"] == "Login successful"
        print(f"✓ Admin login successful - ID: {data['id']}")
    
    def test_login_with_demo_credentials(self):
        """Login with demo credentials should succeed"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == DEMO_EMAIL
        print(f"✓ Demo login successful - ID: {data['id']}")
    
    def test_login_with_invalid_credentials(self):
        """Login with invalid credentials should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")
    
    def test_get_me_requires_auth(self):
        """GET /api/auth/me should require authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ /api/auth/me correctly requires authentication")
    
    def test_get_me_with_auth(self):
        """GET /api/auth/me should return user data when authenticated"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_resp.status_code == 200
        
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["email"] == DEMO_EMAIL
        assert "id" in data
        print(f"✓ /api/auth/me returns user data - Name: {data.get('name', 'N/A')}")
    
    def test_logout(self):
        """POST /api/auth/logout should clear session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        
        logout_resp = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_resp.status_code == 200
        assert logout_resp.json()["message"] == "Logged out successfully"
        print("✓ Logout successful")


class TestPostsRoutes:
    """Test /api/posts/* endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_posts_requires_auth(self):
        """GET /api/posts should require authentication"""
        response = requests.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 401
        print("✓ /api/posts correctly requires authentication")
    
    def test_get_posts_with_auth(self, auth_session):
        """GET /api/posts should return posts when authenticated"""
        response = auth_session.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ /api/posts returns {len(data)} posts")
    
    def test_create_post(self, auth_session):
        """POST /api/posts should create a new post"""
        test_post = {
            "title": f"TEST_Post_{uuid.uuid4().hex[:8]}",
            "description": "Test post description for refactoring test",
            "category": "goods",
            "offering": ["Test Item 1"],
            "looking_for": ["Test Item 2"],
            "images": []
        }
        response = auth_session.post(f"{BASE_URL}/api/posts", json=test_post)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["message"] == "Post created successfully"
        print(f"✓ Post created - ID: {data['id']}")
        return data["id"]
    
    def test_like_post(self, auth_session):
        """POST /api/posts/{id}/like should toggle like"""
        # First get a post
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if len(posts) > 0:
            post_id = posts[0]["_id"]
            response = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/like")
            assert response.status_code == 200
            assert "message" in response.json()
            print(f"✓ Like toggled on post {post_id}")
        else:
            pytest.skip("No posts available to like")
    
    def test_get_matched_posts(self, auth_session):
        """GET /api/posts/matches should return matched posts"""
        response = auth_session.get(f"{BASE_URL}/api/posts/matches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ /api/posts/matches returns {len(data)} matched posts")


class TestNetworkRoutes:
    """Test /api/network/* endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_connections(self, auth_session):
        """GET /api/network/connections should return connections"""
        response = auth_session.get(f"{BASE_URL}/api/network/connections")
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        assert "count" in data
        print(f"✓ /api/network/connections returns {data['count']} connections")
    
    def test_get_pending_requests(self, auth_session):
        """GET /api/network/requests/pending should return pending requests"""
        response = auth_session.get(f"{BASE_URL}/api/network/requests/pending")
        assert response.status_code == 200
        data = response.json()
        assert "incoming" in data
        assert "outgoing" in data
        print(f"✓ /api/network/requests/pending - Incoming: {len(data['incoming'])}, Outgoing: {len(data['outgoing'])}")
    
    def test_get_recommended_traders(self, auth_session):
        """GET /api/network/recommended should return recommendations"""
        response = auth_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data or "message" in data
        print(f"✓ /api/network/recommended returns data")


class TestTradesRoutes:
    """Test /api/trades/* endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_incoming_trades(self, auth_session):
        """GET /api/trades/incoming should return incoming trades"""
        response = auth_session.get(f"{BASE_URL}/api/trades/incoming")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ /api/trades/incoming returns {len(data)} trades")
    
    def test_get_outgoing_trades(self, auth_session):
        """GET /api/trades/outgoing should return outgoing trades"""
        response = auth_session.get(f"{BASE_URL}/api/trades/outgoing")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ /api/trades/outgoing returns {len(data)} trades")
    
    def test_get_trade_history(self, auth_session):
        """GET /api/trades/history should return trade history"""
        response = auth_session.get(f"{BASE_URL}/api/trades/history")
        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert "total" in data
        print(f"✓ /api/trades/history returns {data['total']} total trades")
    
    def test_get_active_trade_count(self, auth_session):
        """GET /api/trades/active-count should return count"""
        response = auth_session.get(f"{BASE_URL}/api/trades/active-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        print(f"✓ /api/trades/active-count returns {data['count']}")


class TestGalleryRoutes:
    """Test /api/gallery/* endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_gallery(self, auth_session):
        """GET /api/gallery should return gallery items"""
        response = auth_session.get(f"{BASE_URL}/api/gallery")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ /api/gallery returns {len(data)} items")


class TestCategoriesRoutes:
    """Test /api/categories/* endpoints - these are public"""
    
    def test_get_goods_categories(self):
        """GET /api/categories/goods should return goods categories"""
        response = requests.get(f"{BASE_URL}/api/categories/goods")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ /api/categories/goods returns {len(data['categories'])} categories")
    
    def test_get_skills_categories(self):
        """GET /api/categories/skills should return skills categories"""
        response = requests.get(f"{BASE_URL}/api/categories/skills")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ /api/categories/skills returns {len(data['categories'])} categories")
    
    def test_get_services_categories(self):
        """GET /api/categories/services should return services categories"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ /api/categories/services returns {len(data['categories'])} categories")
    
    def test_get_all_categories(self):
        """GET /api/categories/all should return all categories"""
        response = requests.get(f"{BASE_URL}/api/categories/all")
        assert response.status_code == 200
        data = response.json()
        assert "goods" in data
        assert "skills" in data
        assert "services" in data
        print("✓ /api/categories/all returns all category types")


class TestProfileRoutes:
    """Test profile endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        session.user_id = resp.json().get("id")
        return session
    
    def test_get_profile(self, auth_session):
        """GET /api/profile/{user_id} should return user profile"""
        user_id = auth_session.user_id
        response = auth_session.get(f"{BASE_URL}/api/profile/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == DEMO_EMAIL
        print(f"✓ /api/profile/{user_id} returns profile data")
    
    def test_update_profile(self, auth_session):
        """PUT /api/profile should update profile"""
        response = auth_session.put(f"{BASE_URL}/api/profile", json={
            "bio": f"Test bio updated at {uuid.uuid4().hex[:8]}"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Profile updated successfully"
        print("✓ PUT /api/profile updates profile")


class TestInvitesRoutes:
    """Test /api/invites/* endpoints"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_create_invite(self, auth_session):
        """POST /api/invites/create should create an invite"""
        response = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["message"] == "Invite created successfully"
        print(f"✓ Invite created - Token: {data['token'][:20]}...")
        return data["token"]
    
    def test_validate_invite(self, auth_session):
        """GET /api/invites/validate/{token} should validate invite"""
        # First create an invite
        create_resp = auth_session.post(f"{BASE_URL}/api/invites/create", json={})
        token = create_resp.json()["token"]
        
        # Validate it (public endpoint)
        response = requests.get(f"{BASE_URL}/api/invites/validate/{token}")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        print("✓ Invite validation working")
    
    def test_get_my_invites(self, auth_session):
        """GET /api/invites/my-invites should return user's invites"""
        response = auth_session.get(f"{BASE_URL}/api/invites/my-invites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ /api/invites/my-invites returns {len(data)} invites")


class TestAdminRoutes:
    """Test /api/admin/* endpoints"""
    
    @pytest.fixture
    def admin_session(self):
        """Create admin authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture
    def user_session(self):
        """Create regular user session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_admin_stats(self, admin_session):
        """GET /api/admin/stats should return platform stats"""
        response = admin_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_posts" in data
        print(f"✓ Admin stats - Users: {data['total_users']}, Posts: {data['total_posts']}")
    
    def test_admin_stats_requires_admin(self, user_session):
        """GET /api/admin/stats should require admin role"""
        response = user_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 403
        print("✓ Admin stats correctly requires admin role")
    
    def test_admin_users(self, admin_session):
        """GET /api/admin/users should return all users"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        print(f"✓ Admin users - Total: {data['total']}")
    
    def test_admin_posts(self, admin_session):
        """GET /api/admin/posts should return all posts"""
        response = admin_session.get(f"{BASE_URL}/api/admin/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
        print(f"✓ Admin posts - Total: {data['total']}")
    
    def test_admin_audit_log(self, admin_session):
        """GET /api/admin/audit-log should return audit log"""
        response = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        print(f"✓ Admin audit log - Total: {data['total']}")


class TestCommentsRoutes:
    """Test comments on posts"""
    
    @pytest.fixture
    def auth_session(self):
        """Create authenticated session"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_comments(self, auth_session):
        """GET /api/posts/{id}/comments should return comments"""
        # Get a post first
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if len(posts) > 0:
            post_id = posts[0]["_id"]
            response = auth_session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            print(f"✓ /api/posts/{post_id}/comments returns {len(data)} comments")
        else:
            pytest.skip("No posts available")
    
    def test_create_comment(self, auth_session):
        """POST /api/posts/{id}/comments should create comment"""
        # Get a post first
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if len(posts) > 0:
            post_id = posts[0]["_id"]
            response = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json={
                "content": f"TEST_Comment_{uuid.uuid4().hex[:8]}"
            })
            assert response.status_code == 201
            data = response.json()
            assert "id" in data
            assert "content" in data
            print(f"✓ Comment created on post {post_id}")
        else:
            pytest.skip("No posts available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
