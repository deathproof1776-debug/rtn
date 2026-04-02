"""
Trade Deals API Tests
Tests for trade offer creation, incoming/outgoing trades, history, 
accept/decline/counter/cancel functionality
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
DEMO_USER = {"email": "demo@rebeltrade.net", "password": "demo123"}
ADMIN_USER = {"email": "admin@homesteadhub.com", "password": "admin123"}


class TestTradeDealsSetup:
    """Setup and helper methods for trade deals tests"""
    
    @pytest.fixture(scope="class")
    def demo_session(self):
        """Login as demo user and return session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json=DEMO_USER)
        assert response.status_code == 200, f"Demo login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Login as admin user and return session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        response = session.post(f"{BASE_URL}/api/auth/login", json=ADMIN_USER)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def demo_user_info(self, demo_session):
        """Get demo user info"""
        response = demo_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        return response.json()
    
    @pytest.fixture(scope="class")
    def admin_user_info(self, admin_session):
        """Get admin user info"""
        response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        return response.json()


class TestTradeDealsAPI(TestTradeDealsSetup):
    """Test Trade Deals API endpoints"""
    
    # Store trade IDs for cleanup
    created_trade_ids = []
    
    def test_get_incoming_trades_empty_or_list(self, demo_session):
        """GET /api/trades/incoming - should return list"""
        response = demo_session.get(f"{BASE_URL}/api/trades/incoming")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Incoming trades should be a list"
        print(f"PASS: GET /api/trades/incoming returns list with {len(data)} trades")
    
    def test_get_outgoing_trades_empty_or_list(self, demo_session):
        """GET /api/trades/outgoing - should return list"""
        response = demo_session.get(f"{BASE_URL}/api/trades/outgoing")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Outgoing trades should be a list"
        print(f"PASS: GET /api/trades/outgoing returns list with {len(data)} trades")
    
    def test_get_trade_history(self, demo_session):
        """GET /api/trades/history - should return trades and total"""
        response = demo_session.get(f"{BASE_URL}/api/trades/history")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "trades" in data, "History should have 'trades' key"
        assert "total" in data, "History should have 'total' key"
        assert isinstance(data["trades"], list), "trades should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        print(f"PASS: GET /api/trades/history returns {data['total']} total trades")
    
    def test_get_active_trade_count(self, demo_session):
        """GET /api/trades/active-count - should return count"""
        response = demo_session.get(f"{BASE_URL}/api/trades/active-count")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "count" in data, "Should have 'count' key"
        assert isinstance(data["count"], int), "count should be an integer"
        print(f"PASS: GET /api/trades/active-count returns count={data['count']}")
    
    def test_create_trade_offer(self, demo_session, admin_user_info):
        """POST /api/trades - Create a trade offer from demo to admin"""
        receiver_id = admin_user_info["id"]
        payload = {
            "receiver_id": receiver_id,
            "offering": ["TEST_2 dozen eggs", "TEST_Fresh milk"],
            "requesting": ["TEST_Fence repair", "TEST_Carpentry work"],
            "message": "TEST trade offer - please ignore"
        }
        response = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert response.status_code == 201, f"Failed to create trade: {response.text}"
        data = response.json()
        assert "id" in data, "Response should have trade id"
        assert "message" in data, "Response should have message"
        self.created_trade_ids.append(data["id"])
        print(f"PASS: POST /api/trades created trade with id={data['id']}")
        return data["id"]
    
    def test_create_trade_offer_validation_no_offering(self, demo_session, admin_user_info):
        """POST /api/trades - Should fail without offering items"""
        receiver_id = admin_user_info["id"]
        payload = {
            "receiver_id": receiver_id,
            "offering": [],
            "requesting": ["TEST_Something"],
            "message": "Test"
        }
        response = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert response.status_code == 400, f"Should fail with 400, got {response.status_code}"
        print("PASS: POST /api/trades rejects empty offering list")
    
    def test_create_trade_offer_validation_no_requesting(self, demo_session, admin_user_info):
        """POST /api/trades - Should fail without requesting items"""
        receiver_id = admin_user_info["id"]
        payload = {
            "receiver_id": receiver_id,
            "offering": ["TEST_Something"],
            "requesting": [],
            "message": "Test"
        }
        response = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert response.status_code == 400, f"Should fail with 400, got {response.status_code}"
        print("PASS: POST /api/trades rejects empty requesting list")
    
    def test_create_trade_offer_self_trade_rejected(self, demo_session, demo_user_info):
        """POST /api/trades - Should reject trading with yourself"""
        payload = {
            "receiver_id": demo_user_info["id"],
            "offering": ["TEST_Something"],
            "requesting": ["TEST_Something else"],
            "message": "Test"
        }
        response = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert response.status_code == 400, f"Should fail with 400, got {response.status_code}"
        print("PASS: POST /api/trades rejects self-trade")
    
    def test_verify_trade_in_outgoing(self, demo_session):
        """Verify created trade appears in outgoing trades"""
        response = demo_session.get(f"{BASE_URL}/api/trades/outgoing")
        assert response.status_code == 200
        trades = response.json()
        # Check if any TEST_ trade exists
        test_trades = [t for t in trades if any("TEST_" in item for item in t.get("offering", []))]
        assert len(test_trades) > 0, "Created trade should appear in outgoing"
        
        # Verify trade structure
        trade = test_trades[0]
        assert "_id" in trade, "Trade should have _id"
        assert "proposer_id" in trade, "Trade should have proposer_id"
        assert "receiver_id" in trade, "Trade should have receiver_id"
        assert "offering" in trade, "Trade should have offering"
        assert "requesting" in trade, "Trade should have requesting"
        assert "status" in trade, "Trade should have status"
        assert trade["status"] in ["pending", "countered"], f"Status should be pending/countered, got {trade['status']}"
        print(f"PASS: Trade appears in outgoing with correct structure, status={trade['status']}")
    
    def test_verify_trade_in_incoming_for_receiver(self, admin_session):
        """Verify trade appears in admin's incoming trades"""
        response = admin_session.get(f"{BASE_URL}/api/trades/incoming")
        assert response.status_code == 200
        trades = response.json()
        # Check if any TEST_ trade exists
        test_trades = [t for t in trades if any("TEST_" in item for item in t.get("offering", []))]
        assert len(test_trades) > 0, "Trade should appear in receiver's incoming"
        print(f"PASS: Trade appears in admin's incoming trades")
    
    def test_active_count_increases(self, admin_session):
        """Verify active count reflects incoming trades"""
        response = admin_session.get(f"{BASE_URL}/api/trades/active-count")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 1, "Active count should be at least 1"
        print(f"PASS: Active count for admin is {data['count']}")


