#!/usr/bin/env python3
"""
Step-by-step check of API fixes
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def check_endpoint(method, endpoint, headers=None, data=None, description=""):
    """Test a single endpoint"""
    try:
        print(f"\n🔍 Testing {method} {endpoint}")
        print(f"   📝 {description}")
        
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        elif method.upper() == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
            
        print(f"   🔢 Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success")
            try:
                result = response.json()
                if isinstance(result, dict):
                    print(f"   📊 Response keys: {list(result.keys())}")
                elif isinstance(result, list):
                    print(f"   📊 Response: List with {len(result)} items")
                else:
                    print(f"   📊 Response type: {type(result)}")
            except:
                print(f"   📊 Non-JSON response")
            return True
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   📝 Error detail: {error_detail}")
            except:
                print(f"   📝 Error text: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   💥 Connection Error - Server not running")
        return False
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return False

def main():
    print("🚀 Step-by-step API Testing")
    print("=" * 50)
    
    # Wait for server to be ready
    print("\n⏳ Checking if server is running...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            print(f"   Waiting... ({i+1}/10)")
            time.sleep(2)
    else:
        print("❌ Server is not responding. Please start the server first.")
        return
    
    # Track results
    total_tests = 0
    passed_tests = 0
    
    # Step 1: Basic endpoints
    print("\n" + "="*50)
    print("STEP 1: Testing Basic Endpoints")
    print("="*50)
    
    tests = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
    ]
    
    for method, endpoint, description in tests:
        total_tests += 1
        if check_endpoint(method, endpoint, description=description):
            passed_tests += 1
    
    # Step 2: Authentication
    print("\n" + "="*50)
    print("STEP 2: Testing Authentication")
    print("="*50)
    
    # Try admin login
    login_data = {
        "login": "admin.user",
        "password": "admin123"
    }
    
    total_tests += 1
    if check_endpoint("POST", "/auth/login", data=login_data, description="Admin login"):
        passed_tests += 1
        
        # Get token from login response
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test authenticated endpoints
            auth_tests = [
                ("GET", "/auth/me", "Get current user"),
                ("GET", "/auth/users", "Get all users"),
            ]
            
            for method, endpoint, description in auth_tests:
                total_tests += 1
                if check_endpoint(method, endpoint, headers=headers, description=description):
                    passed_tests += 1
        else:
            print("   ⚠️  Cannot get token for further auth tests")
    
    # Step 3: Core entities (without auth for now)
    print("\n" + "="*50)
    print("STEP 3: Testing Core Entities")
    print("="*50)
    
    core_tests = [
        ("GET", "/departments", "Get departments"),
        ("GET", "/specialties", "Get specialties"),
    ]
    
    for method, endpoint, description in core_tests:
        total_tests += 1
        if check_endpoint(method, endpoint, description=description):
            passed_tests += 1
    
    # Step 4: Admin endpoints (if we have token)
    if 'token' in locals():
        print("\n" + "="*50)
        print("STEP 4: Testing Admin Endpoints")
        print("="*50)
        
        admin_tests = [
            ("GET", "/admin/students", "Get students"),
            ("GET", "/admin/teachers", "Get teachers"),
            ("GET", "/admin/department-heads", "Get department heads"),
            ("GET", "/admin/levels", "Get levels"),
            ("GET", "/admin/subjects", "Get subjects"),
            ("GET", "/admin/subjects/helpers/levels", "Get levels helper"),
            ("GET", "/admin/subjects/helpers/teachers", "Get teachers helper"),
            ("GET", "/admin/dashboard/stats", "Dashboard stats"),
        ]
        
        for method, endpoint, description in admin_tests:
            total_tests += 1
            if check_endpoint(method, endpoint, headers=headers, description=description):
                passed_tests += 1
    
    # Final summary
    print("\n" + "="*60)
    print("🎯 FINAL RESULTS")
    print("="*60)
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📊 Total: {total_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! APIs are working correctly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Check the errors above.")

if __name__ == "__main__":
    main()