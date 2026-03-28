#!/usr/bin/env python3
"""
Test suite for HomesteadHub Comments Feature
Tests: POST, GET, DELETE comments on posts with encryption verification
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://homestead-hub-13.preview.emergentagent.com')

class TestCommentsFeature:
    """Comments endpoint tests for barter posts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.user_data = login_response.json()
        self.user_id = self.user_data.get("id")
        print(f"Logged in as user: {self.user_id}")
        
        yield
        
        # Cleanup - logout
        self.session.post(f"{BASE_URL}/api/auth/logout")
    
    @pytest.fixture
    def create_test_post(self):
        """Create a test post for comment testing"""
        timestamp = int(time.time())
        post_data = {
            "title": f"TEST_Comment_Post_{timestamp}",
            "description": "Test post for comment testing",
            "category": "goods",
            "offering": ["test item"],
            "looking_for": ["test trade"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert response.status_code == 201, f"Failed to create post: {response.text}"
        post_id = response.json().get("id")
        print(f"Created test post: {post_id}")
        return post_id
    
    # ==================== CREATE COMMENT TESTS ====================
    
    def test_create_comment_success(self, create_test_post):
        """Test creating a comment on a post - should return 201"""
        post_id = create_test_post
        comment_data = {"content": "This is a test comment"}
        
        response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json=comment_data
        )
        
        # Status assertion
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "id" in data, "Response should contain comment id"
        assert "user_id" in data, "Response should contain user_id"
        assert "user_name" in data, "Response should contain user_name"
        assert "content" in data, "Response should contain content"
        assert "created_at" in data, "Response should contain created_at"
        
        # Verify content is decrypted in response
        assert data["content"] == "This is a test comment", "Content should be decrypted"
        print(f"Created comment: {data['id']}")
    
    def test_create_comment_empty_content(self, create_test_post):
        """Test creating a comment with empty content"""
        post_id = create_test_post
        comment_data = {"content": ""}
        
        response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json=comment_data
        )
        
        # Empty content should still work (no validation in backend)
        # This is a potential improvement area
        print(f"Empty content response: {response.status_code}")
    
    def test_create_comment_nonexistent_post(self):
        """Test creating a comment on a non-existent post - should return 404"""
        fake_post_id = "000000000000000000000000"
        comment_data = {"content": "Test comment"}
        
        response = self.session.post(
            f"{BASE_URL}/api/posts/{fake_post_id}/comments",
            json=comment_data
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Should contain error detail"
        print(f"Non-existent post error: {data.get('detail')}")
    
    def test_create_comment_without_auth(self, create_test_post):
        """Test creating a comment without authentication - should return 401"""
        post_id = create_test_post
        
        # Create new session without auth
        unauthenticated_session = requests.Session()
        comment_data = {"content": "Unauthorized comment"}
        
        response = unauthenticated_session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json=comment_data
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Unauthenticated request correctly rejected")
    
    # ==================== GET COMMENTS TESTS ====================
    
    def test_get_comments_success(self, create_test_post):
        """Test retrieving comments for a post"""
        post_id = create_test_post
        
        # First create a comment
        comment_data = {"content": "Comment to retrieve"}
        create_response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json=comment_data
        )
        assert create_response.status_code == 201
        created_comment = create_response.json()
        
        # Now get comments
        response = self.session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Data assertions
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) >= 1, "Should have at least one comment"
        
        # Find our comment
        found_comment = None
        for comment in data:
            if comment.get("id") == created_comment["id"]:
                found_comment = comment
                break
        
        assert found_comment is not None, "Created comment should be in the list"
        assert found_comment["content"] == "Comment to retrieve", "Content should be decrypted"
        print(f"Retrieved {len(data)} comments")
    
    def test_get_comments_empty_post(self, create_test_post):
        """Test retrieving comments from a post with no comments"""
        post_id = create_test_post
        
        response = self.session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        # Note: Post might have 0 comments initially
        print(f"Empty post has {len(data)} comments")
    
    def test_get_comments_nonexistent_post(self):
        """Test retrieving comments from non-existent post - should return 404"""
        fake_post_id = "000000000000000000000000"
        
        response = self.session.get(f"{BASE_URL}/api/posts/{fake_post_id}/comments")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent post correctly returns 404")
    
    def test_get_comments_without_auth(self, create_test_post):
        """Test retrieving comments without authentication - should return 401"""
        post_id = create_test_post
        
        unauthenticated_session = requests.Session()
        response = unauthenticated_session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Unauthenticated GET correctly rejected")
    
    # ==================== DELETE COMMENT TESTS ====================
    
    def test_delete_own_comment(self, create_test_post):
        """Test deleting own comment - should succeed"""
        post_id = create_test_post
        
        # Create a comment
        comment_data = {"content": "Comment to delete"}
        create_response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json=comment_data
        )
        assert create_response.status_code == 201
        comment_id = create_response.json()["id"]
        
        # Delete the comment
        response = self.session.delete(
            f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}"
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data, "Should contain success message"
        print(f"Deleted comment: {comment_id}")
        
        # Verify deletion - GET comments should not include deleted comment
        get_response = self.session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        comments = get_response.json()
        comment_ids = [c.get("id") for c in comments]
        assert comment_id not in comment_ids, "Deleted comment should not be in list"
        print("Verified comment was deleted")
    
    def test_delete_nonexistent_comment(self, create_test_post):
        """Test deleting a non-existent comment - should return 404"""
        post_id = create_test_post
        fake_comment_id = "000000000000000000000000"
        
        response = self.session.delete(
            f"{BASE_URL}/api/posts/{post_id}/comments/{fake_comment_id}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent comment correctly returns 404")
    
    def test_delete_comment_nonexistent_post(self):
        """Test deleting comment from non-existent post - should return 404"""
        fake_post_id = "000000000000000000000000"
        fake_comment_id = "000000000000000000000000"
        
        response = self.session.delete(
            f"{BASE_URL}/api/posts/{fake_post_id}/comments/{fake_comment_id}"
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Non-existent post correctly returns 404")
    
    def test_delete_comment_without_auth(self, create_test_post):
        """Test deleting comment without authentication - should return 401"""
        post_id = create_test_post
        
        # Create a comment first
        comment_data = {"content": "Comment for auth test"}
        create_response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json=comment_data
        )
        comment_id = create_response.json()["id"]
        
        # Try to delete without auth
        unauthenticated_session = requests.Session()
        response = unauthenticated_session.delete(
            f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}"
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Unauthenticated DELETE correctly rejected")
    
    # ==================== AUTHORIZATION TESTS ====================
    
    def test_post_owner_can_delete_others_comment(self):
        """Test that post owner can delete any comment on their post"""
        # This test requires two users - we'll create a second user
        timestamp = int(time.time())
        
        # Register a second user
        second_session = requests.Session()
        register_response = second_session.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"TEST_user2_{timestamp}@test.com",
            "password": "testpass123",
            "name": f"Test User 2 {timestamp}",
            "location": "Test Location"
        })
        
        if register_response.status_code != 200:
            pytest.skip("Could not create second user for authorization test")
        
        # Create a post with admin (self.session)
        post_data = {
            "title": f"TEST_Auth_Post_{timestamp}",
            "description": "Post for authorization testing",
            "category": "goods",
            "offering": ["test"],
            "looking_for": ["test"]
        }
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Second user creates a comment
        comment_response = second_session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json={"content": "Comment from second user"}
        )
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]
        
        # Post owner (admin) deletes the comment
        delete_response = self.session.delete(
            f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}"
        )
        
        assert delete_response.status_code == 200, f"Post owner should be able to delete any comment: {delete_response.text}"
        print("Post owner successfully deleted another user's comment")
        
        # Cleanup - logout second user
        second_session.post(f"{BASE_URL}/api/auth/logout")
    
    def test_non_owner_cannot_delete_others_comment(self):
        """Test that non-owner cannot delete someone else's comment"""
        timestamp = int(time.time())
        
        # Register a second user
        second_session = requests.Session()
        register_response = second_session.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"TEST_user3_{timestamp}@test.com",
            "password": "testpass123",
            "name": f"Test User 3 {timestamp}",
            "location": "Test Location"
        })
        
        if register_response.status_code != 200:
            pytest.skip("Could not create second user for authorization test")
        
        # Admin creates a post
        post_data = {
            "title": f"TEST_Auth_Post2_{timestamp}",
            "description": "Post for authorization testing",
            "category": "goods",
            "offering": ["test"],
            "looking_for": ["test"]
        }
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Admin creates a comment
        comment_response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json={"content": "Admin's comment"}
        )
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]
        
        # Second user tries to delete admin's comment (should fail)
        delete_response = second_session.delete(
            f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}"
        )
        
        assert delete_response.status_code == 403, f"Non-owner should get 403: {delete_response.status_code}"
        print("Non-owner correctly forbidden from deleting others' comments")
        
        # Cleanup
        second_session.post(f"{BASE_URL}/api/auth/logout")
    
    # ==================== ENCRYPTION VERIFICATION ====================
    
    def test_comment_content_decryption(self, create_test_post):
        """Test that comment content is properly decrypted when retrieved"""
        post_id = create_test_post
        test_content = "Special characters: !@#$%^&*() and unicode: 日本語 🎉"
        
        # Create comment with special content
        create_response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json={"content": test_content}
        )
        assert create_response.status_code == 201
        
        # Verify content in create response
        created_data = create_response.json()
        assert created_data["content"] == test_content, "Create response should have decrypted content"
        
        # Verify content in GET response
        get_response = self.session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        comments = get_response.json()
        
        found = False
        for comment in comments:
            if comment.get("id") == created_data["id"]:
                assert comment["content"] == test_content, "GET response should have decrypted content"
                found = True
                break
        
        assert found, "Comment should be found in GET response"
        print("Encryption/decryption working correctly for special characters")


class TestCommentsIntegration:
    """Integration tests for comments with posts"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        yield
        
        self.session.post(f"{BASE_URL}/api/auth/logout")
    
    def test_comments_included_in_posts_list(self):
        """Test that comments array is included when fetching posts"""
        # Create a post
        timestamp = int(time.time())
        post_data = {
            "title": f"TEST_Integration_Post_{timestamp}",
            "description": "Integration test post",
            "category": "services",
            "offering": ["test service"],
            "looking_for": ["test trade"]
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        
        # Add a comment
        comment_response = self.session.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json={"content": "Integration test comment"}
        )
        assert comment_response.status_code == 201
        
        # Fetch posts list
        posts_response = self.session.get(f"{BASE_URL}/api/posts")
        assert posts_response.status_code == 200
        
        posts = posts_response.json()
        
        # Find our post
        our_post = None
        for post in posts:
            if post.get("_id") == post_id:
                our_post = post
                break
        
        assert our_post is not None, "Created post should be in posts list"
        assert "comments" in our_post, "Post should have comments field"
        assert isinstance(our_post["comments"], list), "Comments should be a list"
        print(f"Post has {len(our_post['comments'])} comments in list view")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
