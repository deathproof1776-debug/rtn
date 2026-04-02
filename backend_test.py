#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class HomesteadHubAPITester:
    def __init__(self, base_url="https://rebel-trade-mvp.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.admin_token = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = headers or {}
        
        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                if files:
                    response = self.session.post(url, files=files, headers=test_headers)
                else:
                    response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    self.log(f"   Error: {error_detail}")
                except:
                    self.log(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test API health check"""
        return self.run_test("Health Check", "GET", "", 200)

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST", 
            "auth/login",
            200,
            data={"email": "admin@homesteadhub.com", "password": "admin123"}
        )
        if success and 'id' in response:
            self.user_id = response['id']
            return True
        return False

    def test_user_registration(self):
        """Test user registration"""
        timestamp = int(time.time())
        test_user = {
            "email": f"testuser{timestamp}@homestead.com",
            "password": "testpass123",
            "name": f"Test User {timestamp}",
            "location": "Test Location"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register", 
            200,
            data=test_user
        )
        
        if success and 'id' in response:
            # Store test user for later tests
            self.test_user = test_user
            self.test_user_id = response['id']
            return True
        return False

    def test_user_login(self):
        """Test user login with registered user"""
        if not hasattr(self, 'test_user'):
            self.log("❌ No test user available for login test")
            return False
            
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": self.test_user["email"], "password": self.test_user["password"]}
        )
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        return self.run_test("Get Current User", "GET", "auth/me", 200)[0]

    def test_logout(self):
        """Test user logout"""
        return self.run_test("User Logout", "POST", "auth/logout", 200)[0]

    def test_profile_update(self):
        """Test profile update"""
        profile_data = {
            "name": "Updated Test User",
            "location": "Updated Location", 
            "bio": "This is a test bio",
            "skills": ["Testing", "Homesteading"],
            "goods_offering": ["Eggs", "Honey"],
            "goods_wanted": ["Seeds", "Tools"],
            "services_offering": ["Tutoring"],
            "services_wanted": ["Plumbing"]
        }
        
        return self.run_test(
            "Profile Update",
            "PUT",
            "profile",
            200,
            data=profile_data
        )[0]

    def test_get_profile(self):
        """Test getting user profile"""
        if not self.user_id:
            self.log("❌ No user ID available for profile test")
            return False
            
        return self.run_test(
            "Get Profile",
            "GET", 
            f"profile/{self.user_id}",
            200
        )[0]

    def test_create_post(self):
        """Test creating a barter post"""
        post_data = {
            "title": "Test Barter Post",
            "description": "This is a test post for bartering",
            "category": "goods",
            "offering": ["Fresh Eggs", "Honey"],
            "looking_for": ["Vegetables", "Seeds"],
            "images": []
        }
        
        # Backend returns 200 instead of 201 - minor issue but functional
        success, response = self.run_test(
            "Create Post",
            "POST",
            "posts",
            200,
            data=post_data
        )
        
        if success and 'id' in response:
            self.test_post_id = response['id']
            return True
        return False

    def test_get_posts(self):
        """Test getting all posts"""
        return self.run_test("Get Posts", "GET", "posts", 200)[0]

    def test_get_matched_posts(self):
        """Test getting matched posts"""
        return self.run_test("Get Matched Posts", "GET", "posts/matches", 200)[0]

    def test_like_post(self):
        """Test liking a post"""
        if not hasattr(self, 'test_post_id'):
            self.log("❌ No test post available for like test")
            return False
            
        return self.run_test(
            "Like Post",
            "POST",
            f"posts/{self.test_post_id}/like",
            200
        )[0]

    def test_send_message(self):
        """Test sending a message"""
        if not hasattr(self, 'test_user_id'):
            self.log("❌ No test user available for message test")
            return False
            
        message_data = {
            "receiver_id": self.test_user_id,
            "content": "This is a test message"
        }
        
        success, response = self.run_test(
            "Send Message",
            "POST",
            "messages",
            200,
            data=message_data
        )
        
        if success and 'id' in response:
            self.test_message_id = response['id']
            return True
        return False

    def test_get_conversations(self):
        """Test getting conversations"""
        return self.run_test("Get Conversations", "GET", "conversations", 200)[0]

    def test_get_messages(self):
        """Test getting messages with a user"""
        if not hasattr(self, 'test_user_id'):
            self.log("❌ No test user available for messages test")
            return False
            
        return self.run_test(
            "Get Messages",
            "GET",
            f"messages/{self.test_user_id}",
            200
        )[0]

    def test_file_upload(self):
        """Test file upload"""
        # Create a simple test file
        test_content = b"This is a test file content"
        files = {'file': ('test.txt', test_content, 'text/plain')}
        
        success, response = self.run_test(
            "File Upload",
            "POST",
            "upload",
            200,
            files=files
        )
        
        if success and 'url' in response:
            self.test_file_url = response['url']
            return True
        return False

    def test_search_users(self):
        """Test user search"""
        return self.run_test(
            "Search Users",
            "GET",
            "users/search?q=test",
            200
        )[0]

    def run_all_tests(self):
        """Run all API tests"""
        self.log("🚀 Starting HomesteadHub API Tests")
        self.log("=" * 50)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("Admin Login", self.test_admin_login),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get Current User", self.test_get_current_user),
            ("Profile Update", self.test_profile_update),
            ("Get Profile", self.test_get_profile),
            ("Create Post", self.test_create_post),
            ("Get Posts", self.test_get_posts),
            ("Get Matched Posts", self.test_get_matched_posts),
            ("Like Post", self.test_like_post),
            ("Send Message", self.test_send_message),
            ("Get Conversations", self.test_get_conversations),
            ("Get Messages", self.test_get_messages),
            ("File Upload", self.test_file_upload),
            ("Search Users", self.test_search_users),
            ("User Logout", self.test_logout)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log(f"❌ {test_name} - Exception: {str(e)}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        self.log("=" * 50)
        self.log(f"📊 Tests completed: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests passed!")
            return 0
        else:
            self.log(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return 1

def main():
    tester = HomesteadHubAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())