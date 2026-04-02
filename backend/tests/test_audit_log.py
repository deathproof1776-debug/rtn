"""
Test suite for Admin Activity Log / Audit Trail feature
Tests audit log creation for admin actions and GET /api/admin/audit-log endpoint
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from environment
ADMIN_EMAIL = os.environ.get('TEST_ADMIN_EMAIL', 'demo@rebeltrade.net')
ADMIN_PASSWORD = os.environ.get('TEST_ADMIN_PASSWORD', 'demo123')
REGULAR_USER_EMAIL = os.environ.get('TEST_REGULAR_EMAIL', 'sarah.meadow@example.com')
REGULAR_USER_PASSWORD = os.environ.get('TEST_REGULAR_PASSWORD', 'homestead123')


@pytest.fixture(scope="module")
def admin_session():
    """Get authenticated admin session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    
    data = response.json()
    assert data.get("role") == "admin", f"User is not admin, role: {data.get('role')}"
    
    return session


@pytest.fixture(scope="module")
def regular_session():
    """Get authenticated regular user session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": REGULAR_USER_EMAIL,
        "password": REGULAR_USER_PASSWORD
    })
    
    if response.status_code != 200:
        pytest.skip(f"Regular user login failed: {response.status_code}")
    
    return session


class TestAuditLogEndpoint:
    """Tests for GET /api/admin/audit-log endpoint"""
    
    def test_audit_log_returns_correct_structure(self, admin_session):
        """GET /api/admin/audit-log returns logs with correct fields"""
        response = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "logs" in data, "Response should contain 'logs' field"
        assert "total" in data, "Response should contain 'total' field"
        assert isinstance(data["logs"], list), "logs should be a list"
        assert isinstance(data["total"], int), "total should be an integer"
        
        print(f"Audit log has {data['total']} entries")
    
    def test_audit_log_entry_has_required_fields(self, admin_session):
        """Each audit log entry should have required fields"""
        response = admin_session.get(f"{BASE_URL}/api/admin/audit-log?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data["logs"]) > 0:
            log_entry = data["logs"][0]
            required_fields = ["admin_id", "admin_name", "action", "target_type", "target_id", "target_name", "created_at"]
            
            for field in required_fields:
                assert field in log_entry, f"Log entry missing required field: {field}"
            
            # details is optional but should be present
            assert "details" in log_entry, "Log entry should have 'details' field"
            
            print(f"Sample log entry: action={log_entry['action']}, target={log_entry['target_name']}")
        else:
            print("No audit log entries found - will be created by subsequent tests")
    
    def test_audit_log_sorted_by_created_at_desc(self, admin_session):
        """Audit logs should be sorted by created_at descending (newest first)"""
        response = admin_session.get(f"{BASE_URL}/api/admin/audit-log?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data["logs"]) >= 2:
            for i in range(len(data["logs"]) - 1):
                current_time = data["logs"][i]["created_at"]
                next_time = data["logs"][i + 1]["created_at"]
                assert current_time >= next_time, f"Logs not sorted correctly: {current_time} should be >= {next_time}"
            print("Audit logs are correctly sorted by created_at descending")
        else:
            print("Not enough logs to verify sorting")
    
    def test_non_admin_cannot_access_audit_log(self, regular_session):
        """Non-admin users should get 403 when accessing audit log"""
        response = regular_session.get(f"{BASE_URL}/api/admin/audit-log")
        
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("Non-admin correctly denied access to audit log (403)")


class TestVerifyTraderAuditLog:
    """Tests that verify-trader action creates audit log entries"""
    
    def test_verify_trader_creates_audit_log(self, admin_session):
        """POST /api/admin/verify-trader should create an audit log entry"""
        # First get a user to verify
        users_response = admin_session.get(f"{BASE_URL}/api/admin/users?limit=50")
        assert users_response.status_code == 200
        
        users = users_response.json().get("users", [])
        # Find a non-admin user to toggle verification
        test_user = None
        for u in users:
            if u.get("role") != "admin" and u.get("email") != ADMIN_EMAIL:
                test_user = u
                break
        
        if not test_user:
            pytest.skip("No non-admin user found to test verification")
        
        user_id = test_user["_id"]
        current_verified = test_user.get("is_verified", False)
        new_verified = not current_verified
        
        # Get current audit log count
        audit_before = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        count_before = audit_before.json().get("total", 0)
        
        # Verify/unverify the trader
        verify_response = admin_session.post(f"{BASE_URL}/api/admin/verify-trader", json={
            "user_id": user_id,
            "is_verified": new_verified
        })
        
        assert verify_response.status_code == 200, f"Verify trader failed: {verify_response.text}"
        
        # Check audit log was created
        time.sleep(0.5)  # Small delay for DB write
        audit_after = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        count_after = audit_after.json().get("total", 0)
        
        assert count_after > count_before, f"Audit log count should increase. Before: {count_before}, After: {count_after}"
        
        # Check the latest log entry
        latest_log = audit_after.json()["logs"][0]
        expected_action = "verified" if new_verified else "unverified"
        assert latest_log["action"] == expected_action, f"Expected action '{expected_action}', got '{latest_log['action']}'"
        assert latest_log["target_id"] == user_id, f"Target ID mismatch"
        assert latest_log["target_type"] == "user", f"Target type should be 'user'"
        
        print(f"Verify trader audit log created: {latest_log['action']} {latest_log['target_name']}")
        
        # Revert the change
        admin_session.post(f"{BASE_URL}/api/admin/verify-trader", json={
            "user_id": user_id,
            "is_verified": current_verified
        })


class TestRoleChangeAuditLog:
    """Tests that role change action creates audit log entries"""
    
    def test_role_change_creates_audit_log(self, admin_session):
        """PUT /api/admin/users/{id}/role should create an audit log entry"""
        # Get users
        users_response = admin_session.get(f"{BASE_URL}/api/admin/users?limit=50")
        assert users_response.status_code == 200
        
        users = users_response.json().get("users", [])
        # Find a non-admin user to change role
        test_user = None
        for u in users:
            if u.get("role") == "user" and u.get("email") != ADMIN_EMAIL:
                test_user = u
                break
        
        if not test_user:
            pytest.skip("No regular user found to test role change")
        
        user_id = test_user["_id"]
        
        # Get current audit log count
        audit_before = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        count_before = audit_before.json().get("total", 0)
        
        # Change role to admin
        role_response = admin_session.put(f"{BASE_URL}/api/admin/users/{user_id}/role", json={
            "role": "admin"
        })
        
        assert role_response.status_code == 200, f"Role change failed: {role_response.text}"
        
        # Check audit log was created
        time.sleep(0.5)
        audit_after = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        count_after = audit_after.json().get("total", 0)
        
        assert count_after > count_before, f"Audit log count should increase"
        
        # Check the latest log entry
        latest_log = audit_after.json()["logs"][0]
        assert latest_log["action"] == "role_changed", f"Expected action 'role_changed', got '{latest_log['action']}'"
        assert latest_log["target_id"] == user_id
        assert "admin" in latest_log.get("details", "").lower(), "Details should mention the new role"
        
        print(f"Role change audit log created: {latest_log['details']}")
        
        # Revert the change
        admin_session.put(f"{BASE_URL}/api/admin/users/{user_id}/role", json={
            "role": "user"
        })


class TestDeletePostAuditLog:
    """Tests that delete post action creates audit log entries"""
    
    def test_delete_post_creates_audit_log(self, admin_session):
        """DELETE /api/admin/posts/{id} should create an audit log entry"""
        # First create a test post
        create_response = admin_session.post(f"{BASE_URL}/api/posts", json={
            "title": "TEST_AUDIT_POST_DELETE",
            "description": "Test post for audit log testing",
            "category": "goods",
            "offering": ["Test Item"],
            "looking_for": ["Another Item"]
        })
        
        if create_response.status_code != 201:
            pytest.skip(f"Could not create test post: {create_response.text}")
        
        post_id = create_response.json().get("id")
        
        # Get current audit log count
        audit_before = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        count_before = audit_before.json().get("total", 0)
        
        # Delete the post
        delete_response = admin_session.delete(f"{BASE_URL}/api/admin/posts/{post_id}")
        
        assert delete_response.status_code == 200, f"Delete post failed: {delete_response.text}"
        
        # Check audit log was created
        time.sleep(0.5)
        audit_after = admin_session.get(f"{BASE_URL}/api/admin/audit-log")
        count_after = audit_after.json().get("total", 0)
        
        assert count_after > count_before, f"Audit log count should increase"
        
        # Check the latest log entry
        latest_log = audit_after.json()["logs"][0]
        assert latest_log["action"] == "deleted_post", f"Expected action 'deleted_post', got '{latest_log['action']}'"
        assert latest_log["target_id"] == post_id
        assert latest_log["target_type"] == "post"
        
        print(f"Delete post audit log created: {latest_log['target_name']}")


class TestAuditLogPagination:
    """Tests for audit log pagination"""
    
    def test_audit_log_respects_limit(self, admin_session):
        """Audit log should respect limit parameter"""
        response = admin_session.get(f"{BASE_URL}/api/admin/audit-log?limit=2")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["logs"]) <= 2, f"Should return at most 2 logs, got {len(data['logs'])}"
        print(f"Pagination test: requested limit=2, got {len(data['logs'])} logs")
    
    def test_audit_log_respects_skip(self, admin_session):
        """Audit log should respect skip parameter"""
        # Get first page
        first_page = admin_session.get(f"{BASE_URL}/api/admin/audit-log?limit=2&skip=0")
        assert first_page.status_code == 200
        
        # Get second page
        second_page = admin_session.get(f"{BASE_URL}/api/admin/audit-log?limit=2&skip=2")
        assert second_page.status_code == 200
        
        first_logs = first_page.json()["logs"]
        second_logs = second_page.json()["logs"]
        
        if len(first_logs) > 0 and len(second_logs) > 0:
            # Ensure no overlap
            first_ids = [log.get("created_at") for log in first_logs]
            second_ids = [log.get("created_at") for log in second_logs]
            
            for sid in second_ids:
                assert sid not in first_ids, "Skip should return different logs"
            
            print("Pagination skip working correctly")
        else:
            print("Not enough logs to verify skip pagination")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
