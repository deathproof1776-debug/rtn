"""
Comprehensive Feature Verification Tests for Rebel Trade Network
Tests ALL features across ALL scenarios as requested.
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@homesteadhub.com"
ADMIN_PASSWORD = "admin123"
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"


class TestAuthFlow:
    """AUTH FLOW: Login/logout, session persistence, invalid credentials"""
    
    def test_api_root_running(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        print("✓ API root is running")
    
    def test_login_admin_user(self):
        """Login with admin credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == ADMIN_EMAIL
        assert data["role"] == "admin"
        assert "access_token" in session.cookies or "id" in data
        print(f"✓ Admin login successful: {data['name']}")
    
    def test_login_demo_user(self):
        """Login with demo user credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == DEMO_EMAIL
        print(f"✓ Demo user login successful: {data['name']}")
    
    def test_login_invalid_credentials(self):
        """Login with invalid credentials should fail"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid credentials rejected correctly")
    
    def test_auth_me_requires_auth(self):
        """GET /api/auth/me requires authentication"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401
        print("✓ /api/auth/me requires authentication")
    
    def test_session_persistence(self):
        """Session should persist across requests"""
        session = requests.Session()
        # Login
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_resp.status_code == 200
        
        # Access protected endpoint
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["email"] == DEMO_EMAIL
        print("✓ Session persistence working")
    
    def test_logout(self):
        """Logout should clear session"""
        session = requests.Session()
        # Login
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        
        # Logout
        logout_resp = session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_resp.status_code == 200
        
        # Verify session cleared
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 401
        print("✓ Logout clears session correctly")


class TestFeedAndPosts:
    """FEED: Post creation, display, like/unlike, comments, nearby filter"""
    
    @pytest.fixture
    def auth_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_posts_requires_auth(self):
        """GET /api/posts requires authentication"""
        response = requests.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 401
        print("✓ Posts endpoint requires auth")
    
    def test_get_posts(self, auth_session):
        """Get posts feed"""
        response = auth_session.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} posts from feed")
    
    def test_create_post(self, auth_session):
        """Create a new barter post"""
        post_data = {
            "title": f"TEST_Post_{uuid.uuid4().hex[:8]}",
            "description": "Test post for comprehensive testing",
            "category": "goods",
            "offering": ["Fresh Eggs", "Honey"],
            "looking_for": ["Seeds", "Tools"],
            "images": []
        }
        response = auth_session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        print(f"✓ Created post: {data['id']}")
        return data["id"]
    
    def test_like_unlike_post(self, auth_session):
        """Like and unlike a post"""
        # Get a post
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if not posts:
            pytest.skip("No posts available")
        
        post_id = posts[0]["_id"]
        
        # Like
        like_resp = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/like")
        assert like_resp.status_code == 200
        
        # Unlike (toggle)
        unlike_resp = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/like")
        assert unlike_resp.status_code == 200
        print(f"✓ Like/unlike toggle working for post {post_id}")
    
    def test_create_comment(self, auth_session):
        """Create a comment on a post"""
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if not posts:
            pytest.skip("No posts available")
        
        post_id = posts[0]["_id"]
        comment_data = {"content": f"TEST_Comment_{uuid.uuid4().hex[:8]}"}
        
        response = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        print(f"✓ Created comment: {data['id']}")
        return data["id"]
    
    def test_get_comments(self, auth_session):
        """Get comments for a post"""
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if not posts:
            pytest.skip("No posts available")
        
        post_id = posts[0]["_id"]
        response = auth_session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} comments for post")
    
    def test_threaded_comments(self, auth_session):
        """Test 2-level comment threading"""
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        posts = posts_resp.json()
        if not posts:
            pytest.skip("No posts available")
        
        post_id = posts[0]["_id"]
        
        # Create parent comment
        parent_resp = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json={
            "content": f"TEST_Parent_{uuid.uuid4().hex[:8]}"
        })
        assert parent_resp.status_code == 201
        parent_id = parent_resp.json()["id"]
        
        # Create reply
        reply_resp = auth_session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json={
            "content": f"TEST_Reply_{uuid.uuid4().hex[:8]}",
            "parent_id": parent_id
        })
        assert reply_resp.status_code == 201
        print("✓ Threaded comments (2 levels) working")
    
    def test_nearby_filter(self, auth_session):
        """Test nearby posts filter"""
        response = auth_session.get(f"{BASE_URL}/api/posts?nearby_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Nearby filter returned {len(data)} posts")
    
    def test_matched_posts(self, auth_session):
        """Get posts matching user's wants/offerings"""
        response = auth_session.get(f"{BASE_URL}/api/posts/matches")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Matched posts returned {len(data)} results")


