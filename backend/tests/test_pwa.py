"""
PWA Feature Tests - Testing manifest, service worker, offline page, and icons
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPWAManifest:
    """Tests for PWA manifest.json"""
    
    def test_manifest_accessible(self):
        """Manifest file should be accessible"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200, f"Manifest not accessible: {response.status_code}"
        print("SUCCESS: Manifest is accessible")
    
    def test_manifest_content_type(self):
        """Manifest should have correct content type"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        content_type = response.headers.get('Content-Type', '')
        assert 'json' in content_type.lower(), f"Wrong content type: {content_type}"
        print(f"SUCCESS: Manifest content type is correct: {content_type}")
    
    def test_manifest_required_fields(self):
        """Manifest should contain required PWA fields"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        
        required_fields = ['name', 'short_name', 'start_url', 'display', 'icons']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
            print(f"SUCCESS: Manifest has required field '{field}'")
    
    def test_manifest_app_metadata(self):
        """Manifest should have correct app metadata"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        
        assert data['name'] == 'Rebel Trade Network', f"Wrong name: {data.get('name')}"
        assert data['short_name'] == 'RebelTrade', f"Wrong short_name: {data.get('short_name')}"
        assert data['display'] == 'standalone', f"Wrong display mode: {data.get('display')}"
        assert data['start_url'] == '/', f"Wrong start_url: {data.get('start_url')}"
        print("SUCCESS: Manifest has correct app metadata")
    
    def test_manifest_theme_colors(self):
        """Manifest should have theme and background colors"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        
        assert 'theme_color' in data, "Missing theme_color"
        assert 'background_color' in data, "Missing background_color"
        assert data['theme_color'] == '#C35E37', f"Wrong theme_color: {data.get('theme_color')}"
        assert data['background_color'] == '#0C0A09', f"Wrong background_color: {data.get('background_color')}"
        print("SUCCESS: Manifest has correct theme colors")