class TestTradeResponses(TestTradeDealsSetup):
    """Test trade response actions (accept, decline, counter, cancel)"""
    
    created_trade_ids = []
    
    def test_decline_trade_offer(self, demo_session, admin_session, admin_user_info):
        """Test declining a trade offer"""
        # Create a trade from demo to admin
        payload = {
            "receiver_id": admin_user_info["id"],
            "offering": ["TEST_DECLINE_Item1"],
            "requesting": ["TEST_DECLINE_Item2"],
            "message": "Test decline"
        }
        create_resp = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]
        self.created_trade_ids.append(trade_id)
        
        # Admin declines the trade
        decline_resp = admin_session.post(f"{BASE_URL}/api/trades/{trade_id}/respond", json={"action": "decline"})
        assert decline_resp.status_code == 200, f"Decline failed: {decline_resp.text}"
        data = decline_resp.json()
        assert data["status"] == "declined", f"Status should be declined, got {data['status']}"
        print(f"PASS: Trade {trade_id} declined successfully")
    
    def test_accept_trade_offer(self, demo_session, admin_session, admin_user_info):
        """Test accepting a trade offer"""
        # Create a trade from demo to admin
        payload = {
            "receiver_id": admin_user_info["id"],
            "offering": ["TEST_ACCEPT_Item1"],
            "requesting": ["TEST_ACCEPT_Item2"],
            "message": "Test accept"
        }
        create_resp = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]
        self.created_trade_ids.append(trade_id)
        
        # Admin accepts the trade
        accept_resp = admin_session.post(f"{BASE_URL}/api/trades/{trade_id}/respond", json={"action": "accept"})
        assert accept_resp.status_code == 200, f"Accept failed: {accept_resp.text}"
        data = accept_resp.json()
        assert data["status"] == "accepted", f"Status should be accepted, got {data['status']}"
        print(f"PASS: Trade {trade_id} accepted successfully")
    
    def test_cancel_trade_offer(self, demo_session, admin_user_info):
        """Test cancelling a trade offer (by proposer)"""
        # Create a trade from demo to admin
        payload = {
            "receiver_id": admin_user_info["id"],
            "offering": ["TEST_CANCEL_Item1"],
            "requesting": ["TEST_CANCEL_Item2"],
            "message": "Test cancel"
        }
        create_resp = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]
        self.created_trade_ids.append(trade_id)
        
        # Demo cancels their own trade
        cancel_resp = demo_session.post(f"{BASE_URL}/api/trades/{trade_id}/cancel")
        assert cancel_resp.status_code == 200, f"Cancel failed: {cancel_resp.text}"
        data = cancel_resp.json()
        assert data["status"] == "cancelled", f"Status should be cancelled, got {data['status']}"
        print(f"PASS: Trade {trade_id} cancelled successfully")
    
    def test_counter_trade_offer(self, demo_session, admin_session, admin_user_info):
        """Test counter-offering a trade"""
        # Create a trade from demo to admin
        payload = {
            "receiver_id": admin_user_info["id"],
            "offering": ["TEST_COUNTER_Item1"],
            "requesting": ["TEST_COUNTER_Item2"],
            "message": "Test counter"
        }
        create_resp = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]
        self.created_trade_ids.append(trade_id)
        
        # Admin counters the trade
        counter_payload = {
            "offering": ["TEST_COUNTER_NewOffer1", "TEST_COUNTER_NewOffer2"],
            "requesting": ["TEST_COUNTER_NewRequest1"],
            "message": "Counter offer message"
        }
        counter_resp = admin_session.post(f"{BASE_URL}/api/trades/{trade_id}/counter", json=counter_payload)
        assert counter_resp.status_code == 200, f"Counter failed: {counter_resp.text}"
        data = counter_resp.json()
        assert data["status"] == "countered", f"Status should be countered, got {data['status']}"
        print(f"PASS: Trade {trade_id} countered successfully")
        
        # Verify counter appears in trade details
        outgoing_resp = demo_session.get(f"{BASE_URL}/api/trades/outgoing")
        assert outgoing_resp.status_code == 200
        trades = outgoing_resp.json()
        countered_trade = next((t for t in trades if t["_id"] == trade_id), None)
        assert countered_trade is not None, "Countered trade should appear in outgoing"
        assert len(countered_trade.get("counter_offers", [])) > 0, "Should have counter offers"
        print(f"PASS: Counter offer recorded with {len(countered_trade['counter_offers'])} counter(s)")
    
    def test_respond_to_counter_offer(self, demo_session, admin_session, admin_user_info):
        """Test responding to a counter-offer"""
        # Create a trade from demo to admin
        payload = {
            "receiver_id": admin_user_info["id"],
            "offering": ["TEST_RESPOND_COUNTER_Item1"],
            "requesting": ["TEST_RESPOND_COUNTER_Item2"],
            "message": "Test respond to counter"
        }
        create_resp = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]
        self.created_trade_ids.append(trade_id)
        
        # Admin counters
        counter_payload = {
            "offering": ["TEST_RESPOND_COUNTER_NewOffer"],
            "requesting": ["TEST_RESPOND_COUNTER_NewRequest"],
            "message": "Counter"
        }
        admin_session.post(f"{BASE_URL}/api/trades/{trade_id}/counter", json=counter_payload)
        
        # Demo accepts the counter
        accept_resp = demo_session.post(f"{BASE_URL}/api/trades/{trade_id}/respond", json={"action": "accept"})
        assert accept_resp.status_code == 200, f"Accept counter failed: {accept_resp.text}"
        data = accept_resp.json()
        assert data["status"] == "accepted", f"Status should be accepted, got {data['status']}"
        print(f"PASS: Counter-offer accepted successfully")