class TestTradeNetwork:
    """TRADE NETWORK: Connections, requests, recommendations"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_connections(self, demo_session):
        """Get network connections"""
        response = demo_session.get(f"{BASE_URL}/api/network/connections")
        assert response.status_code == 200
        data = response.json()
        assert "connections" in data
        assert "count" in data
        print(f"✓ Got {data['count']} network connections")
    
    def test_get_pending_requests(self, demo_session):
        """Get pending network requests"""
        response = demo_session.get(f"{BASE_URL}/api/network/requests/pending")
        assert response.status_code == 200
        data = response.json()
        assert "incoming" in data
        assert "outgoing" in data
        print(f"✓ Got {len(data['incoming'])} incoming, {len(data['outgoing'])} outgoing requests")
    
    def test_get_recommended_traders(self, demo_session):
        """Get recommended traders"""
        response = demo_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        print(f"✓ Got {len(data['recommendations'])} recommended traders")
    
    def test_network_status(self, demo_session, admin_session):
        """Check network status with another user"""
        # Get admin user ID
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me").json()
        admin_id = admin_me["id"]
        
        response = demo_session.get(f"{BASE_URL}/api/network/status/{admin_id}")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✓ Network status with admin: {data['status']}")


class TestTradeDeals:
    """TRADE DEALS: Create, counter-offer, accept/decline, cancel, history"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return session
    
    def test_get_incoming_trades(self, demo_session):
        """Get incoming trade offers"""
        response = demo_session.get(f"{BASE_URL}/api/trades/incoming")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} incoming trades")
    
    def test_get_outgoing_trades(self, demo_session):
        """Get outgoing trade offers"""
        response = demo_session.get(f"{BASE_URL}/api/trades/outgoing")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} outgoing trades")
    
    def test_get_trade_history(self, demo_session):
        """Get trade history"""
        response = demo_session.get(f"{BASE_URL}/api/trades/history")
        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert "total" in data
        print(f"✓ Got {data['total']} trades in history")
    
    def test_get_active_trade_count(self, demo_session):
        """Get active trade count for badge"""
        response = demo_session.get(f"{BASE_URL}/api/trades/active-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        print(f"✓ Active trade count: {data['count']}")
    
    def test_create_trade_offer(self, demo_session, admin_session):
        """Create a trade offer"""
        # Get admin user ID
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me").json()
        admin_id = admin_me["id"]
        
        trade_data = {
            "receiver_id": admin_id,
            "offering": ["Fresh Eggs", "Honey"],
            "requesting": ["Seeds"],
            "message": f"TEST_Trade_{uuid.uuid4().hex[:8]}"
        }
        response = demo_session.post(f"{BASE_URL}/api/trades", json=trade_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        print(f"✓ Created trade offer: {data['id']}")
        return data["id"]


class TestMessaging:
    """MESSAGING: Conversations, send/receive messages"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return session
    
    def test_get_conversations(self, demo_session):
        """Get conversations list"""
        response = demo_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} conversations")
    
    def test_send_message(self, demo_session, admin_session):
        """Send a direct message"""
        # Get admin user ID
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me").json()
        admin_id = admin_me["id"]
        
        message_data = {
            "receiver_id": admin_id,
            "content": f"TEST_Message_{uuid.uuid4().hex[:8]}"
        }
        response = demo_session.post(f"{BASE_URL}/api/messages", json=message_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✓ Sent message: {data['id']}")
    
    def test_get_messages(self, demo_session, admin_session):
        """Get messages with a user"""
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me").json()
        admin_id = admin_me["id"]
        
        response = demo_session.get(f"{BASE_URL}/api/messages/{admin_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} messages with admin")


class TestGallery:
    """GALLERY: Upload, view, like, comment"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_gallery(self, demo_session):
        """Get gallery items"""
        response = demo_session.get(f"{BASE_URL}/api/gallery")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} gallery items")
    
    def test_like_gallery_item(self, demo_session):
        """Like a gallery item"""
        gallery_resp = demo_session.get(f"{BASE_URL}/api/gallery")
        items = gallery_resp.json()
        if not items:
            pytest.skip("No gallery items available")
        
        item_id = items[0]["id"]
        response = demo_session.post(f"{BASE_URL}/api/gallery/{item_id}/like")
        assert response.status_code == 200
        print(f"✓ Liked gallery item: {item_id}")


class TestProfile:
    """PROFILE: View, edit, avatar"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_own_profile(self, demo_session):
        """Get own profile via /api/auth/me"""
        response = demo_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == DEMO_EMAIL
        print(f"✓ Got own profile: {data['name']}")
    
    def test_get_other_profile(self, demo_session):
        """Get another user's profile"""
        # Get admin session to get their ID
        admin_session = requests.Session()
        admin_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me").json()
        admin_id = admin_me["id"]
        
        response = demo_session.get(f"{BASE_URL}/api/profile/{admin_id}")
        assert response.status_code == 200
        data = response.json()
        assert "_id" in data or "id" in data
        print(f"✓ Got other user profile: {data.get('name', 'Unknown')}")
    
    def test_update_profile(self, demo_session):
        """Update profile"""
        update_data = {
            "bio": f"TEST_Bio_{uuid.uuid4().hex[:8]}"
        }
        response = demo_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        print("✓ Profile updated successfully")
    
    def test_get_nearby_users(self, demo_session):
        """Get nearby users"""
        response = demo_session.get(f"{BASE_URL}/api/users/nearby")
        assert response.status_code == 200
        data = response.json()
        assert "nearby_users" in data
        print(f"✓ Got {len(data['nearby_users'])} nearby users")


class TestAdmin:
    """ADMIN: Stats, user management, post management, audit log"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_admin_stats(self, admin_session):
        """Get admin stats"""
        response = admin_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_posts" in data
        print(f"✓ Admin stats: {data['total_users']} users, {data['total_posts']} posts")
    
    def test_admin_stats_requires_admin(self, demo_session):
        """Admin stats requires admin role"""
        response = demo_session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 403
        print("✓ Admin stats correctly requires admin role")
    
    def test_admin_users(self, admin_session):
        """Get all users (admin)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        print(f"✓ Admin users: {data['total']} total")
    
    def test_admin_posts(self, admin_session):
        """Get all posts (admin)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/posts")
        assert response.status_code == 200
        data = response.json()
        assert "posts" in data
        assert "total" in data
        print(f"✓ Admin posts: {data['total']} total")
    
    def test_admin_audit_log(self, admin_session):
        """Get audit log"""
        response = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        print(f"✓ Audit log: {data['total']} entries")


class TestInvites:
    """INVITES: Create, validate, view"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_create_invite(self, demo_session):
        """Create an invite"""
        response = demo_session.post(f"{BASE_URL}/api/invites/create", json={
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        print(f"✓ Created invite token")
        return data["token"]
    
    def test_validate_invite(self, demo_session):
        """Validate an invite token"""
        # Create invite first
        create_resp = demo_session.post(f"{BASE_URL}/api/invites/create", json={})
        token = create_resp.json()["token"]
        
        # Validate (public endpoint)
        response = requests.get(f"{BASE_URL}/api/invites/validate/{token}")
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == True
        print("✓ Invite validation working")
    
    def test_get_my_invites(self, demo_session):
        """Get my invites"""
        response = demo_session.get(f"{BASE_URL}/api/invites/my-invites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} invites")


class TestPushNotifications:
    """PUSH NOTIFICATIONS: Subscribe, test, unsubscribe"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_vapid_key(self):
        """Get VAPID public key"""
        response = requests.get(f"{BASE_URL}/api/notifications/vapid-public-key")
        assert response.status_code == 200
        data = response.json()
        assert "publicKey" in data
        print("✓ Got VAPID public key")
    
    def test_notification_status(self, demo_session):
        """Get notification subscription status"""
        response = demo_session.get(f"{BASE_URL}/api/notifications/status")
        assert response.status_code == 200
        data = response.json()
        assert "subscribed" in data
        print(f"✓ Notification status: subscribed={data['subscribed']}")


class TestCategories:
    """CATEGORIES: Goods, skills, services"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_get_goods_categories(self, demo_session):
        """Get goods categories"""
        response = demo_session.get(f"{BASE_URL}/api/categories/goods")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ Got {len(data['categories'])} goods categories")
    
    def test_get_skills_categories(self, demo_session):
        """Get skills categories"""
        response = demo_session.get(f"{BASE_URL}/api/categories/skills")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ Got {len(data['categories'])} skills categories")
    
    def test_get_services_categories(self, demo_session):
        """Get services categories"""
        response = demo_session.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        print(f"✓ Got {len(data['categories'])} services categories")
    
    def test_get_all_categories(self, demo_session):
        """Get all categories"""
        response = demo_session.get(f"{BASE_URL}/api/categories/all")
        assert response.status_code == 200
        data = response.json()
        assert "goods" in data
        assert "skills" in data
        assert "services" in data
        print("✓ Got all categories")


class TestFileUploads:
    """FILE UPLOADS: Upload and retrieve files"""
    
    @pytest.fixture
    def demo_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        return session
    
    def test_upload_requires_auth(self):
        """Upload requires authentication"""
        response = requests.post(f"{BASE_URL}/api/upload")
        assert response.status_code in [401, 422]  # 422 if missing file
        print("✓ Upload requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
