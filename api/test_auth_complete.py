#!/usr/bin/env python3
"""
Simple authentication test for image upload issue
Run this while your backend server is running
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if different
TEST_EMAIL = "boubaked@example.com"  # Teacher user
TEST_PASSWORD = "password123"

def test_login():
    """Test login and get token"""
    print("🔐 Testing login...")
    
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data  # Use form data for login
        )
        
        print(f"Login Status: {response.status_code}")
        print(f"Login Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print(f"✅ Login successful! Token: {token[:20]}...")
                return token
            else:
                print("❌ No token in response")
                return None
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None


def test_auth_endpoint(token):
    """Test authentication with simple endpoint"""
    print("\n🔑 Testing authentication...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/teacher/auth-check",
            headers=headers
        )
        
        print(f"Auth check Status: {response.status_code}")
        print(f"Auth check Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authentication working!")
            return True
        else:
            print(f"❌ Authentication failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Auth test error: {e}")
        return False


def test_teacher_auth(token):
    """Test teacher-specific authentication"""
    print("\n👨‍🏫 Testing teacher authentication...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/teacher/teacher-check",
            headers=headers
        )
        
        print(f"Teacher auth Status: {response.status_code}")
        print(f"Teacher auth Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Teacher authentication working!")
            return True
        else:
            print(f"❌ Teacher authentication failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Teacher auth test error: {e}")
        return False


def test_image_upload_simple(token):
    """Test image upload without actual file first"""
    print("\n📤 Testing image upload endpoint (without file)...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Test with a simple POST request (should fail but with different error)
    try:
        response = requests.post(
            f"{BASE_URL}/teacher/profile/upload-image",
            headers=headers
        )
        
        print(f"Upload test Status: {response.status_code}")
        print(f"Upload test Response: {response.text}")
        
        if response.status_code == 422:  # Validation error for missing file
            print("✅ Upload endpoint reachable! (422 is expected without file)")
            return True
        elif response.status_code == 401:
            print("❌ Upload endpoint returns 401 - authentication issue!")
            return False
        else:
            print(f"🤔 Upload endpoint returned: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
        return False


def create_test_image():
    """Create a simple test image"""
    try:
        from PIL import Image
        
        # Create a simple 100x100 red image
        img = Image.new('RGB', (100, 100), color='red')
        test_path = 'test_image.jpg'
        img.save(test_path)
        
        print(f"✅ Created test image: {test_path}")
        return test_path
        
    except ImportError:
        print("⚠️ PIL not available, using text file as test")
        # Create a simple text file to test upload validation
        test_path = 'test_file.txt'
        with open(test_path, 'w') as f:
            f.write("This is a test file")
        return test_path


def test_full_image_upload(token):
    """Test actual image upload"""
    print("\n📷 Testing full image upload...")
    
    # Create test image
    test_file = create_test_image()
    
    headers = {
        "Authorization": f"Bearer {token}"
        # DO NOT set Content-Type for multipart/form-data
        # Let requests set it automatically
    }
    
    try:
        with open(test_file, 'rb') as f:
            files = {
                'file': ('test_image.jpg', f, 'image/jpeg')
            }
            
            response = requests.post(
                f"{BASE_URL}/teacher/profile/upload-image-debug",
                headers=headers,
                files=files
            )
        
        print(f"Full upload Status: {response.status_code}")
        print(f"Full upload Response: {response.text}")
        
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        
        if response.status_code == 200:
            print("✅ Image upload successful!")
            return True
        else:
            print(f"❌ Image upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Full upload error: {e}")
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)
        return False


def main():
    """Run all tests"""
    print("🚀 Starting authentication and upload tests...")
    print(f"Backend URL: {BASE_URL}")
    print("=" * 50)
    
    # Step 1: Login
    token = test_login()
    if not token:
        print("❌ Cannot proceed without valid token")
        return
    
    # Step 2: Test basic auth
    if not test_auth_endpoint(token):
        print("❌ Basic authentication failed")
        return
    
    # Step 3: Test teacher auth
    if not test_teacher_auth(token):
        print("❌ Teacher authentication failed")
        return
    
    # Step 4: Test upload endpoint accessibility
    if not test_image_upload_simple(token):
        print("❌ Upload endpoint has authentication issues")
        return
    
    # Step 5: Test full upload
    test_full_image_upload(token)
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")


if __name__ == "__main__":
    main()