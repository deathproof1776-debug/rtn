"""
Test Video Upload and Gallery Bug Fixes
Tests:
1. Community Board video upload - CreateCommunityPostModal should accept image/* and video/* files
2. Gallery user endpoint - GET /api/gallery/user/{user_id} returns user's gallery items
3. File retrieval - GET /api/files/{path} returns actual file content
4. Upload endpoint returns is_video flag based on content type
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVideoGalleryBugFixes:
    """Test video upload and gallery bug fixes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as demo user
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "demo@rebeltrade.net", "password": "demo123"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.user_data = login_response.json()
        self.user_id = self.user_data.get("id")
        
    # ============ Gallery User Endpoint Tests ============
    
    def test_gallery_user_endpoint_exists(self):
        """Test GET /api/gallery/user/{user_id} endpoint exists and returns data"""
        response = self.session.get(f"{BASE_URL}/api/gallery/user/{self.user_id}")
        assert response.status_code == 200, f"Gallery user endpoint failed: {response.text}"
        
        data = response.json()
        assert "items" in data, "Response should contain 'items' key"
        assert "user_name" in data, "Response should contain 'user_name' key"
        assert isinstance(data["items"], list), "Items should be a list"
        
    def test_gallery_user_endpoint_returns_correct_structure(self):
        """Test gallery user endpoint returns correct item structure"""
        response = self.session.get(f"{BASE_URL}/api/gallery/user/{self.user_id}")
        assert response.status_code == 200
        
        data = response.json()
        if len(data["items"]) > 0:
            item = data["items"][0]
            # Check required fields
            assert "id" in item, "Item should have 'id'"
            assert "url" in item, "Item should have 'url'"
            assert "is_video" in item, "Item should have 'is_video' flag"
            assert "user_id" in item, "Item should have 'user_id'"
            assert "is_liked" in item, "Item should have 'is_liked' flag"
            
    def test_gallery_user_endpoint_404_for_invalid_user(self):
        """Test gallery user endpoint returns 404 for non-existent user"""
        response = self.session.get(f"{BASE_URL}/api/gallery/user/000000000000000000000000")
        assert response.status_code == 404, "Should return 404 for invalid user"
        
    # ============ Upload Endpoint Tests ============
    
    def test_upload_image_returns_is_video_false(self):
        """Test upload endpoint returns is_video=false for images"""
        # Create a minimal valid PNG file (1x1 pixel)
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,  # bit depth, color type, etc
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,  # compressed data
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,  # more data
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND chunk
            0x44, 0xAE, 0x42, 0x60, 0x82                      # IEND CRC
        ])
        
        files = {'file': ('test_image.png', io.BytesIO(png_data), 'image/png')}
        data = {'category': 'community'}
        
        response = self.session.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        
        result = response.json()
        assert "is_video" in result, "Response should contain 'is_video' flag"
        assert result["is_video"] == False, "Image upload should have is_video=false"
        assert "url" in result, "Response should contain 'url'"
        
    def test_upload_video_returns_is_video_true(self):
        """Test upload endpoint returns is_video=true for videos"""
        # Create a minimal MP4 file header (ftyp box)
        mp4_data = bytes([
            0x00, 0x00, 0x00, 0x18,  # box size (24 bytes)
            0x66, 0x74, 0x79, 0x70,  # 'ftyp'
            0x69, 0x73, 0x6F, 0x6D,  # 'isom' brand
            0x00, 0x00, 0x00, 0x00,  # minor version
            0x69, 0x73, 0x6F, 0x6D,  # compatible brand 'isom'
            0x61, 0x76, 0x63, 0x31,  # compatible brand 'avc1'
        ])
        
        files = {'file': ('test_video.mp4', io.BytesIO(mp4_data), 'video/mp4')}
        data = {'category': 'community'}
        
        response = self.session.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
        assert response.status_code == 200, f"Video upload failed: {response.text}"
        
        result = response.json()
        assert "is_video" in result, "Response should contain 'is_video' flag"
        assert result["is_video"] == True, "Video upload should have is_video=true"
        
    # ============ File Retrieval Tests ============
    
    def test_file_retrieval_endpoint(self):
        """Test GET /api/files/{path} returns file content"""
        # First upload a file
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('test_retrieval.png', io.BytesIO(png_data), 'image/png')}
        data = {'category': 'community'}
        
        upload_response = self.session.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
        assert upload_response.status_code == 200
        
        url = upload_response.json()["url"]
        
        # Now retrieve the file
        file_response = self.session.get(f"{BASE_URL}{url}")
        assert file_response.status_code == 200, f"File retrieval failed: {file_response.status_code}"
        assert len(file_response.content) > 0, "File content should not be empty"
        
    def test_file_retrieval_requires_auth(self):
        """Test file retrieval requires authentication for non-avatar files"""
        # Create a new session without auth
        unauth_session = requests.Session()
        
        # Try to access a non-avatar file path
        response = unauth_session.get(
            f"{BASE_URL}/api/files/rebel-trade-network/community/test/test.png"
        )
        assert response.status_code == 401, "Should require authentication"
        
    # ============ Gallery Upload Tests ============
    
    def test_gallery_upload_image(self):
        """Test gallery upload endpoint for images"""
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('TEST_gallery_image.png', io.BytesIO(png_data), 'image/png')}
        data = {'caption': 'TEST_gallery_upload_image'}
        
        response = self.session.post(
            f"{BASE_URL}/api/gallery/upload",
            files=files,
            data=data
        )
        assert response.status_code == 200, f"Gallery upload failed: {response.text}"
        
        result = response.json()
        assert "id" in result, "Response should contain 'id'"
        assert "url" in result, "Response should contain 'url'"
        assert "is_video" in result, "Response should contain 'is_video'"
        assert result["is_video"] == False, "Image should have is_video=false"
        
    def test_gallery_upload_video(self):
        """Test gallery upload endpoint for videos"""
        mp4_data = bytes([
            0x00, 0x00, 0x00, 0x18,
            0x66, 0x74, 0x79, 0x70,
            0x69, 0x73, 0x6F, 0x6D,
            0x00, 0x00, 0x00, 0x00,
            0x69, 0x73, 0x6F, 0x6D,
            0x61, 0x76, 0x63, 0x31,
        ])
        
        files = {'file': ('TEST_gallery_video.mp4', io.BytesIO(mp4_data), 'video/mp4')}
        data = {'caption': 'TEST_gallery_upload_video'}
        
        response = self.session.post(
            f"{BASE_URL}/api/gallery/upload",
            files=files,
            data=data
        )
        assert response.status_code == 200, f"Gallery video upload failed: {response.text}"
        
        result = response.json()
        assert result["is_video"] == True, "Video should have is_video=true"
        
    # ============ Community Post with Media Tests ============
    
    def test_community_post_with_image(self):
        """Test creating community post with image"""
        # First upload an image
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
            0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
            0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
            0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        
        files = {'file': ('test_community_image.png', io.BytesIO(png_data), 'image/png')}
        data = {'category': 'community'}
        
        upload_response = self.session.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
        assert upload_response.status_code == 200
        image_url = upload_response.json()["url"]
        
        # Create community post with image
        post_data = {
            "title": "TEST_Community Post with Image",
            "content": "This is a test post with an image attachment",
            "topic": "general",
            "images": [image_url]
        }
        
        post_response = self.session.post(
            f"{BASE_URL}/api/community",
            json=post_data
        )
        assert post_response.status_code in [200, 201], f"Community post failed: {post_response.text}"
        
        result = post_response.json()
        assert "id" in result, "Response should contain post 'id'"
        
    def test_community_post_with_video(self):
        """Test creating community post with video"""
        # First upload a video
        mp4_data = bytes([
            0x00, 0x00, 0x00, 0x18,
            0x66, 0x74, 0x79, 0x70,
            0x69, 0x73, 0x6F, 0x6D,
            0x00, 0x00, 0x00, 0x00,
            0x69, 0x73, 0x6F, 0x6D,
            0x61, 0x76, 0x63, 0x31,
        ])
        
        files = {'file': ('test_community_video.mp4', io.BytesIO(mp4_data), 'video/mp4')}
        data = {'category': 'community'}
        
        upload_response = self.session.post(
            f"{BASE_URL}/api/upload",
            files=files,
            data=data
        )
        assert upload_response.status_code == 200
        video_url = upload_response.json()["url"]
        is_video = upload_response.json()["is_video"]
        
        assert is_video == True, "Video upload should return is_video=true"
        
        # Create community post with video
        post_data = {
            "title": "TEST_Community Post with Video",
            "content": "This is a test post with a video attachment",
            "topic": "general",
            "images": [video_url]
        }
        
        post_response = self.session.post(
            f"{BASE_URL}/api/community",
            json=post_data
        )
        assert post_response.status_code in [200, 201], f"Community post with video failed: {post_response.text}"


class TestGalleryItemEndpoint:
    """Test gallery item endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as demo user
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "demo@rebeltrade.net", "password": "demo123"}
        )
        assert login_response.status_code == 200
        self.user_data = login_response.json()
        self.user_id = self.user_data.get("id")
        
    def test_gallery_item_endpoint(self):
        """Test GET /api/gallery/item/{item_id} returns item details"""
        # First get gallery items
        gallery_response = self.session.get(f"{BASE_URL}/api/gallery/user/{self.user_id}")
        assert gallery_response.status_code == 200
        
        items = gallery_response.json()["items"]
        if len(items) > 0:
            item_id = items[0]["id"]
            
            # Get item details
            item_response = self.session.get(f"{BASE_URL}/api/gallery/item/{item_id}")
            assert item_response.status_code == 200
            
            item = item_response.json()
            assert "id" in item
            assert "url" in item
            assert "is_video" in item
            assert "comments" in item
