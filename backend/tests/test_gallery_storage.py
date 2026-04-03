"""
Test Gallery and Object Storage Features for Rebel Trade Network
Tests: Gallery upload, like, comment, threading, file validation, cross-user access
"""
import pytest
import requests
import os
import io
from PIL import Image

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "williamrhodes764@protonmail.com"
ADMIN_PASSWORD = "Peaches1776@"
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Authenticated session for admin user (Billy)"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.text}")
    return session


@pytest.fixture(scope="module")
def demo_session():
    """Authenticated session for demo user"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Demo login failed: {response.text}")
    return session


@pytest.fixture(scope="module")
def admin_user_id(admin_session):
    """Get admin user ID"""
    response = admin_session.get(f"{BASE_URL}/api/auth/me")
    if response.status_code == 200:
        return response.json().get("id")
    pytest.skip("Could not get admin user ID")


@pytest.fixture(scope="module")
def demo_user_id(demo_session):
    """Get demo user ID"""
    response = demo_session.get(f"{BASE_URL}/api/auth/me")
    if response.status_code == 200:
        return response.json().get("id")
    pytest.skip("Could not get demo user ID")


def create_test_image():
    """Create a small test image in memory"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


class TestGalleryUpload:
    """Gallery upload endpoint tests"""
    
    def test_gallery_upload_requires_auth(self, api_client):
        """Test that gallery upload requires authentication"""
        img = create_test_image()
        files = {'file': ('test.png', img, 'image/png')}
        response = api_client.post(f"{BASE_URL}/api/gallery/upload", files=files)
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Gallery upload requires authentication")
    
    def test_gallery_upload_image(self, demo_session):
        """Test uploading an image to gallery"""
        img = create_test_image()
        files = {'file': ('test_gallery.png', img, 'image/png')}
        data = {'caption': 'TEST_gallery_image'}
        response = demo_session.post(f"{BASE_URL}/api/gallery/upload", files=files, data=data)
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        result = response.json()
        assert 'id' in result, "Response should contain id"
        assert 'url' in result, "Response should contain url"
        assert result.get('is_video') == False, "Should not be marked as video"
        assert result.get('caption') == 'TEST_gallery_image', "Caption should match"
        print(f"PASS: Gallery image uploaded successfully, id={result['id']}")
        return result['id']
    
    def test_gallery_upload_invalid_file_type(self, demo_session):
        """Test that invalid file types are rejected"""
        # Create a fake text file
        fake_file = io.BytesIO(b"This is not an image")
        files = {'file': ('test.txt', fake_file, 'text/plain')}
        response = demo_session.post(f"{BASE_URL}/api/gallery/upload", files=files)
        assert response.status_code == 400, f"Expected 400 for invalid file type, got {response.status_code}"
        print("PASS: Invalid file type rejected")


