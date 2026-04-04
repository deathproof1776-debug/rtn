"""
Test Edit Post and Edit Comment Features
Tests for:
- PUT /api/posts/{post_id} - Edit post
- PUT /api/posts/{post_id}/comments/{comment_id} - Edit comment
- Authorization checks (only owners can edit)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEditPostAndComment:
    """Test edit post and comment functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with demo user login"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as demo user
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert login_response.status_code == 200, f"Demo login failed: {login_response.text}"
        self.demo_user = login_response.json()
        self.demo_user_id = self.demo_user.get("id")
        print(f"Logged in as demo user: {self.demo_user.get('email')}")
        
        yield
        
        # Cleanup - logout
        self.session.post(f"{BASE_URL}/api/auth/logout")
    
    def test_create_post_for_edit(self):
        """Create a test post that we can edit"""
        post_data = {
            "title": "TEST_Edit Post Test",
            "description": "This is a test post for edit functionality",
            "category": "goods",
            "offering": ["Fresh Eggs", "Honey"],
            "looking_for": ["Seeds", "Tools"],
            "images": []
        }
        
        response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert response.status_code == 201, f"Create post failed: {response.text}"
        
        data = response.json()
        assert "id" in data
        self.test_post_id = data["id"]
        print(f"Created test post with ID: {self.test_post_id}")
        return self.test_post_id
    
    def test_edit_own_post_success(self):
        """Test that user can edit their own post"""
        # First create a post
        post_data = {
            "title": "TEST_Original Title",
            "description": "Original description",
            "category": "goods",
            "offering": ["Item1"],
            "looking_for": ["Item2"],
            "images": []
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        print(f"Created post {post_id} for edit test")
        
        # Now edit the post
        edit_data = {
            "title": "TEST_Updated Title",
            "description": "Updated description",
            "category": "services",
            "offering": ["Updated Item1", "New Item"],
            "looking_for": ["Updated Item2"]
        }
        
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}", json=edit_data)
        assert edit_response.status_code == 200, f"Edit post failed: {edit_response.text}"
        
        data = edit_response.json()
        assert data.get("message") == "Post updated successfully"
        print(f"Successfully edited post {post_id}")
        
        # Verify the changes by fetching posts
        posts_response = self.session.get(f"{BASE_URL}/api/posts")
        assert posts_response.status_code == 200
        
        posts = posts_response.json()
        edited_post = next((p for p in posts if p["_id"] == post_id), None)
        
        if edited_post:
            assert edited_post["title"] == "TEST_Updated Title"
            assert edited_post["description"] == "Updated description"
            assert edited_post["category"] == "services"
            print(f"Verified post edit - title: {edited_post['title']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")
        return post_id
    
    def test_edit_post_not_found(self):
        """Test editing a non-existent post returns 404"""
        fake_id = "000000000000000000000000"
        
        edit_data = {"title": "TEST_Should Fail"}
        response = self.session.put(f"{BASE_URL}/api/posts/{fake_id}", json=edit_data)
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returned 404 for non-existent post")
    
    def test_edit_others_post_forbidden(self):
        """Test that user cannot edit another user's post (403)"""
        # First, create a post as demo user
        post_data = {
            "title": "TEST_Demo User Post",
            "description": "Post by demo user",
            "category": "goods",
            "offering": ["Item"],
            "looking_for": ["Other Item"],
            "images": []
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]
        print(f"Created post {post_id} as demo user")
        
        # Logout demo user
        self.session.post(f"{BASE_URL}/api/auth/logout")
        
        # Login as admin (different user)
        admin_login = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        assert admin_login.status_code == 200
        print("Logged in as admin user")
        
        # Try to edit demo user's post as admin
        edit_data = {"title": "TEST_Admin Trying to Edit"}
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}", json=edit_data)
        
        assert edit_response.status_code == 403, f"Expected 403, got {edit_response.status_code}: {edit_response.text}"
        print("Correctly returned 403 when admin tries to edit demo user's post")
        
        # Cleanup - login back as demo and delete
        self.session.post(f"{BASE_URL}/api/auth/logout")
        self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")
    
    def test_create_comment_for_edit(self):
        """Create a post and comment for edit testing"""
        # Create post
        post_data = {
            "title": "TEST_Post for Comment Edit",
            "description": "Testing comment edit",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Create comment
        comment_data = {"content": "Original comment content", "parent_id": None}
        comment_response = self.session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_data)
        assert comment_response.status_code == 201, f"Create comment failed: {comment_response.text}"
        
        comment = comment_response.json()
        assert "id" in comment
        print(f"Created comment {comment['id']} on post {post_id}")
        
        return post_id, comment["id"]
    
    def test_edit_own_comment_success(self):
        """Test that user can edit their own comment"""
        # Create post and comment
        post_data = {
            "title": "TEST_Post for Comment Edit Test",
            "description": "Testing",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Create comment
        comment_data = {"content": "Original comment", "parent_id": None}
        comment_response = self.session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_data)
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]
        print(f"Created comment {comment_id}")
        
        # Edit the comment
        edit_data = {"content": "Updated comment content"}
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}", json=edit_data)
        
        assert edit_response.status_code == 200, f"Edit comment failed: {edit_response.text}"
        
        data = edit_response.json()
        assert data.get("content") == "Updated comment content"
        assert "updated_at" in data
        print(f"Successfully edited comment - new content: {data.get('content')}")
        
        # Verify by fetching comments
        comments_response = self.session.get(f"{BASE_URL}/api/posts/{post_id}/comments")
        assert comments_response.status_code == 200
        
        comments = comments_response.json()
        edited_comment = next((c for c in comments if c["id"] == comment_id), None)
        
        if edited_comment:
            assert edited_comment["content"] == "Updated comment content"
            assert edited_comment.get("updated_at") is not None
            print(f"Verified comment edit - has updated_at: {edited_comment.get('updated_at')}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")
    
    def test_edit_comment_empty_content_fails(self):
        """Test that editing comment with empty content fails"""
        # Create post and comment
        post_data = {
            "title": "TEST_Empty Comment Test",
            "description": "Testing",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        comment_data = {"content": "Original", "parent_id": None}
        comment_response = self.session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_data)
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]
        
        # Try to edit with empty content
        edit_data = {"content": ""}
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}", json=edit_data)
        
        assert edit_response.status_code == 400, f"Expected 400, got {edit_response.status_code}"
        print("Correctly rejected empty comment content")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")
    
    def test_edit_others_comment_forbidden(self):
        """Test that user cannot edit another user's comment (403)"""
        # Create post and comment as demo user
        post_data = {
            "title": "TEST_Other User Comment Test",
            "description": "Testing",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        comment_data = {"content": "Demo user comment", "parent_id": None}
        comment_response = self.session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json=comment_data)
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]
        print(f"Created comment {comment_id} as demo user")
        
        # Logout and login as admin
        self.session.post(f"{BASE_URL}/api/auth/logout")
        admin_login = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        assert admin_login.status_code == 200
        
        # Try to edit demo user's comment as admin
        edit_data = {"content": "Admin trying to edit"}
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}", json=edit_data)
        
        assert edit_response.status_code == 403, f"Expected 403, got {edit_response.status_code}: {edit_response.text}"
        print("Correctly returned 403 when admin tries to edit demo user's comment")
        
        # Cleanup
        self.session.post(f"{BASE_URL}/api/auth/logout")
        self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")
    
    def test_edit_comment_not_found(self):
        """Test editing non-existent comment returns 404"""
        # Create a post first
        post_data = {
            "title": "TEST_Comment Not Found Test",
            "description": "Testing",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        fake_comment_id = "000000000000000000000000"
        edit_data = {"content": "Should fail"}
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}/comments/{fake_comment_id}", json=edit_data)
        
        assert edit_response.status_code == 404, f"Expected 404, got {edit_response.status_code}"
        print("Correctly returned 404 for non-existent comment")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")
    
    def test_edit_post_with_category_selector_items(self):
        """Test editing post with CategorySelector-style items (objects with name/description)"""
        # Create post with simple items
        post_data = {
            "title": "TEST_CategorySelector Edit Test",
            "description": "Testing CategorySelector items",
            "category": "goods",
            "offering": ["Simple Item"],
            "looking_for": ["Another Item"],
            "images": []
        }
        
        post_response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Edit with CategorySelector-style items (objects with name, description, quantity)
        edit_data = {
            "title": "TEST_CategorySelector Updated",
            "description": "Updated with CategorySelector items",
            "category": "goods",
            "offering": [
                {"name": "Fresh Eggs", "description": "Free range", "quantity": "1 dozen"},
                {"name": "Honey", "description": "Raw local", "quantity": "1 jar"}
            ],
            "looking_for": [
                {"name": "Seeds", "description": "Heirloom varieties"},
                {"name": "Garden Tools"}
            ]
        }
        
        edit_response = self.session.put(f"{BASE_URL}/api/posts/{post_id}", json=edit_data)
        assert edit_response.status_code == 200, f"Edit with CategorySelector items failed: {edit_response.text}"
        print("Successfully edited post with CategorySelector-style items")
        
        # Verify the items were saved correctly
        posts_response = self.session.get(f"{BASE_URL}/api/posts")
        assert posts_response.status_code == 200
        
        posts = posts_response.json()
        edited_post = next((p for p in posts if p["_id"] == post_id), None)
        
        if edited_post:
            # Check offering items
            offering = edited_post.get("offering", [])
            assert len(offering) == 2
            print(f"Offering items: {offering}")
            
            # Check looking_for items
            looking_for = edited_post.get("looking_for", [])
            assert len(looking_for) == 2
            print(f"Looking for items: {looking_for}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/posts/{post_id}")


