"""
Test Community Board, System Messages, and Feed Filters
New features: Community Board, Admin Announcements, Feed Filters
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@homesteadhub.com"
ADMIN_PASSWORD = "admin123"
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"


@pytest.fixture(scope="module")
def admin_session():
    """Get authenticated admin session"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Admin login failed")
    return session


@pytest.fixture(scope="module")
def demo_session():
    """Get authenticated demo user session"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip("Demo user login failed")
    return session


class TestCommunityTopics:
    """Test community topics endpoint"""
    
    def test_get_topics_returns_15_topics(self):
        """GET /api/community/topics returns 15 topics"""
        response = requests.get(f"{BASE_URL}/api/community/topics")
        assert response.status_code == 200
        data = response.json()
        assert "topics" in data
        assert len(data["topics"]) == 15
        
        # Verify topic structure
        for topic in data["topics"]:
            assert "id" in topic
            assert "name" in topic
            assert "icon" in topic
    
    def test_topics_include_expected_categories(self):
        """Topics include expected categories"""
        response = requests.get(f"{BASE_URL}/api/community/topics")
        data = response.json()
        topic_ids = [t["id"] for t in data["topics"]]
        
        expected = ["homesteading", "off-grid", "prepping", "diy", "gardening", 
                   "livestock", "food", "energy", "water", "security", 
                   "health", "finance", "community", "news", "general"]
        
        for expected_id in expected:
            assert expected_id in topic_ids, f"Missing topic: {expected_id}"


class TestCommunityPosts:
    """Test community post CRUD operations"""
    
    def test_create_community_post_requires_auth(self):
        """POST /api/community requires authentication"""
        response = requests.post(f"{BASE_URL}/api/community", json={
            "title": "Test Post",
            "content": "Test content",
            "topic": "general"
        })
        assert response.status_code == 401
    
    def test_create_community_post(self, demo_session):
        """POST /api/community creates post successfully"""
        response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "TEST_Community Post Title",
            "content": "This is a test community post content for testing purposes.",
            "topic": "homesteading"
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["message"] == "Post created successfully"
        
        # Store post ID for cleanup
        pytest.community_post_id = data["id"]
    
    def test_create_community_post_requires_title(self, demo_session):
        """POST /api/community requires title"""
        response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "",
            "content": "Content without title",
            "topic": "general"
        })
        assert response.status_code == 400
        assert "Title is required" in response.json().get("detail", "")
    
    def test_create_community_post_requires_content(self, demo_session):
        """POST /api/community requires content"""
        response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "Title without content",
            "content": "",
            "topic": "general"
        })
        assert response.status_code == 400
        assert "Content is required" in response.json().get("detail", "")
    
    def test_get_community_posts(self, demo_session):
        """GET /api/community returns posts"""
        response = demo_session.get(f"{BASE_URL}/api/community")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_community_posts_with_topic_filter(self, demo_session):
        """GET /api/community?topic=homesteading filters by topic"""
        response = demo_session.get(f"{BASE_URL}/api/community?topic=homesteading")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned posts should have homesteading topic
        for post in data:
            assert post.get("topic") == "homesteading"
    
    def test_get_community_posts_with_nearby_filter(self, demo_session):
        """GET /api/community?nearby_only=true filters nearby posts"""
        response = demo_session.get(f"{BASE_URL}/api/community?nearby_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_community_posts_with_network_filter(self, demo_session):
        """GET /api/community?network_only=true filters network posts"""
        response = demo_session.get(f"{BASE_URL}/api/community?network_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_community_posts_with_verified_filter(self, demo_session):
        """GET /api/community?verified_only=true filters verified posts"""
        response = demo_session.get(f"{BASE_URL}/api/community?verified_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCommunityLikes:
    """Test community post like functionality"""
    
    def test_like_community_post(self, demo_session):
        """POST /api/community/{id}/like toggles like"""
        # First create a post to like
        create_response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "TEST_Post to Like",
            "content": "This post will be liked",
            "topic": "general"
        })
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # Like the post
        like_response = demo_session.post(f"{BASE_URL}/api/community/{post_id}/like")
        assert like_response.status_code == 200
        data = like_response.json()
        assert "liked" in data
        assert data["liked"] == True
        
        # Unlike the post
        unlike_response = demo_session.post(f"{BASE_URL}/api/community/{post_id}/like")
        assert unlike_response.status_code == 200
        data = unlike_response.json()
        assert data["liked"] == False
    
    def test_like_nonexistent_post(self, demo_session):
        """POST /api/community/{id}/like returns 404 for nonexistent post"""
        response = demo_session.post(f"{BASE_URL}/api/community/000000000000000000000000/like")
        assert response.status_code == 404


class TestCommunityComments:
    """Test community post comment functionality"""
    
    def test_add_comment_to_community_post(self, demo_session):
        """POST /api/community/{id}/comments adds comment"""
        # Create a post first
        create_response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "TEST_Post for Comments",
            "content": "This post will have comments",
            "topic": "general"
        })
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # Add a comment
        comment_response = demo_session.post(f"{BASE_URL}/api/community/{post_id}/comments", json={
            "content": "This is a test comment"
        })
        assert comment_response.status_code == 201
        data = comment_response.json()
        assert "id" in data
        assert data["content"] == "This is a test comment"
        
        # Store comment ID for threading test
        pytest.community_comment_id = data["id"]
        pytest.community_post_for_comments = post_id
    
    def test_add_threaded_reply(self, demo_session):
        """POST /api/community/{id}/comments with parent_id creates threaded reply"""
        if not hasattr(pytest, 'community_comment_id'):
            pytest.skip("No parent comment available")
        
        response = demo_session.post(
            f"{BASE_URL}/api/community/{pytest.community_post_for_comments}/comments",
            json={
                "content": "This is a threaded reply",
                "parent_id": pytest.community_comment_id
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == pytest.community_comment_id
    
    def test_comment_requires_content(self, demo_session):
        """POST /api/community/{id}/comments requires content"""
        # Create a post first
        create_response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "TEST_Post for Empty Comment",
            "content": "Testing empty comment",
            "topic": "general"
        })
        post_id = create_response.json()["id"]
        
        response = demo_session.post(f"{BASE_URL}/api/community/{post_id}/comments", json={
            "content": ""
        })
        assert response.status_code == 400


class TestSystemMessages:
    """Test admin system messages (announcements)"""
    
    def test_get_active_messages_no_auth_required(self):
        """GET /api/admin/system-messages/active works without auth"""
        response = requests.get(f"{BASE_URL}/api/admin/system-messages/active")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    def test_create_system_message_requires_admin(self, demo_session):
        """POST /api/admin/system-messages requires admin role"""
        response = demo_session.post(f"{BASE_URL}/api/admin/system-messages", json={
            "message": "Test announcement",
            "type": "info",
            "is_active": True
        })
        assert response.status_code == 403
    
    def test_create_system_message(self, admin_session):
        """POST /api/admin/system-messages creates announcement"""
        response = admin_session.post(f"{BASE_URL}/api/admin/system-messages", json={
            "message": "TEST_System Announcement - Welcome to Rebel Trade Network!",
            "type": "info",
            "is_active": True,
            "priority": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        pytest.system_message_id = data["id"]
    
    def test_get_all_system_messages_requires_admin(self, demo_session):
        """GET /api/admin/system-messages requires admin role"""
        response = demo_session.get(f"{BASE_URL}/api/admin/system-messages")
        assert response.status_code == 403
    
    def test_get_all_system_messages(self, admin_session):
        """GET /api/admin/system-messages returns all messages"""
        response = admin_session.get(f"{BASE_URL}/api/admin/system-messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "total" in data
    
    def test_update_system_message(self, admin_session):
        """PUT /api/admin/system-messages/{id} updates message"""
        if not hasattr(pytest, 'system_message_id'):
            pytest.skip("No system message to update")
        
        response = admin_session.put(
            f"{BASE_URL}/api/admin/system-messages/{pytest.system_message_id}",
            json={
                "message": "TEST_Updated System Announcement",
                "type": "warning",
                "is_active": False
            }
        )
        assert response.status_code == 200
    
    def test_toggle_system_message_active(self, admin_session):
        """PUT /api/admin/system-messages/{id} can toggle is_active"""
        if not hasattr(pytest, 'system_message_id'):
            pytest.skip("No system message to toggle")
        
        # Toggle to active
        response = admin_session.put(
            f"{BASE_URL}/api/admin/system-messages/{pytest.system_message_id}",
            json={"is_active": True}
        )
        assert response.status_code == 200
        
        # Verify it appears in active messages
        active_response = requests.get(f"{BASE_URL}/api/admin/system-messages/active")
        assert active_response.status_code == 200
        messages = active_response.json()["messages"]
        message_ids = [m["_id"] for m in messages]
        assert pytest.system_message_id in message_ids
    
    def test_delete_system_message(self, admin_session):
        """DELETE /api/admin/system-messages/{id} deletes message"""
        if not hasattr(pytest, 'system_message_id'):
            pytest.skip("No system message to delete")
        
        response = admin_session.delete(
            f"{BASE_URL}/api/admin/system-messages/{pytest.system_message_id}"
        )
        assert response.status_code == 200
        
        # Verify it's gone from active messages
        active_response = requests.get(f"{BASE_URL}/api/admin/system-messages/active")
        messages = active_response.json()["messages"]
        message_ids = [m["_id"] for m in messages]
        assert pytest.system_message_id not in message_ids


class TestBarterFeedFilters:
    """Test barter feed filter functionality"""
    
    def test_get_posts_with_nearby_filter(self, demo_session):
        """GET /api/posts?nearby_only=true filters nearby posts"""
        response = demo_session.get(f"{BASE_URL}/api/posts?nearby_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_posts_with_network_filter(self, demo_session):
        """GET /api/posts?network_only=true filters network posts"""
        response = demo_session.get(f"{BASE_URL}/api/posts?network_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_posts_with_verified_filter(self, demo_session):
        """GET /api/posts?verified_only=true filters verified posts"""
        response = demo_session.get(f"{BASE_URL}/api/posts?verified_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_posts_with_category_filter(self, demo_session):
        """GET /api/posts?category=goods filters by category"""
        response = demo_session.get(f"{BASE_URL}/api/posts?category=goods")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned posts should have goods category
        for post in data:
            assert post.get("category") == "goods"
    
    def test_get_posts_with_multiple_filters(self, demo_session):
        """GET /api/posts with multiple filters works"""
        response = demo_session.get(
            f"{BASE_URL}/api/posts?nearby_only=true&verified_only=true&category=services"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCommunityPostDeletion:
    """Test community post deletion"""
    
    def test_delete_own_community_post(self, demo_session):
        """DELETE /api/community/{id} deletes own post"""
        # Create a post to delete
        create_response = demo_session.post(f"{BASE_URL}/api/community", json={
            "title": "TEST_Post to Delete",
            "content": "This post will be deleted",
            "topic": "general"
        })
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # Delete the post
        delete_response = demo_session.delete(f"{BASE_URL}/api/community/{post_id}")
        assert delete_response.status_code == 200
        
        # Verify it's deleted (should return 404)
        get_response = demo_session.get(f"{BASE_URL}/api/community/{post_id}")
        assert get_response.status_code == 404


class TestCleanup:
    """Cleanup test data"""
    
    def test_cleanup_test_posts(self, demo_session):
        """Clean up TEST_ prefixed community posts"""
        # Get all community posts
        response = demo_session.get(f"{BASE_URL}/api/community?limit=100")
        if response.status_code == 200:
            posts = response.json()
            for post in posts:
                if post.get("title", "").startswith("TEST_"):
                    demo_session.delete(f"{BASE_URL}/api/community/{post['_id']}")
        assert True  # Cleanup always passes