class TestGalleryRetrieval:
    """Gallery retrieval endpoint tests"""
    
    def test_get_user_gallery(self, demo_session, demo_user_id):
        """Test getting a user's gallery"""
        response = demo_session.get(f"{BASE_URL}/api/gallery/{demo_user_id}")
        assert response.status_code == 200, f"Failed to get gallery: {response.text}"
        
        data = response.json()
        assert 'items' in data, "Response should contain items"
        assert 'user_name' in data, "Response should contain user_name"
        assert 'total' in data, "Response should contain total count"
        print(f"PASS: Retrieved gallery with {len(data['items'])} items")
    
    def test_get_gallery_item_details(self, demo_session, demo_user_id):
        """Test getting a single gallery item with full details"""
        # First get the gallery to find an item
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{demo_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        response = demo_session.get(f"{BASE_URL}/api/gallery/item/{item_id}")
        assert response.status_code == 200, f"Failed to get item: {response.text}"
        
        data = response.json()
        assert 'id' in data, "Response should contain id"
        assert 'url' in data, "Response should contain url"
        assert 'comments' in data, "Response should contain comments"
        assert 'like_count' in data, "Response should contain like_count"
        print(f"PASS: Retrieved gallery item details for {item_id}")
    
    def test_get_nonexistent_gallery_item(self, demo_session):
        """Test getting a non-existent gallery item returns 404"""
        response = demo_session.get(f"{BASE_URL}/api/gallery/item/nonexistent-id-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent gallery item returns 404")


class TestGalleryLikes:
    """Gallery like/unlike endpoint tests"""
    
    def test_like_gallery_item(self, demo_session, admin_user_id):
        """Test liking a gallery item"""
        # Get admin's gallery (Billy has items)
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test likes")
        
        item_id = gallery_response.json()['items'][0]['id']
        
        # Like the item
        response = demo_session.post(f"{BASE_URL}/api/gallery/{item_id}/like")
        assert response.status_code == 200, f"Like failed: {response.text}"
        
        data = response.json()
        assert 'action' in data, "Response should contain action"
        assert 'like_count' in data, "Response should contain like_count"
        print(f"PASS: Gallery item {data['action']}, like_count={data['like_count']}")
    
    def test_unlike_gallery_item(self, demo_session, admin_user_id):
        """Test unliking a gallery item (toggle)"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        
        # Toggle like twice to test unlike
        demo_session.post(f"{BASE_URL}/api/gallery/{item_id}/like")  # First toggle
        response = demo_session.post(f"{BASE_URL}/api/gallery/{item_id}/like")  # Second toggle
        assert response.status_code == 200, f"Unlike failed: {response.text}"
        print(f"PASS: Gallery item like toggled, action={response.json()['action']}")
    
    def test_like_requires_auth(self, api_client, admin_user_id):
        """Test that liking requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/gallery/fake-item-id/like")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Like requires authentication")


