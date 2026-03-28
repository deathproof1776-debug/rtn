"""
Test suite for Categories API endpoints
Tests the categorized goods, skills, and services selectors feature
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCategoriesEndpoints:
    """Test category API endpoints - no auth required"""
    
    def test_get_all_categories(self):
        """GET /api/categories/all - Returns all categories"""
        response = requests.get(f"{BASE_URL}/api/categories/all")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "goods" in data, "Response should have 'goods' key"
        assert "skills" in data, "Response should have 'skills' key"
        assert "services" in data, "Response should have 'services' key"
        
        # Verify counts
        assert len(data["goods"]) == 5, f"Expected 5 goods categories, got {len(data['goods'])}"
        assert len(data["skills"]) == 5, f"Expected 5 skills categories, got {len(data['skills'])}"
        assert len(data["services"]) == 7, f"Expected 7 services categories, got {len(data['services'])}"
        print("PASS: GET /api/categories/all returns all categories correctly")
    
    def test_get_goods_categories(self):
        """GET /api/categories/goods - Returns goods categories"""
        response = requests.get(f"{BASE_URL}/api/categories/goods")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data, "Response should have 'categories' key"
        
        categories = data["categories"]
        expected_categories = ["food", "tools", "crafts", "livestock", "miscellaneous"]
        
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
            assert "name" in categories[cat], f"Category {cat} missing 'name'"
            assert "icon" in categories[cat], f"Category {cat} missing 'icon'"
            assert "items" in categories[cat], f"Category {cat} missing 'items'"
            assert len(categories[cat]["items"]) > 0, f"Category {cat} has no items"
        
        print(f"PASS: GET /api/categories/goods returns {len(categories)} categories")
    
    def test_goods_category_structure(self):
        """Verify goods categories have correct structure and items"""
        response = requests.get(f"{BASE_URL}/api/categories/goods")
        data = response.json()["categories"]
        
        # Test Food category
        assert data["food"]["name"] == "Food"
        assert data["food"]["icon"] == "carrot"
        assert "Fresh Eggs" in data["food"]["items"]
        assert "Honey" in data["food"]["items"]
        
        # Test Tools category
        assert data["tools"]["name"] == "Tools"
        assert data["tools"]["icon"] == "wrench"
        assert "Hand Saws" in data["tools"]["items"]
        
        # Test Crafts category
        assert data["crafts"]["name"] == "Crafts"
        assert data["crafts"]["icon"] == "scissors"
        
        # Test Livestock category
        assert data["livestock"]["name"] == "Livestock"
        assert data["livestock"]["icon"] == "cow"
        
        # Test Miscellaneous category
        assert data["miscellaneous"]["name"] == "Miscellaneous"
        assert data["miscellaneous"]["icon"] == "package"
        
        print("PASS: Goods categories have correct structure")
    
    def test_get_skills_categories(self):
        """GET /api/categories/skills - Returns skills categories"""
        response = requests.get(f"{BASE_URL}/api/categories/skills")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data, "Response should have 'categories' key"
        
        categories = data["categories"]
        expected_categories = ["homestead", "landscape", "trade", "creative", "life"]
        
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
            assert "name" in categories[cat], f"Category {cat} missing 'name'"
            assert "icon" in categories[cat], f"Category {cat} missing 'icon'"
            assert "items" in categories[cat], f"Category {cat} missing 'items'"
        
        print(f"PASS: GET /api/categories/skills returns {len(categories)} categories")
    
    def test_skills_category_structure(self):
        """Verify skills categories have correct structure"""
        response = requests.get(f"{BASE_URL}/api/categories/skills")
        data = response.json()["categories"]
        
        # Test Homestead Skills
        assert data["homestead"]["name"] == "Homestead Skills"
        assert data["homestead"]["icon"] == "house"
        assert "Canning & Preserving" in data["homestead"]["items"]
        
        # Test Landscape Skills
        assert data["landscape"]["name"] == "Landscape & Land Skills"
        assert data["landscape"]["icon"] == "tree"
        
        # Test Trade Skills
        assert data["trade"]["name"] == "Trade & Technical Skills"
        assert data["trade"]["icon"] == "hammer"
        
        # Test Creative Skills
        assert data["creative"]["name"] == "Creative & Artisan Skills"
        assert data["creative"]["icon"] == "palette"
        
        # Test Life Skills
        assert data["life"]["name"] == "Life & Survival Skills"
        assert data["life"]["icon"] == "first-aid"
        
        print("PASS: Skills categories have correct structure")
    
    def test_get_services_categories(self):
        """GET /api/categories/services - Returns services categories"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data, "Response should have 'categories' key"
        
        categories = data["categories"]
        expected_categories = ["labor", "equipment", "animal", "professional", "education", "health", "custom"]
        
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
            assert "name" in categories[cat], f"Category {cat} missing 'name'"
            assert "icon" in categories[cat], f"Category {cat} missing 'icon'"
            assert "items" in categories[cat], f"Category {cat} missing 'items'"
        
        print(f"PASS: GET /api/categories/services returns {len(categories)} categories")
    
    def test_services_category_structure(self):
        """Verify services categories have correct structure"""
        response = requests.get(f"{BASE_URL}/api/categories/services")
        data = response.json()["categories"]
        
        # Test Labor category
        assert data["labor"]["name"] == "Labor & Physical Work"
        assert data["labor"]["icon"] == "users"
        
        # Test Equipment category
        assert data["equipment"]["name"] == "Equipment & Rentals"
        assert data["equipment"]["icon"] == "tractor"
        
        # Test Animal category
        assert data["animal"]["name"] == "Animal Services"
        assert data["animal"]["icon"] == "paw"
        
        # Test Professional category
        assert data["professional"]["name"] == "Professional Services"
        assert data["professional"]["icon"] == "briefcase"
        
        # Test Education category
        assert data["education"]["name"] == "Education & Training"
        assert data["education"]["icon"] == "book"
        
        # Test Health category
        assert data["health"]["name"] == "Health & Personal Services"
        assert data["health"]["icon"] == "heart"
        
        # Test Custom category
        assert data["custom"]["name"] == "Custom & Made-to-Order"
        assert data["custom"]["icon"] == "magic-wand"
        
        print("PASS: Services categories have correct structure")


