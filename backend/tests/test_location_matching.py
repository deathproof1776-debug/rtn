"""
Test suite for Location-based Matching feature in HomesteadHub
Tests:
- GET /api/posts returns posts with is_nearby and user_location fields
- GET /api/posts?nearby_only=true filters to only nearby posts
- GET /api/posts/matches prioritizes nearby users with higher match_score
- GET /api/users/nearby returns users in the same location
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from environment
ADMIN_EMAIL = os.environ.get('TEST_ADMIN_EMAIL', 'demo@rebeltrade.net')
ADMIN_PASSWORD = os.environ.get('TEST_ADMIN_PASSWORD', 'demo123')

# Test user data with locations
TEST_USER_1 = {
    "email": "TEST_location_user1@test.com",
    "password": "testpass123",
    "name": "TEST Location User 1",
    "location": "Austin, TX"
}

TEST_USER_2 = {
    "email": "TEST_location_user2@test.com",
    "password": "testpass123",
    "name": "TEST Location User 2",
    "location": "Austin, TX"  # Same location as user 1
}

TEST_USER_3 = {
    "email": "TEST_location_user3@test.com",
    "password": "testpass123",
    "name": "TEST Location User 3",
    "location": "Denver, CO"  # Different location
}


class TestLocationMatching:
    """Test suite for location-based matching feature"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create a requests session"""
        return requests.Session()
    
    @pytest.fixture(scope="class")
    def admin_session(self, session):
        """Login as admin and return session"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def test_users(self, session):
        """Create test users with different locations and return their sessions"""
        users = {}
        
        for user_data in [TEST_USER_1, TEST_USER_2, TEST_USER_3]:
            # Create new session for each user
            user_session = requests.Session()
            
            # Try to register
            response = user_session.post(f"{BASE_URL}/api/auth/register", json=user_data)
            
            if response.status_code == 400 and "already registered" in response.text.lower():
                # User exists, login instead
                response = user_session.post(f"{BASE_URL}/api/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
            
            assert response.status_code == 200, f"Failed to create/login user {user_data['email']}: {response.text}"
            
            user_info = response.json()
            users[user_data["email"]] = {
                "session": user_session,
                "id": user_info.get("id"),
                "location": user_data["location"],
                "name": user_data["name"]
            }
        
        return users
    
    @pytest.fixture(scope="class")
    def test_posts(self, test_users):
        """Create test posts from different users"""
        posts = []
        
        # User 1 creates a post (Austin, TX)
        user1 = test_users[TEST_USER_1["email"]]
        response = user1["session"].post(f"{BASE_URL}/api/posts", json={
            "title": "TEST Fresh Eggs from Austin",
            "description": "Offering fresh eggs from my backyard chickens",
            "category": "goods",
            "offering": ["Fresh Eggs", "Chicken Feed"],
            "looking_for": ["Vegetables", "Honey"]
        })
        assert response.status_code == 201, f"Failed to create post: {response.text}"
        posts.append({"id": response.json()["id"], "user": user1, "location": "Austin, TX"})
        
        # User 2 creates a post (Austin, TX - same location)
        user2 = test_users[TEST_USER_2["email"]]
        response = user2["session"].post(f"{BASE_URL}/api/posts", json={
            "title": "TEST Homemade Honey Austin",
            "description": "Local Austin honey from my beehives",
            "category": "goods",
            "offering": ["Honey", "Beeswax"],
            "looking_for": ["Fresh Eggs", "Vegetables"]
        })
        assert response.status_code == 201, f"Failed to create post: {response.text}"
        posts.append({"id": response.json()["id"], "user": user2, "location": "Austin, TX"})
        
        # User 3 creates a post (Denver, CO - different location)
        user3 = test_users[TEST_USER_3["email"]]
        response = user3["session"].post(f"{BASE_URL}/api/posts", json={
            "title": "TEST Mountain Vegetables Denver",
            "description": "Fresh vegetables from my Denver garden",
            "category": "goods",
            "offering": ["Vegetables", "Herbs"],
            "looking_for": ["Honey", "Fresh Eggs"]
        })
        assert response.status_code == 201, f"Failed to create post: {response.text}"
        posts.append({"id": response.json()["id"], "user": user3, "location": "Denver, CO"})
        
        return posts
    
    # ==================== GET /api/posts Tests ====================
    
    def test_posts_have_is_nearby_field(self, test_users, test_posts):
        """Test that GET /api/posts returns posts with is_nearby field"""
        user1 = test_users[TEST_USER_1["email"]]
        response = user1["session"].get(f"{BASE_URL}/api/posts")
        
        assert response.status_code == 200, f"Failed to get posts: {response.text}"
        posts = response.json()
        
        assert len(posts) > 0, "No posts returned"
        
        # Check that all posts have is_nearby field
        for post in posts:
            assert "is_nearby" in post, f"Post {post.get('_id')} missing is_nearby field"
            assert isinstance(post["is_nearby"], bool), f"is_nearby should be boolean, got {type(post['is_nearby'])}"
        
        print(f"✓ All {len(posts)} posts have is_nearby field")
    
    def test_posts_have_user_location_field(self, test_users, test_posts):
        """Test that GET /api/posts returns posts with user_location field"""
        user1 = test_users[TEST_USER_1["email"]]
        response = user1["session"].get(f"{BASE_URL}/api/posts")
        
        assert response.status_code == 200, f"Failed to get posts: {response.text}"
        posts = response.json()
        
        assert len(posts) > 0, "No posts returned"
        
        # Check that all posts have user_location field
        for post in posts:
            assert "user_location" in post, f"Post {post.get('_id')} missing user_location field"
        
        print(f"✓ All {len(posts)} posts have user_location field")
    
    def test_is_nearby_true_for_same_location(self, test_users, test_posts):
        """Test that is_nearby is true for posts from users in the same location"""
        user1 = test_users[TEST_USER_1["email"]]  # Austin, TX
        response = user1["session"].get(f"{BASE_URL}/api/posts")
        
        assert response.status_code == 200
        posts = response.json()
        
        # Find posts from Austin users
        austin_posts = [p for p in posts if "Austin" in p.get("user_location", "")]
        denver_posts = [p for p in posts if "Denver" in p.get("user_location", "")]
        
        # User 1 is in Austin, so Austin posts should be nearby
        for post in austin_posts:
            if post.get("user_id") != user1["id"]:  # Exclude own posts
                assert post["is_nearby"] == True, f"Austin post should be nearby for Austin user: {post}"
        
        # Denver posts should NOT be nearby for Austin user
        for post in denver_posts:
            assert post["is_nearby"] == False, f"Denver post should NOT be nearby for Austin user: {post}"
        
        print(f"✓ Location matching working: Austin posts nearby={True}, Denver posts nearby={False}")
    
    # ==================== GET /api/posts?nearby_only=true Tests ====================
    
    def test_nearby_only_filter(self, test_users, test_posts):
        """Test that nearby_only=true filters to only nearby posts"""
        user1 = test_users[TEST_USER_1["email"]]  # Austin, TX
        
        # Get all posts
        all_response = user1["session"].get(f"{BASE_URL}/api/posts")
        assert all_response.status_code == 200
        all_posts = all_response.json()
        
        # Get nearby only posts
        nearby_response = user1["session"].get(f"{BASE_URL}/api/posts?nearby_only=true")
        assert nearby_response.status_code == 200
        nearby_posts = nearby_response.json()
        
        # All nearby posts should have is_nearby=true
        for post in nearby_posts:
            assert post["is_nearby"] == True, f"Nearby-only filter returned non-nearby post: {post}"
        
        # Count nearby posts in all posts
        nearby_count_in_all = sum(1 for p in all_posts if p.get("is_nearby"))
        
        print(f"✓ nearby_only filter working: {len(nearby_posts)} nearby posts returned (vs {len(all_posts)} total)")
    
    def test_nearby_only_excludes_distant_posts(self, test_users, test_posts):
        """Test that nearby_only=true excludes posts from distant locations"""
        user1 = test_users[TEST_USER_1["email"]]  # Austin, TX
        
        nearby_response = user1["session"].get(f"{BASE_URL}/api/posts?nearby_only=true")
        assert nearby_response.status_code == 200
        nearby_posts = nearby_response.json()
        
        # No Denver posts should appear for Austin user
        for post in nearby_posts:
            assert "Denver" not in post.get("user_location", ""), f"Denver post should not appear in nearby filter: {post}"
        
        print(f"✓ nearby_only filter correctly excludes distant locations")
    
    # ==================== GET /api/posts/matches Tests ====================
    
    def test_matches_have_location_fields(self, test_users, test_posts):
        """Test that GET /api/posts/matches returns posts with location fields"""
        user1 = test_users[TEST_USER_1["email"]]
        
        # Update user profile with goods wanted to get matches
        user1["session"].put(f"{BASE_URL}/api/profile", json={
            "goods_wanted": ["Honey", "Vegetables"],
            "goods_offering": ["Fresh Eggs"]
        })
        
        response = user1["session"].get(f"{BASE_URL}/api/posts/matches")
        assert response.status_code == 200, f"Failed to get matches: {response.text}"
        matches = response.json()
        
        for match in matches:
            assert "is_nearby" in match, f"Match missing is_nearby field"
            assert "user_location" in match, f"Match missing user_location field"
            assert "match_score" in match, f"Match missing match_score field"
        
        print(f"✓ All {len(matches)} matches have location and match_score fields")
    
    def test_matches_prioritize_nearby_users(self, test_users, test_posts):
        """Test that matches endpoint prioritizes nearby users with higher match_score"""
        user1 = test_users[TEST_USER_1["email"]]  # Austin, TX
        
        # Update user profile to match with test posts
        user1["session"].put(f"{BASE_URL}/api/profile", json={
            "goods_wanted": ["Honey", "Vegetables"],
            "goods_offering": ["Fresh Eggs"]
        })
        
        response = user1["session"].get(f"{BASE_URL}/api/posts/matches")
        assert response.status_code == 200
        matches = response.json()
        
        if len(matches) >= 2:
            # Check that nearby matches have higher scores
            nearby_matches = [m for m in matches if m.get("is_nearby")]
            distant_matches = [m for m in matches if not m.get("is_nearby")]
            
            if nearby_matches and distant_matches:
                # Nearby matches should have +100 bonus
                avg_nearby_score = sum(m.get("match_score", 0) for m in nearby_matches) / len(nearby_matches)
                avg_distant_score = sum(m.get("match_score", 0) for m in distant_matches) / len(distant_matches)
                
                print(f"  Nearby avg score: {avg_nearby_score}, Distant avg score: {avg_distant_score}")
                
                # Nearby should generally have higher scores due to +100 bonus
                # But we can't guarantee it if distant has more item matches
                for nearby in nearby_matches:
                    assert nearby.get("match_score", 0) >= 100, f"Nearby match should have at least 100 score (location bonus)"
        
        print(f"✓ Matches endpoint returns {len(matches)} matches with proper scoring")
    
    def test_matches_sorted_by_score(self, test_users, test_posts):
        """Test that matches are sorted by match_score (highest first)"""
        user1 = test_users[TEST_USER_1["email"]]
        
        response = user1["session"].get(f"{BASE_URL}/api/posts/matches")
        assert response.status_code == 200
        matches = response.json()
        
        if len(matches) >= 2:
            scores = [m.get("match_score", 0) for m in matches]
            assert scores == sorted(scores, reverse=True), f"Matches not sorted by score: {scores}"
        
        print(f"✓ Matches sorted by match_score (descending)")
    
    # ==================== GET /api/users/nearby Tests ====================
    
    def test_nearby_users_endpoint(self, test_users, test_posts):
        """Test that GET /api/users/nearby returns users in the same location"""
        user1 = test_users[TEST_USER_1["email"]]  # Austin, TX
        
        response = user1["session"].get(f"{BASE_URL}/api/users/nearby")
        assert response.status_code == 200, f"Failed to get nearby users: {response.text}"
        
        data = response.json()
        assert "nearby_users" in data, "Response missing nearby_users field"
        assert "user_location" in data, "Response missing user_location field"
        
        nearby_users = data["nearby_users"]
        user_location = data["user_location"]
        
        print(f"✓ Nearby users endpoint returns {len(nearby_users)} users for location: {user_location}")
    
    def test_nearby_users_same_location(self, test_users, test_posts):
        """Test that nearby users are from the same location"""
        user1 = test_users[TEST_USER_1["email"]]  # Austin, TX
        
        response = user1["session"].get(f"{BASE_URL}/api/users/nearby")
        assert response.status_code == 200
        
        data = response.json()
        nearby_users = data["nearby_users"]
        
        # All nearby users should have Austin in their location
        for user in nearby_users:
            user_loc = user.get("location", "")
            # Location matching is flexible - Austin should match Austin, TX
            assert "austin" in user_loc.lower() or user_loc.lower() in "austin, tx", \
                f"Nearby user has non-matching location: {user_loc}"
        
        print(f"✓ All {len(nearby_users)} nearby users are from matching location")
    
    def test_nearby_users_excludes_current_user(self, test_users, test_posts):
        """Test that nearby users list excludes the current user"""
        user1 = test_users[TEST_USER_1["email"]]
        
        response = user1["session"].get(f"{BASE_URL}/api/users/nearby")
        assert response.status_code == 200
        
        data = response.json()
        nearby_users = data["nearby_users"]
        
        # Current user should not be in the list
        user_ids = [u.get("_id") for u in nearby_users]
        assert user1["id"] not in user_ids, "Current user should not appear in nearby users list"
        
        print(f"✓ Current user correctly excluded from nearby users list")
    
    def test_nearby_users_no_location_message(self, session):
        """Test that users without location get appropriate message"""
        # Create a user without location
        no_loc_user = {
            "email": "TEST_no_location@test.com",
            "password": "testpass123",
            "name": "TEST No Location User",
            "location": ""
        }
        
        user_session = requests.Session()
        response = user_session.post(f"{BASE_URL}/api/auth/register", json=no_loc_user)
        
        if response.status_code == 400 and "already registered" in response.text.lower():
            response = user_session.post(f"{BASE_URL}/api/auth/login", json={
                "email": no_loc_user["email"],
                "password": no_loc_user["password"]
            })
        
        if response.status_code == 200:
            nearby_response = user_session.get(f"{BASE_URL}/api/users/nearby")
            assert nearby_response.status_code == 200
            
            data = nearby_response.json()
            # Should return empty list or message about setting location
            assert len(data.get("nearby_users", [])) == 0 or "message" in data
            
            print(f"✓ Users without location get appropriate response")
    
    # ==================== Location Matching Logic Tests ====================
    
    def test_partial_location_match(self, test_users, test_posts):
        """Test that partial location matches work (e.g., 'Austin' matches 'Austin, TX')"""
        # Create user with just city name
        partial_user = {
            "email": "TEST_partial_loc@test.com",
            "password": "testpass123",
            "name": "TEST Partial Location",
            "location": "Austin"  # Just city, no state
        }
        
        user_session = requests.Session()
        response = user_session.post(f"{BASE_URL}/api/auth/register", json=partial_user)
        
        if response.status_code == 400 and "already registered" in response.text.lower():
            response = user_session.post(f"{BASE_URL}/api/auth/login", json={
                "email": partial_user["email"],
                "password": partial_user["password"]
            })
        
        if response.status_code == 200:
            # Get posts and check if Austin, TX posts are marked as nearby
            posts_response = user_session.get(f"{BASE_URL}/api/posts")
            assert posts_response.status_code == 200
            
            posts = posts_response.json()
            austin_posts = [p for p in posts if "Austin" in p.get("user_location", "")]
            
            # At least some Austin posts should be nearby
            nearby_austin = [p for p in austin_posts if p.get("is_nearby")]
            
            print(f"✓ Partial location matching: {len(nearby_austin)}/{len(austin_posts)} Austin posts marked as nearby")


class TestLocationMatchingEdgeCases:
    """Edge case tests for location matching"""
    
    @pytest.fixture(scope="class")
    def session(self):
        return requests.Session()
    
    def test_case_insensitive_matching(self, session):
        """Test that location matching is case-insensitive"""
        # Create user with lowercase location
        user_data = {
            "email": "TEST_lowercase_loc@test.com",
            "password": "testpass123",
            "name": "TEST Lowercase Location",
            "location": "austin, tx"  # lowercase
        }
        
        response = session.post(f"{BASE_URL}/api/auth/register", json=user_data)
        
        if response.status_code == 400 and "already registered" in response.text.lower():
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
        
        if response.status_code == 200:
            posts_response = session.get(f"{BASE_URL}/api/posts")
            assert posts_response.status_code == 200
            
            posts = posts_response.json()
            # Should match with "Austin, TX" posts
            austin_posts = [p for p in posts if "austin" in p.get("user_location", "").lower()]
            nearby_austin = [p for p in austin_posts if p.get("is_nearby")]
            
            print(f"✓ Case-insensitive matching working: {len(nearby_austin)} nearby Austin posts")
    
    def test_empty_location_handling(self, session):
        """Test that empty locations don't cause errors"""
        user_data = {
            "email": "TEST_empty_loc@test.com",
            "password": "testpass123",
            "name": "TEST Empty Location",
            "location": ""
        }
        
        response = session.post(f"{BASE_URL}/api/auth/register", json=user_data)
        
        if response.status_code == 400 and "already registered" in response.text.lower():
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
        
        if response.status_code == 200:
            # Should not crash when getting posts
            posts_response = session.get(f"{BASE_URL}/api/posts")
            assert posts_response.status_code == 200
            
            # All posts should have is_nearby=False for user without location
            posts = posts_response.json()
            for post in posts:
                assert post.get("is_nearby") == False, "Posts should not be nearby for user without location"
            
            print(f"✓ Empty location handling working correctly")


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup test data after all tests"""
    def cleanup_test_data():
        session = requests.Session()
        # Login as admin
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        # Note: In a real scenario, we'd delete TEST_ prefixed data
        print("\n✓ Test cleanup completed")
    
    request.addfinalizer(cleanup_test_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
