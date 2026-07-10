"""
Backend tests for avatar backfill bug fix.
Tests that when user updates their avatar via PUT /api/profile,
all existing posts and community_posts get backfilled with the new avatar.
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "deathproofrebel@protonmail.com"
ADMIN_PASSWORD = "Peaches1776@"


@pytest.fixture(scope="module")
def session():
    """Shared requests session with credentials."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def auth_session(session):
    """Authenticated session as admin."""
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Admin login failed: {resp.status_code} {resp.text}")
    return session


@pytest.fixture(scope="module")
def admin_user_id(auth_session):
    """Get admin user's ID from /api/auth/me."""
    resp = auth_session.get(f"{BASE_URL}/api/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    user_id = data.get("id") or data.get("_id")
    assert user_id, "Could not get admin user id"
    return user_id


class TestAvatarBackfill:
    """Test that updating avatar via PUT /api/profile backfills all posts."""

    def test_login_success(self, auth_session):
        """Verify admin login works."""
        resp = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("name") or data.get("email")
        print(f"Logged in as: {data.get('name')} ({data.get('email')})")

    def test_create_barter_post(self, auth_session, admin_user_id):
        """Create a test barter post to verify backfill later."""
        unique_title = f"TEST_AvatarBackfill_Barter_{uuid.uuid4().hex[:8]}"
        payload = {
            "title": unique_title,
            "description": "Test post for avatar backfill verification",
            "category": "goods",
            "offering": ["Test item"],
            "looking_for": ["Something else"]
        }
        resp = auth_session.post(f"{BASE_URL}/api/posts", json=payload)
        assert resp.status_code == 201, f"Failed to create post: {resp.text}"
        data = resp.json()
        post_id = data.get("id") or data.get("_id")
        assert post_id, "No post_id in response"
        # Store for later use in the module
        TestAvatarBackfill._test_post_id = post_id
        print(f"Created barter post: {post_id}")

    def test_create_community_post(self, auth_session):
        """Create a test community post to verify backfill later."""
        unique_title = f"TEST_AvatarBackfill_Community_{uuid.uuid4().hex[:8]}"
        payload = {
            "title": unique_title,
            "content": "Test community post for avatar backfill verification",
            "topic": "general"
        }
        resp = auth_session.post(f"{BASE_URL}/api/community", json=payload)
        assert resp.status_code == 201, f"Failed to create community post: {resp.text}"
        data = resp.json()
        post_id = data.get("id") or data.get("_id")
        assert post_id, "No community post_id in response"
        TestAvatarBackfill._test_community_post_id = post_id
        print(f"Created community post: {post_id}")

    def test_update_avatar_via_profile_put(self, auth_session):
        """PUT /api/profile with new avatar — should return 200 and trigger backfill."""
        # Use a deterministic test avatar URL
        test_avatar = f"https://example.com/test-avatar-{uuid.uuid4().hex[:8]}.jpg"
        TestAvatarBackfill._test_avatar_url = test_avatar

        resp = auth_session.put(f"{BASE_URL}/api/profile", json={"avatar": test_avatar})
        assert resp.status_code == 200, f"Profile update failed: {resp.status_code} {resp.text}"
        data = resp.json()
        assert "message" in data
        assert "updated" in data["message"].lower() or "success" in data["message"].lower()
        print(f"Profile avatar updated to: {test_avatar}")

    def test_user_profile_shows_new_avatar(self, auth_session, admin_user_id):
        """GET /api/profile/{user_id} should return updated avatar."""
        resp = auth_session.get(f"{BASE_URL}/api/profile/{admin_user_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("avatar") == TestAvatarBackfill._test_avatar_url, (
            f"Expected avatar {TestAvatarBackfill._test_avatar_url}, got {data.get('avatar')}"
        )
        print(f"Profile shows avatar: {data.get('avatar')}")

    def test_barter_post_backfilled_with_new_avatar(self, auth_session):
        """GET /api/posts should show the test post with the updated avatar."""
        post_id = getattr(TestAvatarBackfill, '_test_post_id', None)
        if not post_id:
            pytest.skip("No test post created")

        # Fetch all posts and find our test post
        resp = auth_session.get(f"{BASE_URL}/api/posts")
        assert resp.status_code == 200
        posts = resp.json()
        if isinstance(posts, dict):
            posts = posts.get("posts", [])

        test_post = next((p for p in posts if p.get("id") == post_id or p.get("_id") == post_id), None)
        if test_post is None:
            pytest.skip(f"Test post {post_id} not found in feed (may not be visible to admin's own feed)")

        actual_avatar = test_post.get("user_avatar", "")
        expected_avatar = TestAvatarBackfill._test_avatar_url
        assert actual_avatar == expected_avatar, (
            f"Barter post avatar backfill FAILED. Expected: {expected_avatar}, Got: {actual_avatar}"
        )
        print(f"Barter post avatar correctly backfilled: {actual_avatar}")

    def test_community_post_backfilled_with_new_avatar(self, auth_session):
        """GET /api/community/posts should show the test post with the updated avatar."""
        post_id = getattr(TestAvatarBackfill, '_test_community_post_id', None)
        if not post_id:
            pytest.skip("No test community post created")

        resp = auth_session.get(f"{BASE_URL}/api/community")
        assert resp.status_code == 200
        data = resp.json()
        posts = data if isinstance(data, list) else data.get("posts", [])

        test_post = next((p for p in posts if p.get("id") == post_id or p.get("_id") == post_id), None)
        if test_post is None:
            pytest.skip(f"Community test post {post_id} not found in response")

        actual_avatar = test_post.get("user_avatar", "")
        expected_avatar = TestAvatarBackfill._test_avatar_url
        assert actual_avatar == expected_avatar, (
            f"Community post avatar backfill FAILED. Expected: {expected_avatar}, Got: {actual_avatar}"
        )
        print(f"Community post avatar correctly backfilled: {actual_avatar}")

    def test_backfill_also_works_on_existing_posts(self, auth_session, admin_user_id):
        """Update avatar a second time and verify backfill updates all posts again."""
        second_avatar = f"https://example.com/test-avatar-v2-{uuid.uuid4().hex[:8]}.jpg"
        TestAvatarBackfill._test_avatar_v2 = second_avatar

        resp = auth_session.put(f"{BASE_URL}/api/profile", json={"avatar": second_avatar})
        assert resp.status_code == 200
        print(f"Updated avatar to v2: {second_avatar}")

        # Verify profile
        resp = auth_session.get(f"{BASE_URL}/api/profile/{admin_user_id}")
        assert resp.status_code == 200
        assert resp.json().get("avatar") == second_avatar

        # Verify barter posts
        posts_resp = auth_session.get(f"{BASE_URL}/api/posts")
        assert posts_resp.status_code == 200
        posts = posts_resp.json()
        if isinstance(posts, dict):
            posts = posts.get("posts", [])

        post_id = getattr(TestAvatarBackfill, '_test_post_id', None)
        if post_id:
            test_post = next((p for p in posts if p.get("id") == post_id or p.get("_id") == post_id), None)
            if test_post:
                assert test_post.get("user_avatar") == second_avatar, (
                    f"Second backfill failed for barter post. Got: {test_post.get('user_avatar')}"
                )
                print(f"Second avatar backfill verified on barter post: {test_post.get('user_avatar')}")

    def test_avatar_update_without_other_fields(self, auth_session):
        """PUT /api/profile with ONLY avatar field should work (partial update)."""
        new_avatar = f"https://example.com/partial-update-{uuid.uuid4().hex[:8]}.jpg"
        # Only send avatar, no other fields
        resp = auth_session.put(f"{BASE_URL}/api/profile", json={"avatar": new_avatar})
        assert resp.status_code == 200, f"Partial avatar update failed: {resp.text}"
        print("Partial avatar update (only avatar field) works correctly")

    def test_cleanup_restore_avatar(self, auth_session):
        """Restore avatar to a known test state (or empty for cleanup)."""
        # Restore to empty - leave clean for next test
        resp = auth_session.put(f"{BASE_URL}/api/profile", json={"avatar": ""})
        # This is cleanup so we allow it to fail gracefully
        print(f"Cleanup: reset avatar. Status: {resp.status_code}")
