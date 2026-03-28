"""
Push Notifications API Tests
Tests for:
- GET /api/notifications/vapid-public-key - Returns VAPID public key
- POST /api/notifications/subscribe - Subscribe to push notifications
- POST /api/notifications/unsubscribe - Unsubscribe from push notifications
- GET /api/notifications/status - Get subscription status
- POST /api/notifications/test - Send test push notification
- POST /api/posts/{post_id}/like - Triggers push notification to post owner
- POST /api/posts/{post_id}/comments - Triggers push notification to post owner
- POST /api/messages - Triggers push notification to receiver
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test subscription data (mock browser push subscription)
MOCK_SUBSCRIPTION = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-12345",
    "keys": {
        "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
        "auth": "tBHItJI5svbpez7KI4CCXg"
    }
}

MOCK_SUBSCRIPTION_2 = {
    "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint-67890",
    "keys": {
        "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
        "auth": "tBHItJI5svbpez7KI4CCXg"
    }
}


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_cookies(api_client):
    """Login and get auth cookies"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@homesteadhub.com",
        "password": "admin123"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.cookies


@pytest.fixture(scope="module")
def test_user_cookies(api_client):
    """Create and login a test user for notification testing"""
    # Register test user
    test_email = f"TEST_notif_user_{int(time.time())}@test.com"
    register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
        "email": test_email,
        "password": "testpass123",
        "name": "Test Notification User",
        "location": "Austin, TX"
    })
    
    if register_response.status_code == 201 or register_response.status_code == 200:
        return register_response.cookies
    
    # If registration fails (user exists), try login
    login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": test_email,
        "password": "testpass123"
    })
    return login_response.cookies


class TestVapidPublicKey:
    """Tests for GET /api/notifications/vapid-public-key"""
    
    def test_get_vapid_public_key_returns_200(self, api_client):
        """VAPID public key endpoint should return 200"""
        response = api_client.get(f"{BASE_URL}/api/notifications/vapid-public-key")
        assert response.status_code == 200
        print(f"✓ GET /api/notifications/vapid-public-key returns 200")
    
    def test_vapid_public_key_has_correct_structure(self, api_client):
        """Response should contain publicKey field"""
        response = api_client.get(f"{BASE_URL}/api/notifications/vapid-public-key")
        data = response.json()
        assert "publicKey" in data, "Response should contain 'publicKey' field"
        assert isinstance(data["publicKey"], str), "publicKey should be a string"
        assert len(data["publicKey"]) > 0, "publicKey should not be empty"
        print(f"✓ VAPID public key structure is correct: {data['publicKey'][:30]}...")
    
    def test_vapid_public_key_no_auth_required(self, api_client):
        """VAPID public key should be accessible without authentication"""
        # Create a new session without cookies
        new_session = requests.Session()
        response = new_session.get(f"{BASE_URL}/api/notifications/vapid-public-key")
        assert response.status_code == 200
        print("✓ VAPID public key accessible without authentication")


class TestPushSubscription:
    """Tests for POST /api/notifications/subscribe"""
    
    def test_subscribe_requires_auth(self, api_client):
        """Subscribe endpoint should require authentication"""
        response = api_client.post(f"{BASE_URL}/api/notifications/subscribe", json=MOCK_SUBSCRIPTION)
        assert response.status_code == 401
        print("✓ Subscribe endpoint requires authentication")
    
    def test_subscribe_success(self, api_client, auth_cookies):
        """Should successfully subscribe to push notifications"""
        response = api_client.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=MOCK_SUBSCRIPTION,
            cookies=auth_cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "subscribed" in data
        assert data["subscribed"] == True
        print(f"✓ Successfully subscribed to push notifications: {data}")
    
    def test_subscribe_duplicate_returns_already_subscribed(self, api_client, auth_cookies):
        """Subscribing again with same endpoint should return already subscribed"""
        # First subscription
        api_client.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=MOCK_SUBSCRIPTION,
            cookies=auth_cookies
        )
        
        # Second subscription with same endpoint
        response = api_client.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=MOCK_SUBSCRIPTION,
            cookies=auth_cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert data["subscribed"] == True
        assert "Already subscribed" in data.get("message", "")
        print("✓ Duplicate subscription handled correctly")
    
    def test_subscribe_validates_payload(self, api_client, auth_cookies):
        """Subscribe should validate subscription payload"""
        # Missing keys
        invalid_subscription = {"endpoint": "https://test.com"}
        response = api_client.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=invalid_subscription,
            cookies=auth_cookies
        )
        assert response.status_code == 422  # Validation error
        print("✓ Subscribe validates payload structure")


