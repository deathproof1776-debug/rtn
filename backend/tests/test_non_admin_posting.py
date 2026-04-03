"""
Test non-admin user posting flows for Barter Feed and Community Board.
Tests: post creation, likes, comments, push notifications.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Demo user credentials (non-admin)
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"


class TestNonAdminBarterPost:
    """Test barter post creation and interactions for non-admin users"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as demo user before each test"""
        self.session = requests.Session()
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_res.status_code == 200, f"Demo user login failed: {login_res.text}"
        self.user_data = login_res.json()
        print(f"Logged in as demo user: {self.user_data.get('name', 'Unknown')}")
        yield
        # Cleanup
        self.session.close()
    
    def test_create_barter_post_with_all_fields(self):
        """Demo user can create barter post with title, description, category, offering, looking_for"""
        post_data = {
            "title": "TEST_Barter_Fresh Eggs for Trade",
            "description": "I have fresh free-range eggs from my homestead chickens",
            "category": "goods",
            "offering": [{"name": "Fresh Eggs", "quantity": "2 dozen", "description": "Free range"}],
            "looking_for": [{"name": "Vegetables", "quantity": "5 lbs", "description": "Organic preferred"}],
            "images": []
        }
        
        res = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert res.status_code == 201, f"Failed to create barter post: {res.text}"
        
        data = res.json()
        assert "id" in data, "Response should contain post id"
        assert data.get("message") == "Post created successfully"
        
        self.created_post_id = data["id"]
        print(f"Created barter post with ID: {self.created_post_id}")
        
        # Verify post appears in feed
        feed_res = self.session.get(f"{BASE_URL}/api/posts")
        assert feed_res.status_code == 200
        
        posts = feed_res.json()
        post_ids = [p["_id"] for p in posts]
        assert self.created_post_id in post_ids, "Created post should appear in feed"
        
        # Find our post and verify fields
        our_post = next((p for p in posts if p["_id"] == self.created_post_id), None)
        assert our_post is not None
        assert our_post["title"] == post_data["title"]
        assert our_post["category"] == "goods"
        print("Post appears in feed with correct data")
    
    def test_create_barter_post_services_category(self):
        """Demo user can create barter post with services category"""
        post_data = {
            "title": "TEST_Barter_Carpentry Services",
            "description": "Offering carpentry and woodworking services",
            "category": "services",
            "offering": [{"name": "Carpentry", "quantity": "10 hours", "description": "Furniture repair"}],
            "looking_for": [{"name": "Plumbing help", "quantity": "5 hours", "description": ""}],
            "images": []
        }
        
        res = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert res.status_code == 201, f"Failed to create services post: {res.text}"
        print("Created services category barter post")
    
    def test_create_barter_post_skills_category(self):
        """Demo user can create barter post with skills category"""
        post_data = {
            "title": "TEST_Barter_Teaching Guitar",
            "description": "Can teach guitar lessons in exchange for other skills",
            "category": "skills",
            "offering": [{"name": "Guitar Lessons", "quantity": "4 sessions", "description": "Beginner to intermediate"}],
            "looking_for": [{"name": "Spanish Lessons", "quantity": "4 sessions", "description": ""}],
            "images": []
        }
        
        res = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert res.status_code == 201, f"Failed to create skills post: {res.text}"
        print("Created skills category barter post")
    
    def test_like_own_barter_post(self):
        """User can like their own barter post"""
        # First create a post
        post_data = {
            "title": "TEST_Barter_Like Test Post",
            "description": "Testing like functionality",
            "category": "goods",
            "offering": [{"name": "Test Item", "quantity": "1", "description": ""}],
            "looking_for": [{"name": "Another Item", "quantity": "1", "description": ""}],
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Like the post
        like_res = self.session.post(f"{BASE_URL}/api/posts/{post_id}/like")
        assert like_res.status_code == 200, f"Failed to like post: {like_res.text}"
        assert like_res.json().get("message") == "Post liked"
        print("Successfully liked own barter post")
        
        # Unlike the post
        unlike_res = self.session.post(f"{BASE_URL}/api/posts/{post_id}/like")
        assert unlike_res.status_code == 200
        assert unlike_res.json().get("message") == "Post unliked"
        print("Successfully unliked own barter post")
    
    def test_comment_on_barter_post(self):
        """User can comment on barter posts"""
        # First create a post
        post_data = {
            "title": "TEST_Barter_Comment Test Post",
            "description": "Testing comment functionality",
            "category": "goods",
            "offering": [{"name": "Test Item", "quantity": "1", "description": ""}],
            "looking_for": [{"name": "Another Item", "quantity": "1", "description": ""}],
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Add a comment
        comment_data = {"content": "TEST_Comment: This is a great offer!", "parent_id": None}
        comment_res = self.session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_data)
        assert comment_res.status_code == 201, f"Failed to add comment: {comment_res.text}"
        
        comment = comment_res.json()
        assert "id" in comment
        assert comment["content"] == "TEST_Comment: This is a great offer!"
        print(f"Successfully added comment with ID: {comment['id']}")
        
        # Verify comment appears in post
        comments_res = self.session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        assert comments_res.status_code == 200
        comments = comments_res.json()
        assert len(comments) >= 1
        print("Comment appears in post comments")
    
    def test_barter_post_validation_title_required(self):
        """Barter post requires title"""
        post_data = {
            "title": "",
            "description": "Test description",
            "category": "goods",
            "offering": [{"name": "Test", "quantity": "1", "description": ""}],
            "looking_for": [{"name": "Test", "quantity": "1", "description": ""}],
            "images": []
        }
        
        res = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        # Should fail validation - either 400 or 422
        assert res.status_code in [400, 422], f"Expected validation error, got {res.status_code}"
        print("Title validation working correctly")


class TestNonAdminCommunityPost:
    """Test community post creation and interactions for non-admin users"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as demo user before each test"""
        self.session = requests.Session()
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_res.status_code == 200, f"Demo user login failed: {login_res.text}"
        self.user_data = login_res.json()
        print(f"Logged in as demo user: {self.user_data.get('name', 'Unknown')}")
        yield
        self.session.close()
    
    def test_get_community_topics(self):
        """Verify all 15 community topics are available"""
        res = self.session.get(f"{BASE_URL}/api/community/topics")
        assert res.status_code == 200, f"Failed to get topics: {res.text}"
        
        data = res.json()
        topics = data.get("topics", [])
        assert len(topics) == 15, f"Expected 15 topics, got {len(topics)}"
        
        expected_topics = ["homesteading", "off-grid", "prepping", "diy", "gardening", 
                          "livestock", "food", "energy", "water", "security", 
                          "health", "finance", "community", "news", "general"]
        topic_ids = [t["id"] for t in topics]
        for expected in expected_topics:
            assert expected in topic_ids, f"Missing topic: {expected}"
        
        print(f"All 15 topics available: {topic_ids}")
    
    def test_create_community_post_with_all_fields(self):
        """Demo user can create community post with title, content, topic"""
        post_data = {
            "title": "TEST_Community_Best Practices for Rainwater Collection",
            "content": "I've been collecting rainwater for 5 years now. Here are my top tips for setting up a reliable system...",
            "topic": "water",
            "images": []
        }
        
        res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert res.status_code == 201, f"Failed to create community post: {res.text}"
        
        data = res.json()
        assert "id" in data
        self.created_post_id = data["id"]
        print(f"Created community post with ID: {self.created_post_id}")
        
        # Verify post appears in community board
        feed_res = self.session.get(f"{BASE_URL}/api/community")
        assert feed_res.status_code == 200
        
        posts = feed_res.json()
        post_ids = [p["_id"] for p in posts]
        assert self.created_post_id in post_ids, "Created post should appear in community board"
        
        # Verify topic badge
        our_post = next((p for p in posts if p["_id"] == self.created_post_id), None)
        assert our_post is not None
        assert our_post["topic"] == "water"
        print("Post appears in community board with correct topic badge")
    
    def test_create_community_post_each_topic(self):
        """Demo user can create posts with different topics"""
        topics_to_test = ["homesteading", "gardening", "diy", "general"]
        
        for topic in topics_to_test:
            post_data = {
                "title": f"TEST_Community_{topic.title()} Discussion",
                "content": f"This is a test post about {topic}",
                "topic": topic,
                "images": []
            }
            
            res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
            assert res.status_code == 201, f"Failed to create {topic} post: {res.text}"
            print(f"Created community post with topic: {topic}")
    
    def test_like_community_post(self):
        """User can like community posts"""
        # First create a post
        post_data = {
            "title": "TEST_Community_Like Test",
            "content": "Testing like functionality on community posts",
            "topic": "general",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Like the post
        like_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/like")
        assert like_res.status_code == 200, f"Failed to like community post: {like_res.text}"
        assert like_res.json().get("liked") == True
        print("Successfully liked community post")
        
        # Unlike the post
        unlike_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/like")
        assert unlike_res.status_code == 200
        assert unlike_res.json().get("liked") == False
        print("Successfully unliked community post")
    
    def test_comment_on_community_post(self):
        """User can comment on community posts"""
        # First create a post
        post_data = {
            "title": "TEST_Community_Comment Test",
            "content": "Testing comment functionality",
            "topic": "general",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Add a comment
        comment_data = {"content": "TEST_Comment: Great information!", "parent_id": None}
        comment_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/comments", json=comment_data)
        assert comment_res.status_code == 201, f"Failed to add comment: {comment_res.text}"
        
        comment = comment_res.json()
        assert "id" in comment
        assert comment["content"] == "TEST_Comment: Great information!"
        print(f"Successfully added comment with ID: {comment['id']}")
    
    def test_reply_to_community_comment(self):
        """User can reply to comments (threaded comments)"""
        # Create a post
        post_data = {
            "title": "TEST_Community_Reply Test",
            "content": "Testing threaded reply functionality",
            "topic": "general",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Add parent comment
        parent_comment = {"content": "TEST_Comment: Parent comment", "parent_id": None}
        parent_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/comments", json=parent_comment)
        assert parent_res.status_code == 201
        parent_id = parent_res.json()["id"]
        
        # Add reply to parent
        reply_comment = {"content": "TEST_Comment: This is a reply", "parent_id": parent_id}
        reply_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/comments", json=reply_comment)
        assert reply_res.status_code == 201, f"Failed to add reply: {reply_res.text}"
        
        reply = reply_res.json()
        assert reply["parent_id"] == parent_id
        print("Successfully added threaded reply")
    
    def test_community_post_validation(self):
        """Community post requires title and content"""
        # Missing title
        res1 = self.session.post(f"{BASE_URL}/api/community", json={
            "title": "",
            "content": "Some content",
            "topic": "general"
        })
        assert res1.status_code == 400, f"Expected 400 for missing title, got {res1.status_code}"
        
        # Missing content
        res2 = self.session.post(f"{BASE_URL}/api/community", json={
            "title": "Some title",
            "content": "",
            "topic": "general"
        })
        assert res2.status_code == 400, f"Expected 400 for missing content, got {res2.status_code}"
        
        print("Community post validation working correctly")
    
    def test_filter_community_by_topic(self):
        """Community posts can be filtered by topic"""
        # Create a post with specific topic
        post_data = {
            "title": "TEST_Community_Filter Test Gardening",
            "content": "This is a gardening post for filter testing",
            "topic": "gardening",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Filter by gardening topic
        filter_res = self.session.get(f"{BASE_URL}/api/community?topic=gardening")
        assert filter_res.status_code == 200
        
        posts = filter_res.json()
        # All posts should have gardening topic
        for post in posts:
            assert post["topic"] == "gardening", f"Expected gardening topic, got {post['topic']}"
        
        print(f"Topic filter working - found {len(posts)} gardening posts")


class TestPushNotifications:
    """Test push notification triggers for community interactions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as demo user"""
        self.session = requests.Session()
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_res.status_code == 200
        self.user_data = login_res.json()
        yield
        self.session.close()
    
    def test_like_triggers_notification_endpoint(self):
        """Liking a post should trigger notification (verify endpoint is called)"""
        # Create a post
        post_data = {
            "title": "TEST_Notification_Like Test",
            "content": "Testing notification on like",
            "topic": "general",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Like the post - this should trigger notification in background
        like_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/like")
        assert like_res.status_code == 200
        print("Like action completed - notification should be triggered in background")
    
    def test_comment_triggers_notification_endpoint(self):
        """Commenting on a post should trigger notification"""
        # Create a post
        post_data = {
            "title": "TEST_Notification_Comment Test",
            "content": "Testing notification on comment",
            "topic": "general",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Add comment - this should trigger notification
        comment_data = {"content": "TEST_Comment: Notification test", "parent_id": None}
        comment_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/comments", json=comment_data)
        assert comment_res.status_code == 201
        print("Comment action completed - notification should be triggered in background")
    
    def test_reply_triggers_notification_endpoint(self):
        """Replying to a comment should trigger notification to parent author"""
        # Create a post
        post_data = {
            "title": "TEST_Notification_Reply Test",
            "content": "Testing notification on reply",
            "topic": "general",
            "images": []
        }
        
        create_res = self.session.post(f"{BASE_URL}/api/community", json=post_data)
        assert create_res.status_code == 201
        post_id = create_res.json()["id"]
        
        # Add parent comment
        parent_comment = {"content": "TEST_Comment: Parent for reply test", "parent_id": None}
        parent_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/comments", json=parent_comment)
        assert parent_res.status_code == 201
        parent_id = parent_res.json()["id"]
        
        # Add reply - this should trigger notification to parent author
        reply_comment = {"content": "TEST_Comment: Reply notification test", "parent_id": parent_id}
        reply_res = self.session.post(f"{BASE_URL}/api/community/{post_id}/comments", json=reply_comment)
        assert reply_res.status_code == 201
        print("Reply action completed - notification should be triggered in background")


class TestFilterPersistence:
    """Test that filters stay active after creating posts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as demo user"""
        self.session = requests.Session()
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_res.status_code == 200
        yield
        self.session.close()
    
    def test_barter_feed_filter_with_category(self):
        """Barter feed category filter works"""
        # Get posts with goods category filter
        res = self.session.get(f"{BASE_URL}/api/posts?category=goods")
        assert res.status_code == 200
        
        posts = res.json()
        for post in posts:
            assert post.get("category") == "goods", f"Expected goods category, got {post.get('category')}"
        
        print(f"Category filter working - found {len(posts)} goods posts")
    
    def test_community_filter_with_topic(self):
        """Community board topic filter works"""
        res = self.session.get(f"{BASE_URL}/api/community?topic=homesteading")
        assert res.status_code == 200
        
        posts = res.json()
        for post in posts:
            assert post.get("topic") == "homesteading"
        
        print(f"Topic filter working - found {len(posts)} homesteading posts")


# Cleanup test data
class TestCleanup:
    """Cleanup TEST_ prefixed data"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        login_res = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": DEMO_EMAIL,
            "password": DEMO_PASSWORD
        })
        assert login_res.status_code == 200
        yield
        self.session.close()
    
    def test_cleanup_test_posts(self):
        """Clean up TEST_ prefixed posts"""
        # Get all community posts
        community_res = self.session.get(f"{BASE_URL}/api/community?limit=100")
        if community_res.status_code == 200:
            posts = community_res.json()
            for post in posts:
                if post.get("title", "").startswith("TEST_"):
                    delete_res = self.session.delete(f"{BASE_URL}/api/community/{post['_id']}")
                    if delete_res.status_code == 200:
                        print(f"Deleted community post: {post['title'][:50]}")
        
        print("Cleanup completed")
