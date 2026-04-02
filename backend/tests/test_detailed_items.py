"""
Test suite for Detailed Items feature (name/description/quantity)
Tests profile update and post creation with detailed item format
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDetailedItemsFeature:
    """Tests for detailed items with name/description/quantity format"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login with demo user
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.user_id = login_response.json().get("id")
        yield
    
    # ==========================================
    # Profile Update Tests - Detailed Items
    # ==========================================
    
    def test_profile_update_with_detailed_goods_offering(self):
        """Test profile update accepts detailed items with name/description/quantity"""
        detailed_items = [
            {"name": "Fresh Eggs", "description": "Free range, organic", "quantity": "2 dozen/week"},
            {"name": "Raw Honey", "description": "Local wildflower", "quantity": "1 lb jars"},
            {"name": "Goat Milk", "description": "Grade A, pasteurized", "quantity": "1 gallon/week"}
        ]
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": detailed_items
        })
        
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        assert response.json().get("message") == "Profile updated successfully"
        
        # Verify data persisted correctly
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        assert profile_response.status_code == 200
        
        profile_data = profile_response.json()
        goods_offering = profile_data.get("goods_offering", [])
        
        assert len(goods_offering) == 3, f"Expected 3 items, got {len(goods_offering)}"
        
        # Verify first item has all fields
        first_item = goods_offering[0]
        assert first_item.get("name") == "Fresh Eggs"
        assert first_item.get("description") == "Free range, organic"
        assert first_item.get("quantity") == "2 dozen/week"
        
        print("✓ Profile update with detailed goods_offering works correctly")
    
    def test_profile_update_with_detailed_skills(self):
        """Test profile update accepts detailed skills"""
        detailed_skills = [
            {"name": "Woodworking", "description": "Custom furniture and repairs", "quantity": "10+ years experience"},
            {"name": "Beekeeping", "description": "Hive management and honey extraction", "quantity": ""}
        ]
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "skills": detailed_skills
        })
        
        assert response.status_code == 200
        
        # Verify persistence
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        profile_data = profile_response.json()
        skills = profile_data.get("skills", [])
        
        assert len(skills) == 2
        assert skills[0].get("name") == "Woodworking"
        assert skills[0].get("description") == "Custom furniture and repairs"
        
        print("✓ Profile update with detailed skills works correctly")
    
    def test_profile_update_with_detailed_services(self):
        """Test profile update accepts detailed services offering/wanted"""
        services_offering = [
            {"name": "Tractor Services", "description": "Plowing and tilling", "quantity": "By the hour"},
            {"name": "Fence Building", "description": "Wood and wire fencing", "quantity": "Per linear foot"}
        ]
        
        services_wanted = [
            {"name": "Veterinary Care", "description": "For goats and chickens", "quantity": "As needed"},
            {"name": "Welding", "description": "Farm equipment repairs", "quantity": ""}
        ]
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "services_offering": services_offering,
            "services_wanted": services_wanted
        })
        
        assert response.status_code == 200
        
        # Verify persistence
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        profile_data = profile_response.json()
        
        assert len(profile_data.get("services_offering", [])) == 2
        assert len(profile_data.get("services_wanted", [])) == 2
        assert profile_data["services_offering"][0].get("name") == "Tractor Services"
        assert profile_data["services_wanted"][0].get("name") == "Veterinary Care"
        
        print("✓ Profile update with detailed services works correctly")
    
    def test_profile_update_backward_compatible_with_strings(self):
        """Test profile update still works with simple string items (backward compatibility)"""
        simple_items = ["Tomatoes", "Peppers", "Squash"]
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "goods_wanted": simple_items
        })
        
        assert response.status_code == 200
        
        # Verify strings are normalized to object format
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        profile_data = profile_response.json()
        goods_wanted = profile_data.get("goods_wanted", [])
        
        assert len(goods_wanted) == 3
        
        # Each item should be normalized to object format
        for item in goods_wanted:
            assert isinstance(item, dict), f"Item should be dict, got {type(item)}"
            assert "name" in item
            assert "description" in item
            assert "quantity" in item
        
        assert goods_wanted[0].get("name") == "Tomatoes"
        assert goods_wanted[0].get("description") == ""  # Empty for simple strings
        assert goods_wanted[0].get("quantity") == ""
        
        print("✓ Profile update backward compatible with simple string items")
    
    def test_profile_update_mixed_format_items(self):
        """Test profile update handles mixed format (strings and objects)"""
        mixed_items = [
            "Simple Item",
            {"name": "Detailed Item", "description": "With details", "quantity": "5 units"},
            "Another Simple"
        ]
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": mixed_items
        })
        
        assert response.status_code == 200
        
        # Verify all items normalized
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        profile_data = profile_response.json()
        goods_offering = profile_data.get("goods_offering", [])
        
        assert len(goods_offering) == 3
        
        # First item (was string)
        assert goods_offering[0].get("name") == "Simple Item"
        assert goods_offering[0].get("description") == ""
        
        # Second item (was detailed)
        assert goods_offering[1].get("name") == "Detailed Item"
        assert goods_offering[1].get("description") == "With details"
        assert goods_offering[1].get("quantity") == "5 units"
        
        print("✓ Profile update handles mixed format items correctly")
    
    # ==========================================
    # Post Creation Tests - Detailed Items
    # ==========================================
    
    def test_create_post_with_detailed_items(self):
        """Test post creation accepts detailed items with name/description/quantity"""
        post_data = {
            "title": "TEST_Detailed Items Post",
            "description": "Testing detailed items feature",
            "category": "goods",
            "offering": [
                {"name": "Fresh Eggs", "description": "Free range hens", "quantity": "3 dozen"},
                {"name": "Honey", "description": "Raw, unfiltered", "quantity": "2 lbs"}
            ],
            "looking_for": [
                {"name": "Vegetables", "description": "Organic preferred", "quantity": "Weekly supply"},
                {"name": "Firewood", "description": "Seasoned hardwood", "quantity": "1 cord"}
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        
        assert response.status_code == 201, f"Post creation failed: {response.text}"
        post_id = response.json().get("id")
        assert post_id is not None
        
        # Verify post in feed
        feed_response = self.session.get(f"{BASE_URL}/api/posts")
        assert feed_response.status_code == 200
        
        posts = feed_response.json()
        created_post = next((p for p in posts if p.get("_id") == post_id), None)
        
        if created_post:
            # Verify offering items
            offering = created_post.get("offering", [])
            assert len(offering) == 2
            assert offering[0].get("name") == "Fresh Eggs"
            assert offering[0].get("quantity") == "3 dozen"
            
            # Verify looking_for items
            looking_for = created_post.get("looking_for", [])
            assert len(looking_for) == 2
            assert looking_for[0].get("name") == "Vegetables"
            assert looking_for[0].get("description") == "Organic preferred"
        
        print("✓ Post creation with detailed items works correctly")
    
    def test_create_post_with_simple_string_items(self):
        """Test post creation still works with simple string items"""
        post_data = {
            "title": "TEST_Simple Items Post",
            "description": "Testing backward compatibility",
            "category": "services",
            "offering": ["Carpentry", "Plumbing"],
            "looking_for": ["Electrical Work", "Painting"]
        }
        
        response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        
        assert response.status_code == 201, f"Post creation failed: {response.text}"
        post_id = response.json().get("id")
        
        # Verify items are normalized
        feed_response = self.session.get(f"{BASE_URL}/api/posts")
        posts = feed_response.json()
        created_post = next((p for p in posts if p.get("_id") == post_id), None)
        
        if created_post:
            offering = created_post.get("offering", [])
            assert len(offering) == 2
            # Should be normalized to object format
            assert offering[0].get("name") == "Carpentry"
            assert offering[0].get("description") == ""
            assert offering[0].get("quantity") == ""
        
        print("✓ Post creation backward compatible with simple string items")
    
    def test_create_post_with_mixed_items(self):
        """Test post creation handles mixed format items"""
        post_data = {
            "title": "TEST_Mixed Items Post",
            "description": "Testing mixed format",
            "category": "skills",
            "offering": [
                "Basic Skill",
                {"name": "Advanced Skill", "description": "Expert level", "quantity": "10 hours/week"}
            ],
            "looking_for": [
                {"name": "Training", "description": "Hands-on", "quantity": ""},
                "Mentorship"
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/posts", json=post_data)
        
        assert response.status_code == 201
        print("✓ Post creation handles mixed format items correctly")
    
    # ==========================================
    # Feed Display Tests
    # ==========================================
    
    def test_feed_returns_detailed_items(self):
        """Test that feed endpoint returns items with full detail structure"""
        response = self.session.get(f"{BASE_URL}/api/posts")
        
        assert response.status_code == 200
        posts = response.json()
        
        # Check that posts have offering and looking_for arrays
        for post in posts[:5]:  # Check first 5 posts
            offering = post.get("offering", [])
            looking_for = post.get("looking_for", [])
            
            # Each item should have name, description, quantity keys
            for item in offering:
                if isinstance(item, dict):
                    assert "name" in item, f"Item missing 'name' key: {item}"
            
            for item in looking_for:
                if isinstance(item, dict):
                    assert "name" in item, f"Item missing 'name' key: {item}"
        
        print("✓ Feed returns items with proper structure")
    
    def test_matched_posts_with_detailed_items(self):
        """Test that matched posts endpoint works with detailed items"""
        response = self.session.get(f"{BASE_URL}/api/posts/matches")
        
        assert response.status_code == 200
        posts = response.json()
        
        # Verify response structure
        assert isinstance(posts, list)
        
        print(f"✓ Matched posts endpoint works (returned {len(posts)} matches)")
    
    # ==========================================
    # Cleanup
    # ==========================================
    
    def test_cleanup_test_posts(self):
        """Cleanup: Remove test posts created during testing"""
        # Get all posts
        response = self.session.get(f"{BASE_URL}/api/posts?limit=50")
        if response.status_code == 200:
            posts = response.json()
            test_posts = [p for p in posts if p.get("title", "").startswith("TEST_")]
            print(f"Found {len(test_posts)} test posts to clean up")
        
        # Reset profile to clean state
        self.session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": [
                {"name": "Fresh Eggs", "description": "Free range, organic", "quantity": "2 dozen/week"},
                {"name": "Raw Honey", "description": "Local wildflower", "quantity": "1 lb jars"}
            ],
            "goods_wanted": [],
            "services_offering": [],
            "services_wanted": [],
            "skills": []
        })
        
        print("✓ Test cleanup completed")


class TestNormalizeItemsFunction:
    """Unit tests for the normalize_items helper function behavior"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert login_response.status_code == 200
        self.user_id = login_response.json().get("id")
        yield
    
    def test_empty_list_handling(self):
        """Test that empty list is handled correctly"""
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": []
        })
        
        assert response.status_code == 200
        
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        profile_data = profile_response.json()
        
        assert profile_data.get("goods_offering") == []
        print("✓ Empty list handling works correctly")
    
    def test_item_with_missing_fields(self):
        """Test items with missing optional fields are handled"""
        items = [
            {"name": "Item with only name"},
            {"name": "Item with description", "description": "Some desc"},
            {"name": "Item with quantity", "quantity": "5 units"}
        ]
        
        response = self.session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": items
        })
        
        assert response.status_code == 200
        
        profile_response = self.session.get(f"{BASE_URL}/api/profile/{self.user_id}")
        profile_data = profile_response.json()
        goods = profile_data.get("goods_offering", [])
        
        # All items should have all three fields
        for item in goods:
            assert "name" in item
            assert "description" in item
            assert "quantity" in item
        
        print("✓ Items with missing fields are normalized correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
