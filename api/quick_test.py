#!/usr/bin/env python3
"""
Quick test of fixed endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_endpoint(endpoint, description=""):
    """Quick test of an endpoint"""
    try:
        print(f"Testing {endpoint}: ", end="", flush=True)
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"✅ OK")
            return True
        else:
            print(f"❌ {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', 'Unknown error')}")
            except:
                pass
            return False
    except requests.exceptions.ConnectionError:
        print("💥 Connection Error")
        return False
    except requests.exceptions.Timeout:
        print("⏰ Timeout")
        return False
    except Exception as e:
        print(f"💥 {e}")
        return False

def test_with_auth(endpoint, token, description=""):
    """Test endpoint with authentication"""
    try:
        print(f"Testing {endpoint} (auth): ", end="", flush=True)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ OK")
            return True
        else:
            print(f"❌ {response.status_code}")
            return False
    except Exception as e:
        print(f"💥 Error")
        return False

def main():
    print("🚀 Quick API Fix Test")
    print("=" * 40)
    
    # Check if server is running
    if not test_endpoint("/health", "Health check"):
        print("❌ Server not running. Please start the server first.")
        return
    
    # Test basic endpoints
    basic_tests = [
        "/",
        "/departments",
        "/specialties",
    ]
    
    print("\\n📋 Basic Endpoints:")
    passed = 0
    for endpoint in basic_tests:
        if test_endpoint(endpoint):
            passed += 1
    
    print(f"\\nBasic endpoints: {passed}/{len(basic_tests)} passed")
    
    # Try to get auth token
    print("\\n🔐 Authentication Test:")
    login_data = {
        "login": "admin.user",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Login successful")
            
            # Test authenticated endpoints
            print("\\n🔒 Authenticated Endpoints:")
            auth_tests = [
                "/auth/me",
                "/auth/users", 
                "/admin/students",
                "/admin/teachers",
                "/admin/department-heads",
                "/admin/levels",
                "/admin/subjects",
                "/admin/subjects/helpers/levels",
                "/admin/subjects/helpers/teachers",
                "/admin/dashboard/stats",
            ]
            
            auth_passed = 0
            for endpoint in auth_tests:
                if test_with_auth(endpoint, token):
                    auth_passed += 1
            
            print(f"\\nAuth endpoints: {auth_passed}/{len(auth_tests)} passed")
            total_passed = passed + (1 if token else 0) + auth_passed
            total_tests = len(basic_tests) + 1 + len(auth_tests)
            
        else:
            print("❌ Login failed")
            total_passed = passed
            total_tests = len(basic_tests) + 1
    
    except Exception as e:
        print(f"❌ Login error: {e}")
        total_passed = passed
        total_tests = len(basic_tests) + 1
    
    print("\\n" + "=" * 40)
    print(f"🎯 Overall: {total_passed}/{total_tests} tests passed")
    print(f"📊 Success rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total_tests - total_passed} issues remain")

if __name__ == "__main__":
    main()