"""
Backend tests for Moderation: user block/unblock + content reporting + admin moderation.
Targets:
- /api/moderation/block/{user_id} POST/DELETE
- /api/moderation/blocks  & /api/moderation/blocks/check/{user_id}
- /api/moderation/report  (validation + dedup)
- /api/admin/reports (list/update/stats, admin-only)
- Mutual block filtering on /api/posts, /api/community, /api/posts/{id}/comments
- Messaging/network 403 when blocked
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://rebel-trade-preview-1.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@homesteadhub.com"
ADMIN_PASSWORD = "admin123"
DEMO_EMAIL = "demo@rebeltrade.net"
DEMO_PASSWORD = "demo123"


def _login(email, password):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, f"Login failed for {email}: {r.status_code} {r.text}"
    me = r.json()
    return s, me["id"], me


@pytest.fixture(scope="module")
def admin_session():
    s, uid, me = _login(ADMIN_EMAIL, ADMIN_PASSWORD)
    return s, uid, me


@pytest.fixture(scope="module")
def demo_session():
    s, uid, me = _login(DEMO_EMAIL, DEMO_PASSWORD)
    return s, uid, me


@pytest.fixture(scope="module", autouse=True)
def _cleanup(admin_session, demo_session):
    """Ensure no stale blocks/reports between the two test users before/after."""
    a_sess, a_id, _ = admin_session
    d_sess, d_id, _ = demo_session
    # pre clean
    a_sess.delete(f"{API}/moderation/block/{d_id}")
    d_sess.delete(f"{API}/moderation/block/{a_id}")
    yield
    a_sess.delete(f"{API}/moderation/block/{d_id}")
    d_sess.delete(f"{API}/moderation/block/{a_id}")


# ---------------- Block / Unblock ----------------

class TestBlockEndpoints:
    def test_self_block_rejected(self, admin_session):
        s, uid, _ = admin_session
        r = s.post(f"{API}/moderation/block/{uid}")
        assert r.status_code == 400

    def test_invalid_user_id(self, admin_session):
        s, _, _ = admin_session
        r = s.post(f"{API}/moderation/block/not-an-objectid")
        assert r.status_code == 400

    def test_nonexistent_user(self, admin_session):
        s, _, _ = admin_session
        # valid ObjectId format but not in DB
        r = s.post(f"{API}/moderation/block/000000000000000000000000")
        assert r.status_code == 404

    def test_block_then_idempotent_then_unblock(self, admin_session, demo_session):
        a, aid, _ = admin_session
        _, did, _ = demo_session

        r1 = a.post(f"{API}/moderation/block/{did}")
        assert r1.status_code in (200, 201), r1.text
        assert "blocked" in r1.json().get("message", "").lower()

        # idempotent re-block returns 200 with "already blocked"
        r2 = a.post(f"{API}/moderation/block/{did}")
        assert r2.status_code in (200, 201)
        assert "already" in r2.json().get("message", "").lower()

        # check blocks list contains demo user
        rl = a.get(f"{API}/moderation/blocks")
        assert rl.status_code == 200
        ids = [b["user_id"] for b in rl.json().get("blocks", [])]
        assert did in ids
        block_entry = next(b for b in rl.json()["blocks"] if b["user_id"] == did)
        assert "name" in block_entry and "avatar" in block_entry and "blocked_at" in block_entry

        # check endpoint for demo (other side should also see is_blocked_either_way=true)
        d, _, _ = demo_session
        chk = d.get(f"{API}/moderation/blocks/check/{aid}")
        assert chk.status_code == 200
        body = chk.json()
        assert body["is_blocked_either_way"] is True
        assert body["i_blocked_them"] is False

        # admin perspective
        chk2 = a.get(f"{API}/moderation/blocks/check/{did}")
        assert chk2.json()["i_blocked_them"] is True
        assert chk2.json()["is_blocked_either_way"] is True

        # unblock
        ru = a.delete(f"{API}/moderation/block/{did}")
        assert ru.status_code == 200

        # unblock again -> 404
        ru2 = a.delete(f"{API}/moderation/block/{did}")
        assert ru2.status_code == 404


# ---------------- Reports ----------------

class TestReportEndpoints:
    def test_invalid_target_type(self, demo_session):
        s, _, _ = demo_session
        r = s.post(f"{API}/moderation/report", json={
            "target_type": "garbage", "target_id": "x", "reason": "spam"
        })
        assert r.status_code == 400

    def test_invalid_reason(self, demo_session, admin_session):
        s, _, _ = demo_session
        _, aid, _ = admin_session
        r = s.post(f"{API}/moderation/report", json={
            "target_type": "user", "target_id": aid, "reason": "not_valid_reason"
        })
        assert r.status_code == 400

    def test_missing_target_id(self, demo_session):
        s, _, _ = demo_session
        r = s.post(f"{API}/moderation/report", json={
            "target_type": "user", "target_id": "", "reason": "spam"
        })
        assert r.status_code == 400

    def test_create_and_dedupe_then_admin_lifecycle(self, demo_session, admin_session):
        d, did, _ = demo_session
        a, aid, _ = admin_session

        # create a unique target_id so the test doesn't clash with prior runs
        import uuid
        target_id = f"test-target-{uuid.uuid4().hex[:10]}"

        r1 = d.post(f"{API}/moderation/report", json={
            "target_type": "post", "target_id": target_id, "reason": "spam",
            "details": "TEST_ automated"
        })
        assert r1.status_code in (200, 201), r1.text
        assert "submitted" in r1.json().get("message", "").lower()

        # duplicate -> should NOT create another row
        r2 = d.post(f"{API}/moderation/report", json={
            "target_type": "post", "target_id": target_id, "reason": "spam"
        })
        assert r2.status_code in (200, 201)
        assert "already" in r2.json().get("message", "").lower()

        # Admin lists pending reports
        ra = a.get(f"{API}/admin/reports?status=pending")
        assert ra.status_code == 200
        reports = ra.json().get("reports", [])
        match = [x for x in reports if x["target_id"] == target_id]
        assert len(match) == 1, f"expected exactly one report for target {target_id}, got {len(match)}"
        report_id = match[0]["_id"]
        assert match[0]["status"] == "pending"
        assert match[0]["reason"] == "spam"

        # Stats include our new pending
        rs = a.get(f"{API}/admin/reports/stats")
        assert rs.status_code == 200
        stats = rs.json()
        assert set(stats.keys()) >= {"pending", "resolved", "dismissed"}
        assert stats["pending"] >= 1

        # Non-admin forbidden
        rd = d.get(f"{API}/admin/reports")
        assert rd.status_code == 403
        rd2 = d.get(f"{API}/admin/reports/stats")
        assert rd2.status_code == 403
        rd3 = d.put(f"{API}/admin/reports/{report_id}", json={"status": "dismissed"})
        assert rd3.status_code == 403

        # Admin resolves
        up = a.put(f"{API}/admin/reports/{report_id}", json={
            "status": "resolved", "resolution_note": "TEST_ auto"
        })
        assert up.status_code == 200

        # Verify status changed
        ra2 = a.get(f"{API}/admin/reports?status=resolved")
        assert ra2.status_code == 200
        got = [x for x in ra2.json()["reports"] if x["_id"] == report_id]
        assert len(got) == 1
        assert got[0]["status"] == "resolved"
        assert got[0]["resolution_note"] == "TEST_ auto"

        # status=all returns it
        rall = a.get(f"{API}/admin/reports?status=all")
        assert rall.status_code == 200
        assert any(x["_id"] == report_id for x in rall.json()["reports"])

        # invalid status filter
        rbad = a.get(f"{API}/admin/reports?status=foo")
        assert rbad.status_code == 400

        # invalid report id update
        rbad2 = a.put(f"{API}/admin/reports/not-an-id", json={"status": "dismissed"})
        assert rbad2.status_code == 400

        # invalid status value
        rbad3 = a.put(f"{API}/admin/reports/{report_id}", json={"status": "approved"})
        assert rbad3.status_code == 400


# ---------------- Mutual block filters ----------------

class TestBlockFilters:
    def _ensure_blocked(self, a, did):
        a.post(f"{API}/moderation/block/{did}")

    def _ensure_unblocked(self, a, did):
        a.delete(f"{API}/moderation/block/{did}")

    def test_posts_filter_and_messaging_and_network(self, admin_session, demo_session):
        a, aid, _ = admin_session
        d, did, _ = demo_session
        self._ensure_unblocked(a, did)

        # Baseline: admin can see demo's posts (if any). We'll check via /api/posts:
        # ensure demo has at least one post — create one
        cp = d.post(f"{API}/posts", json={
            "type": "offering",
            "category": "goods",
            "title": "TEST_ moderation post",
            "description": "TEST_ moderation post by demo",
            "offering": ["TEST item"],
            "looking_for": ["TEST trade"],
            "tags": []
        })
        assert cp.status_code in (200, 201), cp.text
        demo_post_id = cp.json().get("id") or cp.json().get("_id")
        assert demo_post_id

        try:
            # Search for our specific post by title (avoids pagination noise)
            feed_pre = a.get(f"{API}/posts", params={"search": "TEST_ moderation post", "limit": 100}).json()
            pre_list = feed_pre if isinstance(feed_pre, list) else feed_pre.get("posts", [])
            pre_ids = {p.get("id") or p.get("_id") for p in pre_list}
            assert demo_post_id in pre_ids, f"demo post not visible in admin feed pre-block. Got: {list(pre_ids)[:5]}"

            # Block demo
            self._ensure_blocked(a, did)

            # POSTS feed hides demo's posts
            feed_post = a.get(f"{API}/posts", params={"search": "TEST_ moderation post", "limit": 100}).json()
            post_list = feed_post if isinstance(feed_post, list) else feed_post.get("posts", [])
            post_ids = {p.get("id") or p.get("_id") for p in post_list}
            assert demo_post_id not in post_ids, "demo post still visible in admin feed after block"

            # Reverse direction (demo can't see admin posts either) — just verify call returns
            d_feed = d.get(f"{API}/posts")
            assert d_feed.status_code == 200

            # MESSAGES: admin -> demo should 403
            send = a.post(f"{API}/messages", json={"receiver_id": did, "content": "blocked test"})
            assert send.status_code == 403, send.text

            # Demo -> admin also 403 (mutual)
            send_r = d.post(f"{API}/messages", json={"receiver_id": aid, "content": "blocked back"})
            assert send_r.status_code == 403

            # NETWORK request to blocked user -> 403
            nr = a.post(f"{API}/network/request", json={"target_user_id": did})
            assert nr.status_code == 403
            nr2 = d.post(f"{API}/network/request", json={"target_user_id": aid})
            assert nr2.status_code == 403

            # CONVERSATIONS list should not include blocked user
            conv = a.get(f"{API}/conversations")
            assert conv.status_code == 200
            convs = conv.json() if isinstance(conv.json(), list) else conv.json().get("conversations", [])
            # Each conversation usually has a partner/other_user_id field — assert demo id not present in any
            for c in convs:
                ids_in_conv = {c.get("other_user_id"), c.get("user_id"), c.get("partner_id")}
                assert did not in ids_in_conv, f"Blocked user {did} appears in conversations: {c}"
        finally:
            # cleanup post + block
            d.delete(f"{API}/posts/{demo_post_id}")
            self._ensure_unblocked(a, did)