class TestGalleryComments:
    """Gallery comment endpoint tests including threading"""
    
    def test_add_comment_to_gallery_item(self, demo_session, admin_user_id):
        """Test adding a comment to a gallery item"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test comments")
        
        item_id = gallery_response.json()['items'][0]['id']
        
        response = demo_session.post(
            f"{BASE_URL}/api/gallery/{item_id}/comment",
            json={"content": "TEST_comment_on_gallery"}
        )
        assert response.status_code == 200, f"Comment failed: {response.text}"
        
        data = response.json()
        assert 'id' in data, "Response should contain comment id"
        assert 'content' in data, "Response should contain content"
        assert data['content'] == "TEST_comment_on_gallery"
        assert data.get('parent_id') is None, "Top-level comment should have no parent"
        print(f"PASS: Comment added to gallery item, comment_id={data['id']}")
        return data['id']
    
    def test_reply_to_gallery_comment(self, demo_session, admin_user_id):
        """Test replying to a comment (threading)"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        
        # First add a parent comment
        parent_response = demo_session.post(
            f"{BASE_URL}/api/gallery/{item_id}/comment",
            json={"content": "TEST_parent_comment"}
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()['id']
        
        # Now reply to it
        reply_response = demo_session.post(
            f"{BASE_URL}/api/gallery/{item_id}/comment",
            json={"content": "TEST_reply_comment", "parent_id": parent_id}
        )
        assert reply_response.status_code == 200, f"Reply failed: {reply_response.text}"
        
        reply_data = reply_response.json()
        assert reply_data['parent_id'] == parent_id, "Reply should reference parent"
        print(f"PASS: Reply added to comment, parent_id={parent_id}")
    
    def test_reply_to_nonexistent_comment(self, demo_session, admin_user_id):
        """Test replying to a non-existent comment returns 404"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        
        response = demo_session.post(
            f"{BASE_URL}/api/gallery/{item_id}/comment",
            json={"content": "TEST_reply", "parent_id": "nonexistent-comment-id"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Reply to non-existent comment returns 404")
    
    def test_comment_requires_auth(self, api_client):
        """Test that commenting requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/gallery/fake-item-id/comment",
            json={"content": "test"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASS: Comment requires authentication")


class TestCrossUserGalleryAccess:
    """Test cross-user gallery access"""
    
    def test_user_can_view_other_user_gallery(self, demo_session, admin_user_id):
        """Test that demo user can view admin's gallery"""
        response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        assert response.status_code == 200, f"Failed to view other user's gallery: {response.text}"
        print("PASS: User can view other user's gallery")
    
    def test_user_can_like_other_user_gallery_item(self, demo_session, admin_user_id):
        """Test that demo user can like admin's gallery item"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        response = demo_session.post(f"{BASE_URL}/api/gallery/{item_id}/like")
        assert response.status_code == 200, f"Failed to like other user's item: {response.text}"
        print("PASS: User can like other user's gallery item")
    
    def test_user_can_comment_on_other_user_gallery_item(self, demo_session, admin_user_id):
        """Test that demo user can comment on admin's gallery item"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        response = demo_session.post(
            f"{BASE_URL}/api/gallery/{item_id}/comment",
            json={"content": "TEST_cross_user_comment"}
        )
        assert response.status_code == 200, f"Failed to comment on other user's item: {response.text}"
        print("PASS: User can comment on other user's gallery item")


class TestFileServing:
    """Test file serving from object storage"""
    
    def test_file_endpoint_serves_gallery_files(self, demo_session, admin_user_id):
        """Test that /api/files/ endpoint serves gallery files"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test file serving")
        
        item = gallery_response.json()['items'][0]
        file_url = item['url']
        
        # The URL should be like /api/files/rebel-trade-network/gallery/...
        response = demo_session.get(f"{BASE_URL}{file_url}")
        assert response.status_code == 200, f"Failed to serve file: {response.status_code}"
        assert len(response.content) > 0, "File content should not be empty"
        print(f"PASS: File served successfully from {file_url}")
    
    def test_nonexistent_file_returns_404(self, demo_session):
        """Test that non-existent file returns 404"""
        response = demo_session.get(f"{BASE_URL}/api/files/nonexistent/path/file.jpg")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent file returns 404")


class TestAvatarUpload:
    """Test avatar upload with object storage"""
    
    def test_avatar_upload(self, demo_session):
        """Test uploading an avatar"""
        img = create_test_image()
        files = {'file': ('avatar.png', img, 'image/png')}
        data = {'category': 'avatar'}
        response = demo_session.post(f"{BASE_URL}/api/upload", files=files, data=data)
        assert response.status_code == 200, f"Avatar upload failed: {response.text}"
        
        result = response.json()
        assert 'url' in result, "Response should contain url"
        print(f"PASS: Avatar uploaded successfully, url={result['url']}")
    
    def test_avatar_upload_invalid_type(self, demo_session):
        """Test that invalid avatar types are rejected"""
        fake_file = io.BytesIO(b"Not an image")
        files = {'file': ('avatar.txt', fake_file, 'text/plain')}
        data = {'category': 'avatar'}
        response = demo_session.post(f"{BASE_URL}/api/upload", files=files, data=data)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: Invalid avatar type rejected")


class TestGalleryDeletion:
    """Test gallery item deletion"""
    
    def test_delete_own_gallery_item(self, demo_session, demo_user_id):
        """Test deleting own gallery item"""
        # First upload an item to delete
        img = create_test_image()
        files = {'file': ('to_delete.png', img, 'image/png')}
        data = {'caption': 'TEST_to_delete'}
        upload_response = demo_session.post(f"{BASE_URL}/api/gallery/upload", files=files, data=data)
        
        if upload_response.status_code != 200:
            pytest.skip("Could not upload item to test deletion")
        
        item_id = upload_response.json()['id']
        
        # Now delete it
        delete_response = demo_session.delete(f"{BASE_URL}/api/gallery/{item_id}")
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        # Verify it's deleted (should return 404)
        get_response = demo_session.get(f"{BASE_URL}/api/gallery/item/{item_id}")
        assert get_response.status_code == 404, "Deleted item should return 404"
        print(f"PASS: Gallery item deleted successfully")
    
    def test_cannot_delete_other_user_gallery_item(self, demo_session, admin_user_id):
        """Test that user cannot delete another user's gallery item"""
        gallery_response = demo_session.get(f"{BASE_URL}/api/gallery/{admin_user_id}")
        if gallery_response.status_code != 200 or not gallery_response.json().get('items'):
            pytest.skip("No gallery items to test")
        
        item_id = gallery_response.json()['items'][0]['id']
        response = demo_session.delete(f"{BASE_URL}/api/gallery/{item_id}")
        assert response.status_code in [403, 401], f"Expected 403/401, got {response.status_code}"
        print("PASS: Cannot delete other user's gallery item")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