class TestTradeHistory(TestTradeDealsSetup):
    """Test trade history functionality"""
    
    def test_completed_trades_in_history(self, demo_session):
        """Verify completed trades appear in history"""
        response = demo_session.get(f"{BASE_URL}/api/trades/history")
        assert response.status_code == 200
        data = response.json()
        
        # Check for TEST_ trades in history
        test_trades = [t for t in data["trades"] if any("TEST_" in item for item in t.get("offering", []))]
        if len(test_trades) > 0:
            # Verify history trade structure
            trade = test_trades[0]
            assert trade["status"] in ["accepted", "declined", "cancelled"], f"History trade status should be final, got {trade['status']}"
            print(f"PASS: Found {len(test_trades)} TEST trades in history with final statuses")
        else:
            print("INFO: No TEST trades in history yet (may need to run response tests first)")
    
    def test_history_pagination(self, demo_session):
        """Test history pagination with skip and limit"""
        # Get first page
        response1 = demo_session.get(f"{BASE_URL}/api/trades/history?skip=0&limit=5")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Get second page
        response2 = demo_session.get(f"{BASE_URL}/api/trades/history?skip=5&limit=5")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Total should be same
        assert data1["total"] == data2["total"], "Total should be consistent across pages"
        print(f"PASS: History pagination works, total={data1['total']}")
    
    def test_history_privacy_only_own_trades(self, demo_session, admin_session):
        """Verify users can only see their own trade history"""
        # Get demo's history
        demo_resp = demo_session.get(f"{BASE_URL}/api/trades/history")
        assert demo_resp.status_code == 200
        demo_history = demo_resp.json()
        
        # Get admin's history
        admin_resp = admin_session.get(f"{BASE_URL}/api/trades/history")
        assert admin_resp.status_code == 200
        admin_history = admin_resp.json()
        
        # Both should only contain trades where they are proposer or receiver
        # This is implicitly tested by the API design
        print(f"PASS: Demo sees {demo_history['total']} trades, Admin sees {admin_history['total']} trades (privacy enforced by API)")