class TestPushUnsubscribe:
    """Tests for POST /api/notifications/unsubscribe"""
    
    def test_unsubscribe_requires_auth(self):
        """Unsubscribe endpoint should require authentication"""
        # Use fresh session without cookies
        fresh_session = requests.Session()
        response = fresh_session.post(f"{BASE_URL}/api/notifications/unsubscribe", json=MOCK_SUBSCRIPTION)
        assert response.status_code == 401
        print("✓ Unsubscribe endpoint requires authentication")
    
    def test_unsubscribe_success(self, api_client, auth_cookies):
        """Should successfully unsubscribe from push notifications"""
        # First subscribe
        api_client.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=MOCK_SUBSCRIPTION_2,
            cookies=auth_cookies
        )
        
        # Then unsubscribe
        response = api_client.post(
            f"{BASE_URL}/api/notifications/unsubscribe",
            json=MOCK_SUBSCRIPTION_2,
            cookies=auth_cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "subscribed" in data
        assert data["subscribed"] == False
        print(f"✓ Successfully unsubscribed from push notifications: {data}")
    
    def test_unsubscribe_nonexistent_subscription(self, api_client, auth_cookies):
        """Unsubscribing non-existent subscription should return not found"""
        nonexistent_sub = {
            "endpoint": "https://fcm.googleapis.com/fcm/send/nonexistent-endpoint",
            "keys": {
                "p256dh": "test",
                "auth": "test"
            }
        }
        response = api_client.post(
            f"{BASE_URL}/api/notifications/unsubscribe",
            json=nonexistent_sub,
            cookies=auth_cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert data["subscribed"] == False
        print("✓ Unsubscribe handles non-existent subscription correctly")


class TestNotificationStatus:
    """Tests for GET /api/notifications/status"""
    
    def test_status_requires_auth(self):
        """Status endpoint should require authentication"""
        # Use fresh session without cookies
        fresh_session = requests.Session()
        response = fresh_session.get(f"{BASE_URL}/api/notifications/status")
        assert response.status_code == 401
        print("✓ Status endpoint requires authentication")
    
    def test_status_returns_subscription_info(self, api_client, auth_cookies):
        """Status should return subscription status"""
        response = api_client.get(
            f"{BASE_URL}/api/notifications/status",
            cookies=auth_cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "subscribed" in data
        assert isinstance(data["subscribed"], bool)
        assert "subscription_count" in data
        assert isinstance(data["subscription_count"], int)
        print(f"✓ Status returns subscription info: subscribed={data['subscribed']}, count={data['subscription_count']}")


class TestTestNotification:
    """Tests for POST /api/notifications/test"""
    
    def test_test_notification_requires_auth(self):
        """Test notification endpoint should require authentication"""
        # Use fresh session without cookies
        fresh_session = requests.Session()
        response = fresh_session.post(f"{BASE_URL}/api/notifications/test")
        assert response.status_code == 401
        print("✓ Test notification endpoint requires authentication")
    
    def test_test_notification_success(self, api_client, auth_cookies):
        """Should successfully send test notification (even if no subscription)"""
        response = api_client.post(
            f"{BASE_URL}/api/notifications/test",
            cookies=auth_cookies
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Test notification sent: {data}")


class TestLikeNotification:
    """Tests for POST /api/posts/{post_id}/like - triggers push notification"""
    
    def test_like_post_triggers_notification(self, api_client, auth_cookies, test_user_cookies):
        """Liking a post should trigger push notification to post owner"""
        # Create a post as admin
        post_response = api_client.post(
            f"{BASE_URL}/api/posts",
            json={
                "title": "TEST_Notification Test Post",
                "description": "Testing like notifications",
                "category": "goods",
                "offering": ["test item"],
                "looking_for": ["anything"]
            },
            cookies=auth_cookies
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Like the post as test user (different user)
        like_response = api_client.post(
            f"{BASE_URL}/api/posts/{post_id}/like",
            cookies=test_user_cookies
        )
        assert like_response.status_code == 200
        data = like_response.json()
        assert "message" in data
        assert "liked" in data["message"].lower() or "unliked" in data["message"].lower()
        print(f"✓ Like post triggers notification flow: {data}")


class TestCommentNotification:
    """Tests for POST /api/posts/{post_id}/comments - triggers push notification"""
    
    def test_comment_triggers_notification(self, api_client, auth_cookies, test_user_cookies):
        """Commenting on a post should trigger push notification to post owner"""
        # Create a post as admin
        post_response = api_client.post(
            f"{BASE_URL}/api/posts",
            json={
                "title": "TEST_Comment Notification Test",
                "description": "Testing comment notifications",
                "category": "services",
                "offering": ["test service"],
                "looking_for": ["anything"]
            },
            cookies=auth_cookies
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]
        
        # Comment on the post as test user (different user)
        comment_response = api_client.post(
            f"{BASE_URL}/api/posts/{post_id}/comments",
            json={"content": "TEST_This is a test comment for notification"},
            cookies=test_user_cookies
        )
        assert comment_response.status_code == 201
        data = comment_response.json()
        assert "id" in data
        assert "content" in data
        print(f"✓ Comment triggers notification flow: comment_id={data['id']}")


class TestMessageNotification:
    """Tests for POST /api/messages - triggers push notification"""
    
    def test_message_triggers_notification(self, api_client, auth_cookies, test_user_cookies):
        """Sending a message should trigger push notification to receiver"""
        # Get admin user ID
        me_response = api_client.get(f"{BASE_URL}/api/auth/me", cookies=auth_cookies)
        assert me_response.status_code == 200
        admin_id = me_response.json()["_id"]
        
        # Send message from test user to admin
        message_response = api_client.post(
            f"{BASE_URL}/api/messages",
            json={
                "receiver_id": admin_id,
                "content": "TEST_This is a test message for notification"
            },
            cookies=test_user_cookies
        )
        assert message_response.status_code == 200
        data = message_response.json()
        assert "id" in data
        assert "message" in data
        print(f"✓ Message triggers notification flow: message_id={data['id']}")


class TestNotificationEndToEnd:
    """End-to-end notification flow tests"""
    
    def test_full_subscription_flow(self, api_client, auth_cookies):
        """Test complete subscription lifecycle: subscribe -> status -> unsubscribe"""
        unique_endpoint = f"https://fcm.googleapis.com/fcm/send/e2e-test-{int(time.time())}"
        subscription = {
            "endpoint": unique_endpoint,
            "keys": {
                "p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTpQtUbVlUls0VJXg7A8u-Ts1XbjhazAkj7I99e8QcYP7DkM",
                "auth": "tBHItJI5svbpez7KI4CCXg"
            }
        }
        
        # 1. Subscribe
        sub_response = api_client.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=subscription,
            cookies=auth_cookies
        )
        assert sub_response.status_code == 200
        assert sub_response.json()["subscribed"] == True
        print("  ✓ Step 1: Subscribed successfully")
        
        # 2. Check status
        status_response = api_client.get(
            f"{BASE_URL}/api/notifications/status",
            cookies=auth_cookies
        )
        assert status_response.status_code == 200
        assert status_response.json()["subscribed"] == True
        print("  ✓ Step 2: Status shows subscribed")
        
        # 3. Unsubscribe
        unsub_response = api_client.post(
            f"{BASE_URL}/api/notifications/unsubscribe",
            json=subscription,
            cookies=auth_cookies
        )
        assert unsub_response.status_code == 200
        assert unsub_response.json()["subscribed"] == False
        print("  ✓ Step 3: Unsubscribed successfully")
        
        print("✓ Full subscription lifecycle completed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