class TestPWAServiceWorker:
    """Tests for Service Worker"""
    
    def test_service_worker_accessible(self):
        """Service worker file should be accessible"""
        response = requests.get(f"{BASE_URL}/sw.js")
        assert response.status_code == 200, f"Service worker not accessible: {response.status_code}"
        print("SUCCESS: Service worker is accessible")
    
    def test_service_worker_content_type(self):
        """Service worker should have correct content type"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content_type = response.headers.get('Content-Type', '')
        assert 'javascript' in content_type.lower(), f"Wrong content type: {content_type}"
        print(f"SUCCESS: Service worker content type is correct: {content_type}")
    
    def test_service_worker_has_cache_name(self):
        """Service worker should define cache name"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert 'CACHE_NAME' in content, "Service worker missing CACHE_NAME"
        assert 'rebel-trade' in content.lower(), "Service worker cache name should contain 'rebel-trade'"
        print("SUCCESS: Service worker has cache name defined")
    
    def test_service_worker_has_install_handler(self):
        """Service worker should have install event handler"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert "addEventListener('install'" in content or 'addEventListener("install"' in content, \
            "Service worker missing install event handler"
        print("SUCCESS: Service worker has install event handler")
    
    def test_service_worker_has_fetch_handler(self):
        """Service worker should have fetch event handler"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert "addEventListener('fetch'" in content or 'addEventListener("fetch"' in content, \
            "Service worker missing fetch event handler"
        print("SUCCESS: Service worker has fetch event handler")
    
    def test_service_worker_has_offline_fallback(self):
        """Service worker should reference offline page"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert 'offline.html' in content.lower(), "Service worker missing offline page reference"
        print("SUCCESS: Service worker has offline fallback")


class TestPWAOfflinePage:
    """Tests for offline fallback page"""
    
    def test_offline_page_accessible(self):
        """Offline page should be accessible"""
        response = requests.get(f"{BASE_URL}/offline.html")
        assert response.status_code == 200, f"Offline page not accessible: {response.status_code}"
        print("SUCCESS: Offline page is accessible")
    
    def test_offline_page_content_type(self):
        """Offline page should have correct content type"""
        response = requests.get(f"{BASE_URL}/offline.html")
        content_type = response.headers.get('Content-Type', '')
        assert 'html' in content_type.lower(), f"Wrong content type: {content_type}"
        print(f"SUCCESS: Offline page content type is correct: {content_type}")
    
    def test_offline_page_has_title(self):
        """Offline page should have proper title"""
        response = requests.get(f"{BASE_URL}/offline.html")
        content = response.text
        assert '<title>' in content, "Offline page missing title tag"
        assert 'Offline' in content, "Offline page title should contain 'Offline'"
        print("SUCCESS: Offline page has proper title")
    
    def test_offline_page_has_retry_button(self):
        """Offline page should have retry button"""
        response = requests.get(f"{BASE_URL}/offline.html")
        content = response.text
        assert 'retry' in content.lower() or 'try again' in content.lower(), \
            "Offline page missing retry functionality"
        print("SUCCESS: Offline page has retry button")
    
    def test_offline_page_has_branding(self):
        """Offline page should have app branding"""
        response = requests.get(f"{BASE_URL}/offline.html")
        content = response.text
        assert 'Rebel Trade' in content, "Offline page missing app branding"
        print("SUCCESS: Offline page has app branding")


class TestPWAIcons:
    """Tests for PWA icons at all required sizes"""
    
    @pytest.mark.parametrize("size", [72, 96, 128, 144, 152, 192, 384, 512])
    def test_icon_accessible(self, size):
        """Icon at specified size should be accessible"""
        response = requests.get(f"{BASE_URL}/icons/icon-{size}x{size}.png")
        assert response.status_code == 200, f"Icon {size}x{size} not accessible: {response.status_code}"
        print(f"SUCCESS: Icon {size}x{size} is accessible")
    
    @pytest.mark.parametrize("size", [72, 96, 128, 144, 152, 192, 384, 512])
    def test_icon_content_type(self, size):
        """Icon should have correct content type"""
        response = requests.get(f"{BASE_URL}/icons/icon-{size}x{size}.png")
        content_type = response.headers.get('Content-Type', '')
        assert 'image' in content_type.lower(), f"Icon {size}x{size} wrong content type: {content_type}"
        print(f"SUCCESS: Icon {size}x{size} has correct content type")
    
    def test_manifest_icons_match_files(self):
        """Icons in manifest should match available files"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        
        for icon in data.get('icons', []):
            icon_url = icon.get('src', '')
            if icon_url.startswith('/'):
                icon_url = icon_url[1:]  # Remove leading slash
            
            icon_response = requests.get(f"{BASE_URL}/{icon_url}")
            assert icon_response.status_code == 200, f"Manifest icon not found: {icon_url}"
            print(f"SUCCESS: Manifest icon exists: {icon_url}")


class TestPWAIndexHTML:
    """Tests for index.html PWA meta tags"""
    
    def test_index_has_manifest_link(self):
        """Index.html should link to manifest"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'manifest' in content.lower(), "Index.html missing manifest link"
        print("SUCCESS: Index.html has manifest link")
    
    def test_index_has_theme_color(self):
        """Index.html should have theme-color meta tag"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'theme-color' in content.lower(), "Index.html missing theme-color meta tag"
        print("SUCCESS: Index.html has theme-color meta tag")
    
    def test_index_has_apple_meta_tags(self):
        """Index.html should have Apple PWA meta tags"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'apple-mobile-web-app-capable' in content.lower(), \
            "Index.html missing apple-mobile-web-app-capable"
        assert 'apple-touch-icon' in content.lower(), \
            "Index.html missing apple-touch-icon"
        print("SUCCESS: Index.html has Apple PWA meta tags")


class TestLoginFlow:
    """Tests to verify login still works after PWA changes"""
    
    def test_login_endpoint_exists(self):
        """Login endpoint should be accessible"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        # Should return 200 for valid credentials or 401 for invalid
        assert response.status_code in [200, 401], f"Unexpected status: {response.status_code}"
        print(f"SUCCESS: Login endpoint accessible, status: {response.status_code}")
    
    def test_login_with_demo_credentials(self):
        """Login with demo credentials should work"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "demo@rebeltrade.net",
            "password": "demo123"
        })
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        # API returns user data directly with id and email
        assert 'id' in data or 'email' in data, "Login response missing user data"
        print("SUCCESS: Login with demo credentials works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
