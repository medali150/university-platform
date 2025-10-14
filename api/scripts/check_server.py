#!/usr/bin/env python3
"""
Simple test to check server status and test update
"""
import requests

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:8000")
        print(f"✅ Server is running - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return False

def test_login():
    """Test login functionality"""
    login_data = {
        "email": "test.depthead@university.com", 
        "password": "test123"
    }
    try:
        response = requests.post("http://localhost:8000/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Login successful")
            return response.json().get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Checking server status...")
    if check_server():
        print("\n🔐 Testing login...")
        token = test_login()
        if token:
            print("✅ All basic tests passed!")
        else:
            print("❌ Login test failed")
    else:
        print("❌ Server is not running. Please start the server first.")