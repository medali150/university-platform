#!/usr/bin/env python3
"""
Quick Department Heads API Test
"""

import requests
import json

def test_department_heads_endpoint():
    """Test the department heads endpoint directly"""
    
    # First, let's try the health endpoint to make sure server is running
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"🏥 Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Database: {response.json().get('database', 'unknown')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not running: {e}")
        return False
    
    # Try to get all users first to see if there's an admin
    try:
        # Let's try to find any existing admin user by testing a simple endpoint
        response = requests.get("http://127.0.0.1:8000/auth/test", timeout=5)
        print(f"📊 Auth test endpoint: {response.status_code}")
    except:
        pass
    
    # Let's try the department heads endpoint without auth to see the specific error
    try:
        response = requests.get("http://127.0.0.1:8000/admin/department-heads/", timeout=10)
        print(f"🔍 Department heads endpoint (no auth): {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("✅ Expected 401 - Authentication required")
            return True
        elif response.status_code == 500:
            print("❌ 500 Error - This is what we're trying to fix")
            return False
        else:
            print(f"🤔 Unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("🔧 Quick Department Heads API Test")
    print("=" * 40)
    
    success = test_department_heads_endpoint()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Basic endpoint structure is working (needs auth)")
    else:
        print("❌ Endpoint still has issues")

if __name__ == "__main__":
    main()