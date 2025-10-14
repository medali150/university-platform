#!/usr/bin/env python3
"""
SIMPLE AUTH API TEST
==================
Test basic API functionality to isolate server issues
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_api():
    """Test basic API endpoints"""
    
    print("🔍 BASIC API DIAGNOSTICS")
    print("=" * 40)
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Health check OK: {response.text}")
        else:
            print(f"   ❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
    
    # Test 2: Basic GET endpoints
    print("\n2️⃣ Testing Basic Endpoints...")
    endpoints_to_test = [
        "/docs",
        "/auth/users",
        "/departments"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code >= 500:
                print(f"      ❌ Server error: {response.text[:100]}...")
        except Exception as e:
            print(f"   {endpoint}: Error - {str(e)}")
    
    # Test 3: Simple admin login
    print("\n3️⃣ Testing Admin Login...")
    
    login_attempts = [
        {"email": "admin@university.com", "password": "admin123"},
        {"login": "admin@university.com", "password": "admin123"}
    ]
    
    for i, login_data in enumerate(login_attempts, 1):
        try:
            print(f"\n   Attempt {i}: {json.dumps(login_data)}")
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"   ✅ Login successful!")
                print(f"   User: {token_data['user']['firstName']} {token_data['user']['lastName']}")
                
                # Test authenticated endpoint
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                print(f"   /auth/me: {me_response.status_code}")
                
                return token_data['access_token']
                
            elif response.status_code == 401:
                print(f"   ❌ Authentication failed: {response.text}")
            elif response.status_code >= 500:
                print(f"   ❌ Server error: {response.text}")
            else:
                print(f"   ❌ Other error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
    
    return None

if __name__ == "__main__":
    token = test_basic_api()
    if token:
        print(f"\n✅ API is working! Token: {token[:30]}...")
    else:
        print(f"\n❌ API has issues that need to be fixed")