class TestEditPostEndpointDirect:
    """Direct endpoint tests for edit functionality"""
    
    def test_put_post_endpoint_exists(self):
        """Verify PUT /api/posts/{post_id} endpoint exists"""
        session = requests.Session()
        
        # Login
        login = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert login.status_code == 200
        
        # Create a post
        post_data = {
            "title": "TEST_Endpoint Test",
            "description": "Testing endpoint",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        create = session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create.status_code == 201
        post_id = create.json()["id"]
        
        # Test PUT endpoint
        put_response = session.put(f"{BASE_URL}/api/posts/{post_id}", json={"title": "TEST_Updated"})
        assert put_response.status_code == 200
        print(f"PUT /api/posts/{post_id} endpoint working correctly")
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/posts/{post_id}")
        session.post(f"{BASE_URL}/api/auth/logout")
    
    def test_put_comment_endpoint_exists(self):
        """Verify PUT /api/posts/{post_id}/comments/{comment_id} endpoint exists"""
        session = requests.Session()
        
        # Login
        login = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert login.status_code == 200
        
        # Create a post
        post_data = {
            "title": "TEST_Comment Endpoint Test",
            "description": "Testing",
            "category": "goods",
            "offering": ["Test"],
            "looking_for": ["Test"],
            "images": []
        }
        
        create_post = session.post(f"{BASE_URL}/api/posts", json=post_data)
        assert create_post.status_code == 201
        post_id = create_post.json()["id"]
        
        # Create a comment
        create_comment = session.post(f"{BASE_URL}/api/posts/{post_id}/comments", json={
            "content": "Test comment",
            "parent_id": None
        })
        assert create_comment.status_code == 201
        comment_id = create_comment.json()["id"]
        
        # Test PUT endpoint
        put_response = session.put(f"{BASE_URL}/api/posts/{post_id}/comments/{comment_id}", json={
            "content": "Updated comment"
        })
        assert put_response.status_code == 200
        print(f"PUT /api/posts/{post_id}/comments/{comment_id} endpoint working correctly")
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/posts/{post_id}")
        session.post(f"{BASE_URL}/api/auth/logout")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
