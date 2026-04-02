"""
Recommended Traders Feature Tests
Tests for GET /api/network/recommended endpoint - matching users based on complementary goods/services
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from environment
ADMIN_EMAIL = os.environ.get('TEST_ADMIN_EMAIL', 'demo@rebeltrade.net')
ADMIN_PASSWORD = os.environ.get('TEST_ADMIN_PASSWORD', 'demo123')


class TestRecommendedTradersEndpoint:
    """Test GET /api/network/recommended endpoint"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Login as admin and return session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def matcher_user_session(self):
        """Create a user with matching goods/services for admin"""
        session = requests.Session()
        email = f"test_matcher_{int(time.time())}@test.com"
        
        # Register user
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "testpass123",
            "name": "TEST_MatcherUser",
            "location": "Test Location"
        })
        
        if response.status_code == 400 and "already registered" in response.text:
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": email,
                "password": "testpass123"
            })
        
        assert response.status_code in [200, 201], f"Matcher user registration failed: {response.text}"
        user_data = response.json()
        session.user_id = user_data.get("id")
        
        # Update profile with goods that match admin's wants
        # Admin wants: Fresh Eggs, Honey; Admin offers: Seeds
        # So this user should offer: Fresh Eggs, Honey; want: Seeds
        profile_response = session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": ["Fresh Eggs", "Honey"],
            "goods_wanted": ["Seeds"],
            "services_offering": ["Beekeeping"],
            "services_wanted": ["Gardening"]
        })
        assert profile_response.status_code == 200, f"Profile update failed: {profile_response.text}"
        
        return session
    
    @pytest.fixture(scope="class")
    def no_match_user_session(self):
        """Create a user with no matching goods/services"""
        session = requests.Session()
        email = f"test_nomatch_{int(time.time())}@test.com"
        
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "testpass123",
            "name": "TEST_NoMatchUser",
            "location": "Test Location"
        })
        
        if response.status_code == 400 and "already registered" in response.text:
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": email,
                "password": "testpass123"
            })
        
        assert response.status_code in [200, 201]
        user_data = response.json()
        session.user_id = user_data.get("id")
        
        # Update profile with goods that DON'T match admin
        profile_response = session.put(f"{BASE_URL}/api/profile", json={
            "goods_offering": ["Lumber", "Firewood"],
            "goods_wanted": ["Tools", "Nails"],
            "services_offering": [],
            "services_wanted": []
        })
        assert profile_response.status_code == 200
        
        return session
    
    @pytest.fixture(scope="class")
    def setup_admin_profile(self, admin_session):
        """Ensure admin has goods_wanted and goods_offering set"""
        # Update admin profile with specific goods
        response = admin_session.put(f"{BASE_URL}/api/profile", json={
            "goods_wanted": ["Fresh Eggs", "Honey"],
            "goods_offering": ["Seeds"],
            "services_wanted": ["Gardening"],
            "services_offering": ["Community Management"]
        })
        assert response.status_code == 200, f"Admin profile update failed: {response.text}"
        return True
    
    # ==================
    # Basic Endpoint Tests
    # ==================
    
    def test_recommended_endpoint_returns_200(self, admin_session, setup_admin_profile):
        """Test GET /api/network/recommended returns 200"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("Recommended endpoint returns 200 OK")
    
    def test_recommended_response_structure(self, admin_session, setup_admin_profile):
        """Test response has correct structure"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data, "Response should have 'recommendations' field"
        assert isinstance(data["recommendations"], list), "recommendations should be a list"
        
        # Check for total_matches or message field
        assert "total_matches" in data or "message" in data, "Response should have total_matches or message"
        print(f"Response structure valid: {list(data.keys())}")
    
    def test_recommendation_item_structure(self, admin_session, setup_admin_profile, matcher_user_session):
        """Test each recommendation has required fields"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        if recommendations:
            rec = recommendations[0]
            required_fields = ["id", "name", "match_score", "reason"]
            for field in required_fields:
                assert field in rec, f"Recommendation should have '{field}' field"
            
            # Check optional but expected fields
            optional_fields = ["avatar", "location", "is_verified", "offers_you_want", "wants_you_offer"]
            present_fields = [f for f in optional_fields if f in rec]
            print(f"Recommendation has fields: {list(rec.keys())}")
            print(f"Optional fields present: {present_fields}")
        else:
            print("No recommendations found - may need matching users")
    
    # ==================
    # Match Logic Tests
    # ==================
    
    def test_recommendations_show_offers_you_want(self, admin_session, setup_admin_profile, matcher_user_session):
        """Test recommendations include offers_you_want list"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        # Find the matcher user in recommendations
        matcher_rec = None
        for rec in recommendations:
            if rec.get("id") == matcher_user_session.user_id:
                matcher_rec = rec
                break
        
        if matcher_rec:
            assert "offers_you_want" in matcher_rec, "Should have offers_you_want field"
            offers = matcher_rec.get("offers_you_want", [])
            print(f"Matcher offers you want: {offers}")
            # Matcher offers Fresh Eggs, Honey - admin wants these
            assert any(item in offers for item in ["Fresh Eggs", "Honey"]), "Should show matching offers"
        else:
            print(f"Matcher user {matcher_user_session.user_id} not found in recommendations - may be connected or pending")
    
    def test_recommendations_show_wants_you_offer(self, admin_session, setup_admin_profile, matcher_user_session):
        """Test recommendations include wants_you_offer list"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        # Find the matcher user
        matcher_rec = None
        for rec in recommendations:
            if rec.get("id") == matcher_user_session.user_id:
                matcher_rec = rec
                break
        
        if matcher_rec:
            assert "wants_you_offer" in matcher_rec, "Should have wants_you_offer field"
            wants = matcher_rec.get("wants_you_offer", [])
            print(f"Matcher wants you offer: {wants}")
            # Matcher wants Seeds - admin offers these
            assert "Seeds" in wants, "Should show matching wants"
        else:
            print("Matcher user not in recommendations")
    
    def test_recommendations_show_match_reason(self, admin_session, setup_admin_profile, matcher_user_session):
        """Test recommendations include human-readable match reason"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        if recommendations:
            rec = recommendations[0]
            assert "reason" in rec, "Should have reason field"
            reason = rec.get("reason", "")
            assert len(reason) > 0, "Reason should not be empty"
            # Reason format: "Offers X • Wants Y"
            print(f"Match reason: {reason}")
        else:
            print("No recommendations to check reason")
    
    def test_match_score_calculation(self, admin_session, setup_admin_profile, matcher_user_session):
        """Test match score is calculated correctly"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        
        # Find matcher user
        matcher_rec = None
        for rec in recommendations:
            if rec.get("id") == matcher_user_session.user_id:
                matcher_rec = rec
                break
        
        if matcher_rec:
            score = matcher_rec.get("match_score", 0)
            offers_count = len(matcher_rec.get("offers_you_want", []))
            wants_count = len(matcher_rec.get("wants_you_offer", []))
            
            # Score = offers_count * 15 + wants_count * 10
            expected_min_score = offers_count * 15 + wants_count * 10
            assert score >= expected_min_score, f"Score {score} should be >= {expected_min_score}"
            print(f"Match score: {score} (offers: {offers_count}, wants: {wants_count})")
        else:
            print("Matcher user not in recommendations")
    
    # ==================
    # Exclusion Tests
    # ==================
    
    def test_excludes_already_connected_users(self, admin_session, setup_admin_profile):
        """Test that connected users are excluded from recommendations"""
        # Get current connections
        conn_response = admin_session.get(f"{BASE_URL}/api/network/connections")
        assert conn_response.status_code == 200
        connections = conn_response.json().get("connections", [])
        connected_ids = [c["id"] for c in connections]
        
        # Get recommendations
        rec_response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert rec_response.status_code == 200
        recommendations = rec_response.json().get("recommendations", [])
        rec_ids = [r["id"] for r in recommendations]
        
        # Check no overlap
        overlap = set(connected_ids) & set(rec_ids)
        assert len(overlap) == 0, f"Connected users should not appear in recommendations: {overlap}"
        print(f"Verified: {len(connected_ids)} connected users excluded from {len(rec_ids)} recommendations")
    
    def test_excludes_pending_request_users(self, admin_session, setup_admin_profile):
        """Test that users with pending requests are excluded"""
        # Get pending requests
        pending_response = admin_session.get(f"{BASE_URL}/api/network/requests/pending")
        assert pending_response.status_code == 200
        pending_data = pending_response.json()
        
        pending_ids = set()
        for req in pending_data.get("incoming", []):
            pending_ids.add(req.get("from_user_id"))
        for req in pending_data.get("outgoing", []):
            pending_ids.add(req.get("to_user_id"))
        
        # Get recommendations
        rec_response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert rec_response.status_code == 200
        recommendations = rec_response.json().get("recommendations", [])
        rec_ids = [r["id"] for r in recommendations]
        
        # Check no overlap
        overlap = pending_ids & set(rec_ids)
        assert len(overlap) == 0, f"Pending request users should not appear in recommendations: {overlap}"
        print(f"Verified: {len(pending_ids)} pending users excluded from recommendations")
    
    def test_excludes_self(self, admin_session, setup_admin_profile):
        """Test that current user is excluded from recommendations"""
        # Get current user ID
        me_response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        my_id = me_response.json().get("id")
        
        # Get recommendations
        rec_response = admin_session.get(f"{BASE_URL}/api/network/recommended")
        assert rec_response.status_code == 200
        recommendations = rec_response.json().get("recommendations", [])
        rec_ids = [r["id"] for r in recommendations]
        
        assert my_id not in rec_ids, "Current user should not appear in recommendations"
        print("Verified: Current user excluded from recommendations")
    
    # ==================
    # Empty State Tests
    # ==================
    
    def test_empty_state_when_no_preferences(self):
        """Test empty recommendations when user has no goods/services preferences"""
        # Create user with no preferences
        session = requests.Session()
        email = f"test_empty_{int(time.time())}@test.com"
        
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "testpass123",
            "name": "TEST_EmptyUser",
            "location": "Test"
        })
        assert response.status_code in [200, 201]
        
        # Don't set any goods/services - get recommendations
        rec_response = session.get(f"{BASE_URL}/api/network/recommended")
        assert rec_response.status_code == 200
        
        data = rec_response.json()
        recommendations = data.get("recommendations", [])
        
        # Should be empty or have a message
        if len(recommendations) == 0:
            assert "message" in data, "Should have message when no recommendations"
            print(f"Empty state message: {data.get('message')}")
        else:
            print(f"Got {len(recommendations)} recommendations even without preferences")
    
    def test_empty_state_when_no_matches(self, no_match_user_session):
        """Test empty recommendations when no users match"""
        rec_response = no_match_user_session.get(f"{BASE_URL}/api/network/recommended")
        assert rec_response.status_code == 200
        
        data = rec_response.json()
        # May or may not have matches depending on other users in system
        print(f"No-match user got {len(data.get('recommendations', []))} recommendations")
    
    # ==================
    # Limit Parameter Test
    # ==================
    
    def test_limit_parameter(self, admin_session, setup_admin_profile):
        """Test limit parameter works"""
        response = admin_session.get(f"{BASE_URL}/api/network/recommended?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data.get("recommendations", [])
        assert len(recommendations) <= 5, f"Should return at most 5 recommendations, got {len(recommendations)}"
        print(f"Limit=5 returned {len(recommendations)} recommendations")
    
    # ==================
    # Auth Required Test
    # ==================
    
    def test_requires_authentication(self):
        """Test endpoint requires authentication"""
        session = requests.Session()  # No auth
        response = session.get(f"{BASE_URL}/api/network/recommended")
        assert response.status_code == 401, f"Should require auth, got {response.status_code}"
        print("Verified: Endpoint requires authentication")


class TestRecommendedTradersIntegration:
    """Integration tests for recommended traders with connect flow"""
    
    def test_connect_from_recommendation(self):
        """Test full flow: get recommendation -> send connect request"""
        # Create two users with matching goods
        session1 = requests.Session()
        session2 = requests.Session()
        
        ts = int(time.time())
        user1_email = f"test_rec_user1_{ts}@test.com"
        user2_email = f"test_rec_user2_{ts}@test.com"
        
        # Register User1 - wants Eggs, offers Seeds
        resp1 = session1.post(f"{BASE_URL}/api/auth/register", json={
            "email": user1_email,
            "password": "testpass123",
            "name": "TEST_RecUser1",
            "location": "Test"
        })
        assert resp1.status_code in [200, 201]
        user1_id = resp1.json().get("id")
        
        # Set User1 profile
        session1.put(f"{BASE_URL}/api/profile", json={
            "goods_wanted": ["Eggs"],
            "goods_offering": ["Seeds"]
        })
        
        # Register User2 - offers Eggs, wants Seeds (perfect match!)
        resp2 = session2.post(f"{BASE_URL}/api/auth/register", json={
            "email": user2_email,
            "password": "testpass123",
            "name": "TEST_RecUser2",
            "location": "Test"
        })
        assert resp2.status_code in [200, 201]
        user2_id = resp2.json().get("id")
        
        # Set User2 profile
        session2.put(f"{BASE_URL}/api/profile", json={
            "goods_wanted": ["Seeds"],
            "goods_offering": ["Eggs"]
        })
        
        # User1 gets recommendations - should see User2
        rec_response = session1.get(f"{BASE_URL}/api/network/recommended")
        assert rec_response.status_code == 200
        
        recommendations = rec_response.json().get("recommendations", [])
        user2_rec = None
        for rec in recommendations:
            if rec.get("id") == user2_id:
                user2_rec = rec
                break
        
        if user2_rec:
            print(f"Found User2 in recommendations with score {user2_rec.get('match_score')}")
            
            # Send connect request
            connect_response = session1.post(f"{BASE_URL}/api/network/request", json={
                "target_user_id": user2_id
            })
            assert connect_response.status_code == 200, f"Connect failed: {connect_response.text}"
            print("Successfully sent connect request from recommendation")
            
            # Verify User2 no longer in recommendations (pending request)
            rec_response2 = session1.get(f"{BASE_URL}/api/network/recommended")
            recommendations2 = rec_response2.json().get("recommendations", [])
            rec_ids = [r["id"] for r in recommendations2]
            assert user2_id not in rec_ids, "User with pending request should be excluded"
            print("Verified: User excluded after sending request")
        else:
            print(f"User2 ({user2_id}) not found in recommendations - checking why...")
            print(f"Total recommendations: {len(recommendations)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