class TestProfileWithCategories:
    """Test profile update with categorized items"""
    
    @pytest.fixture
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        if login_response.status_code != 200:
            pytest.skip("Could not authenticate")
        return session
    
    def test_update_profile_with_skills(self, auth_session):
        """Test updating profile with skills from categories"""
        # Update profile with skills
        update_data = {
            "skills": ["Canning & Preserving", "Beekeeping", "Carpentry"]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify skills were saved
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        user_data = me_response.json()
        
        # Get profile to verify
        profile_response = auth_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        assert profile_response.status_code == 200
        profile = profile_response.json()
        
        assert "Canning & Preserving" in profile.get("skills", [])
        assert "Beekeeping" in profile.get("skills", [])
        assert "Carpentry" in profile.get("skills", [])
        
        print("PASS: Profile updated with skills from categories")
    
    def test_update_profile_with_goods_offering(self, auth_session):
        """Test updating profile with goods offering"""
        update_data = {
            "goods_offering": ["Fresh Eggs", "Honey", "Handmade Furniture"]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        
        # Verify
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        user_data = me_response.json()
        profile_response = auth_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        profile = profile_response.json()
        
        assert "Fresh Eggs" in profile.get("goods_offering", [])
        assert "Honey" in profile.get("goods_offering", [])
        
        print("PASS: Profile updated with goods offering")
    
    def test_update_profile_with_goods_wanted(self, auth_session):
        """Test updating profile with goods wanted"""
        update_data = {
            "goods_wanted": ["Seeds", "Firewood", "Lumber"]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        
        # Verify
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        user_data = me_response.json()
        profile_response = auth_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        profile = profile_response.json()
        
        assert "Seeds" in profile.get("goods_wanted", [])
        assert "Firewood" in profile.get("goods_wanted", [])
        
        print("PASS: Profile updated with goods wanted")
    
    def test_update_profile_with_services_offering(self, auth_session):
        """Test updating profile with services offering"""
        update_data = {
            "services_offering": ["Farm Labor", "Tractor Rental", "Workshops"]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        
        # Verify
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        user_data = me_response.json()
        profile_response = auth_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        profile = profile_response.json()
        
        assert "Farm Labor" in profile.get("services_offering", [])
        assert "Tractor Rental" in profile.get("services_offering", [])
        
        print("PASS: Profile updated with services offering")
    
    def test_update_profile_with_services_wanted(self, auth_session):
        """Test updating profile with services wanted"""
        update_data = {
            "services_wanted": ["Butchering Services", "Veterinary Services", "Custom Furniture"]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        
        # Verify
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        user_data = me_response.json()
        profile_response = auth_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        profile = profile_response.json()
        
        assert "Butchering Services" in profile.get("services_wanted", [])
        assert "Veterinary Services" in profile.get("services_wanted", [])
        
        print("PASS: Profile updated with services wanted")
    
    def test_update_profile_with_custom_items(self, auth_session):
        """Test updating profile with custom items (not from predefined list)"""
        custom_skill = "TEST_CustomSkill_Unique123"
        custom_good = "TEST_CustomGood_Unique456"
        
        update_data = {
            "skills": [custom_skill],
            "goods_offering": [custom_good]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        
        # Verify custom items were saved
        me_response = auth_session.get(f"{BASE_URL}/api/auth/me")
        user_data = me_response.json()
        profile_response = auth_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        profile = profile_response.json()
        
        assert custom_skill in profile.get("skills", [])
        assert custom_good in profile.get("goods_offering", [])
        
        print("PASS: Profile updated with custom items")
    
    def test_profile_categories_persist_after_reload(self, auth_session):
        """Test that categories persist after profile reload"""
        # Set specific items
        update_data = {
            "skills": ["Welding", "Plumbing"],
            "goods_offering": ["Fresh Vegetables", "Cheese"],
            "goods_wanted": ["Hay", "Straw"],
            "services_offering": ["Fence Building"],
            "services_wanted": ["Midwifery"]
        }
        response = auth_session.put(f"{BASE_URL}/api/profile", json=update_data)
        assert response.status_code == 200
        
        # Create new session and verify persistence
        new_session = requests.Session()
        login_response = new_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@homesteadhub.com",
            "password": "admin123"
        })
        assert login_response.status_code == 200
        
        me_response = new_session.get(f"{BASE_URL}/api/auth/me")
        user_data = me_response.json()
        profile_response = new_session.get(f"{BASE_URL}/api/profile/{user_data['id']}")
        profile = profile_response.json()
        
        assert "Welding" in profile.get("skills", [])
        assert "Fresh Vegetables" in profile.get("goods_offering", [])
        assert "Hay" in profile.get("goods_wanted", [])
        assert "Fence Building" in profile.get("services_offering", [])
        assert "Midwifery" in profile.get("services_wanted", [])
        
        print("PASS: Categories persist after reload")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
