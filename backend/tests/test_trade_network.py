"""
Trade Network Feature Tests
Tests for network request/accept/decline flow, connections management, and feed priority
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@homesteadhub.com"
ADMIN_PASSWORD = "admin123"

# Test users for network testing
TEST_USER_1 = {
    "email": f"test_network_user1_{int(time.time())}@test.com",
    "password": "testpass123",
    "name": "TEST_NetworkUser1"
}

TEST_USER_2 = {
    "email": f"test_network_user2_{int(time.time())}@test.com",
    "password": "testpass123",
    "name": "TEST_NetworkUser2"
}


class TestNetworkEndpoints:
    """Test Trade Network API endpoints"""
    
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
    def user1_session(self):
        """Register and login as test user 1"""
        session = requests.Session()
        # Register
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_1["email"],
            "password": TEST_USER_1["password"],
            "name": TEST_USER_1["name"],
            "location": "Test Location 1"
        })
        if response.status_code == 400 and "already registered" in response.text:
            # User exists, login instead
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_1["email"],
                "password": TEST_USER_1["password"]
            })
        assert response.status_code in [200, 201], f"User1 registration/login failed: {response.text}"
        user_data = response.json()
        session.user_id = user_data.get("id")
        return session
    
    @pytest.fixture(scope="class")
    def user2_session(self):
        """Register and login as test user 2"""
        session = requests.Session()
        # Register
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_2["email"],
            "password": TEST_USER_2["password"],
            "name": TEST_USER_2["name"],
            "location": "Test Location 2"
        })
        if response.status_code == 400 and "already registered" in response.text:
            # User exists, login instead
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": TEST_USER_2["email"],
                "password": TEST_USER_2["password"]
            })
        assert response.status_code in [200, 201], f"User2 registration/login failed: {response.text}"
        user_data = response.json()
        session.user_id = user_data.get("id")
        return session

    # ==================
    # Network Request Tests
    # ==================
    
    def test_send_network_request(self, user1_session, user2_session):
        """Test POST /api/network/request - Send network request"""
        # User1 sends request to User2
        response = user1_session.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": user2_session.user_id
        })
        
        # Could be 200 (success) or 400 (already pending/connected)
        if response.status_code == 200:
            data = response.json()
            assert "id" in data or "message" in data
            print(f"Network request sent successfully: {data}")
        elif response.status_code == 400:
            # Already pending or connected - acceptable
            print(f"Request already exists or connected: {response.json()}")
        else:
            pytest.fail(f"Unexpected status {response.status_code}: {response.text}")
    
    def test_send_request_to_self_fails(self, user1_session):
        """Test that sending request to self fails"""
        response = user1_session.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": user1_session.user_id
        })
        assert response.status_code == 400
        assert "yourself" in response.json().get("detail", "").lower()
    
    def test_send_request_to_nonexistent_user(self, user1_session):
        """Test sending request to non-existent user"""
        response = user1_session.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": "000000000000000000000000"  # Invalid ObjectId
        })
        assert response.status_code == 404
    
    # ==================
    # Pending Requests Tests
    # ==================
    
    def test_get_pending_requests(self, user1_session, user2_session):
        """Test GET /api/network/requests/pending"""
        # Check User2's pending requests (should have incoming from User1)
        response = user2_session.get(f"{BASE_URL}/api/network/requests/pending")
        assert response.status_code == 200
        
        data = response.json()
        assert "incoming" in data
        assert "outgoing" in data
        assert "incoming_count" in data
        print(f"Pending requests for User2: incoming={len(data['incoming'])}, outgoing={len(data['outgoing'])}")
    
    def test_pending_requests_structure(self, user2_session):
        """Test pending requests response structure"""
        response = user2_session.get(f"{BASE_URL}/api/network/requests/pending")
        assert response.status_code == 200
        
        data = response.json()
        if data["incoming"]:
            req = data["incoming"][0]
            assert "id" in req
            assert "from_user_id" in req
            assert "from_user_name" in req
            assert "created_at" in req
    
    # ==================
    # Respond to Request Tests
    # ==================
    
    def test_accept_network_request(self, user1_session, user2_session):
        """Test POST /api/network/respond - Accept request"""
        # First ensure there's a pending request
        user1_session.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": user2_session.user_id
        })
        
        # Get pending requests for User2
        pending_response = user2_session.get(f"{BASE_URL}/api/network/requests/pending")
        pending_data = pending_response.json()
        
        # Find request from User1
        request_id = None
        for req in pending_data.get("incoming", []):
            if req.get("from_user_id") == user1_session.user_id:
                request_id = req["id"]
                break
        
        if request_id:
            # Accept the request
            response = user2_session.post(f"{BASE_URL}/api/network/respond", json={
                "request_id": request_id,
                "accept": True
            })
            assert response.status_code == 200
            data = response.json()
            assert data.get("connected") == True or "accepted" in data.get("message", "").lower()
            print(f"Request accepted: {data}")
        else:
            # Already connected or no pending request
            print("No pending request found - may already be connected")
    
    def test_decline_network_request(self, admin_session, user1_session):
        """Test declining a network request"""
        # Admin sends request to User1
        admin_session.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": user1_session.user_id
        })
        
        # Get pending requests for User1
        pending_response = user1_session.get(f"{BASE_URL}/api/network/requests/pending")
        pending_data = pending_response.json()
        
        # Find request from admin
        admin_me = admin_session.get(f"{BASE_URL}/api/auth/me").json()
        admin_id = admin_me.get("id")
        
        request_id = None
        for req in pending_data.get("incoming", []):
            if req.get("from_user_id") == admin_id:
                request_id = req["id"]
                break
        
        if request_id:
            # Decline the request
            response = user1_session.post(f"{BASE_URL}/api/network/respond", json={
                "request_id": request_id,
                "accept": False
            })
            assert response.status_code == 200
            data = response.json()
            assert data.get("connected") == False or "declined" in data.get("message", "").lower()
            print(f"Request declined: {data}")
        else:
            print("No pending request from admin found")
    
    def test_respond_to_nonexistent_request(self, user1_session):
        """Test responding to non-existent request"""
        response = user1_session.post(f"{BASE_URL}/api/network/respond", json={
            "request_id": "000000000000000000000000",
            "accept": True
        })
        assert response.status_code == 404
    
    # ==================
    # Connections Tests
    # ==================
    
    def test_get_network_connections(self, user1_session):
        """Test GET /api/network/connections"""
        response = user1_session.get(f"{BASE_URL}/api/network/connections")
        assert response.status_code == 200
        
        data = response.json()
        assert "connections" in data
        assert "count" in data
        assert isinstance(data["connections"], list)
        print(f"User1 has {data['count']} connections")
    
    def test_connections_structure(self, user1_session):
        """Test connections response structure"""
        response = user1_session.get(f"{BASE_URL}/api/network/connections")
        assert response.status_code == 200
        
        data = response.json()
        if data["connections"]:
            conn = data["connections"][0]
            assert "id" in conn
            assert "name" in conn
            # Optional fields
            print(f"Connection structure: {list(conn.keys())}")
    
    # ==================
    # Network Status Tests
    # ==================
    
    def test_get_network_status_connected(self, user1_session, user2_session):
        """Test GET /api/network/status/{user_id} for connected users"""
        response = user1_session.get(f"{BASE_URL}/api/network/status/{user2_session.user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "can_request" in data
        print(f"Network status with User2: {data}")
    
    def test_get_network_status_none(self, user1_session):
        """Test network status with non-connected user"""
        # Create a new user to test with
        session = requests.Session()
        new_user_email = f"test_status_user_{int(time.time())}@test.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": new_user_email,
            "password": "testpass123",
            "name": "TEST_StatusUser",
            "location": "Test"
        })
        
        if response.status_code in [200, 201]:
            new_user_id = response.json().get("id")
            
            # Check status
            status_response = user1_session.get(f"{BASE_URL}/api/network/status/{new_user_id}")
            assert status_response.status_code == 200
            
            data = status_response.json()
            # Should be 'none' or 'pending_sent' or 'connected'
            assert data["status"] in ["none", "pending_sent", "pending_received", "connected"]
            print(f"Status with new user: {data}")
    
    # ==================
    # Cancel Request Tests
    # ==================
    
    def test_cancel_network_request(self, user1_session):
        """Test POST /api/network/cancel/{request_id}"""
        # Create a new user to send request to
        session = requests.Session()
        new_user_email = f"test_cancel_user_{int(time.time())}@test.com"
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": new_user_email,
            "password": "testpass123",
            "name": "TEST_CancelUser",
            "location": "Test"
        })
        
        if response.status_code in [200, 201]:
            new_user_id = response.json().get("id")
            
            # Send request
            send_response = user1_session.post(f"{BASE_URL}/api/network/request", json={
                "target_user_id": new_user_id
            })
            
            if send_response.status_code == 200:
                request_id = send_response.json().get("id")
                
                # Cancel the request
                cancel_response = user1_session.post(f"{BASE_URL}/api/network/cancel/{request_id}")
                assert cancel_response.status_code == 200
                assert "cancelled" in cancel_response.json().get("message", "").lower()
                print("Request cancelled successfully")
    
    def test_cancel_nonexistent_request(self, user1_session):
        """Test cancelling non-existent request"""
        response = user1_session.post(f"{BASE_URL}/api/network/cancel/000000000000000000000000")
        assert response.status_code == 404
    
    # ==================
    # Remove Connection Tests
    # ==================
    
    def test_remove_connection(self, user1_session, user2_session):
        """Test DELETE /api/network/connections/{user_id}"""
        # First ensure they're connected
        # Send request
        user1_session.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": user2_session.user_id
        })
        
        # Accept if pending
        pending = user2_session.get(f"{BASE_URL}/api/network/requests/pending").json()
        for req in pending.get("incoming", []):
            if req.get("from_user_id") == user1_session.user_id:
                user2_session.post(f"{BASE_URL}/api/network/respond", json={
                    "request_id": req["id"],
                    "accept": True
                })
                break
        
        # Now try to remove
        response = user1_session.delete(f"{BASE_URL}/api/network/connections/{user2_session.user_id}")
        
        # Could be 200 (removed) or 404 (not connected)
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert "removed" in response.json().get("message", "").lower()
            print("Connection removed successfully")
        else:
            print("Connection not found - may not have been connected")
    
    def test_remove_nonexistent_connection(self, user1_session):
        """Test removing non-existent connection"""
        response = user1_session.delete(f"{BASE_URL}/api/network/connections/000000000000000000000000")
        assert response.status_code == 404
    
    # ==================
    # Feed Priority Tests
    # ==================
    
    def test_posts_include_network_field(self, user1_session):
        """Test GET /api/posts returns is_network field"""
        response = user1_session.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        
        posts = response.json()
        if posts:
            post = posts[0]
            assert "is_network" in post, "Posts should include is_network field"
            print(f"Post has is_network={post['is_network']}")
    
    def test_posts_include_feed_score(self, user1_session):
        """Test GET /api/posts returns feed_score field"""
        response = user1_session.get(f"{BASE_URL}/api/posts")
        assert response.status_code == 200
        
        posts = response.json()
        if posts:
            post = posts[0]
            assert "feed_score" in post, "Posts should include feed_score field"
            print(f"Post has feed_score={post['feed_score']}")
    
    # ==================
    # Auth Required Tests
    # ==================
    
    def test_network_endpoints_require_auth(self):
        """Test that network endpoints require authentication"""
        session = requests.Session()  # No auth
        
        endpoints = [
            ("POST", "/api/network/request", {"target_user_id": "test"}),
            ("POST", "/api/network/respond", {"request_id": "test", "accept": True}),
            ("GET", "/api/network/requests/pending", None),
            ("GET", "/api/network/connections", None),
            ("DELETE", "/api/network/connections/test", None),
            ("GET", "/api/network/status/test", None),
            ("POST", "/api/network/cancel/test", None),
        ]
        
        for method, endpoint, data in endpoints:
            if method == "GET":
                response = session.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = session.post(f"{BASE_URL}{endpoint}", json=data)
            elif method == "DELETE":
                response = session.delete(f"{BASE_URL}{endpoint}")
            
            assert response.status_code == 401, f"{method} {endpoint} should require auth, got {response.status_code}"
        
        print("All network endpoints correctly require authentication")


class TestNetworkIntegration:
    """Integration tests for full network flow"""
    
    def test_full_network_flow(self):
        """Test complete flow: request -> accept -> verify connection -> remove"""
        # Create two fresh users
        session1 = requests.Session()
        session2 = requests.Session()
        
        user1_email = f"test_flow_user1_{int(time.time())}@test.com"
        user2_email = f"test_flow_user2_{int(time.time())}@test.com"
        
        # Register User1
        resp1 = session1.post(f"{BASE_URL}/api/auth/register", json={
            "email": user1_email,
            "password": "testpass123",
            "name": "TEST_FlowUser1",
            "location": "Test"
        })
        assert resp1.status_code in [200, 201]
        user1_id = resp1.json().get("id")
        
        # Register User2
        resp2 = session2.post(f"{BASE_URL}/api/auth/register", json={
            "email": user2_email,
            "password": "testpass123",
            "name": "TEST_FlowUser2",
            "location": "Test"
        })
        assert resp2.status_code in [200, 201]
        user2_id = resp2.json().get("id")
        
        # Step 1: User1 sends request to User2
        send_resp = session1.post(f"{BASE_URL}/api/network/request", json={
            "target_user_id": user2_id
        })
        assert send_resp.status_code == 200
        request_id = send_resp.json().get("id")
        print(f"Step 1: Request sent, id={request_id}")
        
        # Step 2: Verify User2 has pending request
        pending_resp = session2.get(f"{BASE_URL}/api/network/requests/pending")
        assert pending_resp.status_code == 200
        pending_data = pending_resp.json()
        assert pending_data["incoming_count"] >= 1
        print(f"Step 2: User2 has {pending_data['incoming_count']} pending requests")
        
        # Step 3: User2 accepts request
        accept_resp = session2.post(f"{BASE_URL}/api/network/respond", json={
            "request_id": request_id,
            "accept": True
        })
        assert accept_resp.status_code == 200
        assert accept_resp.json().get("connected") == True
        print("Step 3: Request accepted")
        
        # Step 4: Verify both users see connection
        conn1_resp = session1.get(f"{BASE_URL}/api/network/connections")
        assert conn1_resp.status_code == 200
        conn1_data = conn1_resp.json()
        assert conn1_data["count"] >= 1
        print(f"Step 4a: User1 has {conn1_data['count']} connections")
        
        conn2_resp = session2.get(f"{BASE_URL}/api/network/connections")
        assert conn2_resp.status_code == 200
        conn2_data = conn2_resp.json()
        assert conn2_data["count"] >= 1
        print(f"Step 4b: User2 has {conn2_data['count']} connections")
        
        # Step 5: Verify network status shows connected
        status_resp = session1.get(f"{BASE_URL}/api/network/status/{user2_id}")
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "connected"
        print("Step 5: Status shows connected")
        
        # Step 6: Remove connection
        remove_resp = session1.delete(f"{BASE_URL}/api/network/connections/{user2_id}")
        assert remove_resp.status_code == 200
        print("Step 6: Connection removed")
        
        # Step 7: Verify connection is gone
        final_status = session1.get(f"{BASE_URL}/api/network/status/{user2_id}")
        assert final_status.status_code == 200
        assert final_status.json()["status"] == "none"
        print("Step 7: Status shows none - flow complete!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