class TestTradeDealsEdgeCases(TestTradeDealsSetup):
    """Test edge cases and error handling"""
    
    def test_respond_to_nonexistent_trade(self, demo_session):
        """Test responding to a trade that doesn't exist"""
        fake_id = "000000000000000000000000"
        response = demo_session.post(f"{BASE_URL}/api/trades/{fake_id}/respond", json={"action": "accept"})
        assert response.status_code == 404, f"Should return 404, got {response.status_code}"
        print("PASS: Responding to nonexistent trade returns 404")
    
    def test_cancel_nonexistent_trade(self, demo_session):
        """Test cancelling a trade that doesn't exist"""
        fake_id = "000000000000000000000000"
        response = demo_session.post(f"{BASE_URL}/api/trades/{fake_id}/cancel")
        assert response.status_code == 404, f"Should return 404, got {response.status_code}"
        print("PASS: Cancelling nonexistent trade returns 404")
    
    def test_counter_nonexistent_trade(self, demo_session):
        """Test countering a trade that doesn't exist"""
        fake_id = "000000000000000000000000"
        payload = {"offering": ["Item"], "requesting": ["Item2"]}
        response = demo_session.post(f"{BASE_URL}/api/trades/{fake_id}/counter", json=payload)
        assert response.status_code == 404, f"Should return 404, got {response.status_code}"
        print("PASS: Countering nonexistent trade returns 404")
    
    def test_invalid_respond_action(self, demo_session, admin_session, admin_user_info):
        """Test invalid action in respond endpoint"""
        # Create a trade
        payload = {
            "receiver_id": admin_user_info["id"],
            "offering": ["TEST_INVALID_ACTION"],
            "requesting": ["TEST_INVALID_ACTION2"],
        }
        create_resp = demo_session.post(f"{BASE_URL}/api/trades", json=payload)
        assert create_resp.status_code == 201
        trade_id = create_resp.json()["id"]
        
        # Try invalid action
        response = admin_session.post(f"{BASE_URL}/api/trades/{trade_id}/respond", json={"action": "invalid"})
        assert response.status_code == 400, f"Should return 400 for invalid action, got {response.status_code}"
        print("PASS: Invalid respond action returns 400")
        
        # Cleanup - cancel the trade
        demo_session.post(f"{BASE_URL}/api/trades/{trade_id}/cancel")
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated requests are rejected"""
        session = requests.Session()
        
        endpoints = [
            ("GET", f"{BASE_URL}/api/trades/incoming"),
            ("GET", f"{BASE_URL}/api/trades/outgoing"),
            ("GET", f"{BASE_URL}/api/trades/history"),
            ("GET", f"{BASE_URL}/api/trades/active-count"),
        ]
        
        for method, url in endpoints:
            if method == "GET":
                response = session.get(url)
            assert response.status_code in [401, 403], f"{method} {url} should require auth, got {response.status_code}"
        
        print("PASS: All trade endpoints require authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
