#!/usr/bin/env python3
"""
Quick test script to verify department heads endpoint fix
"""

import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:8000"

def test_admin_login():
    """Test admin login and get token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "login": "admin",
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print("✅ Admin login successful")
            return token
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {str(e)}")
        return None

def test_department_heads_endpoint(token):
    """Test the department heads GET endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(
            f"{BASE_URL}/admin/department-heads/",
            headers=headers
        )
        
        print(f"📊 Department Heads Endpoint Test")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Request successful!")
            print(f"   Found {len(data)} department heads")
            
            # Print first few entries
            for i, head in enumerate(data[:3]):
                print(f"   {i+1}. {head.get('firstName', '')} {head.get('lastName', '')} - {head.get('email', '')}")
                
            return True
        else:
            print(f"❌ Request failed")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during request: {str(e)}")
        return False

def main():
    """Run the test"""
    print("🔧 Testing Department Heads Endpoint Fix")
    print("=" * 50)
    
    # Login as admin
    token = test_admin_login()
    if not token:
        print("❌ Cannot proceed without admin token")
        return
    
    # Test the endpoint
    success = test_department_heads_endpoint(token)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Department heads endpoint is now working!")
    else:
        print("❌ Department heads endpoint still has issues")

if __name__ == "__main__":
    main()