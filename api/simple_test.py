#!/usr/bin/env python3
"""
Simple API endpoint validation
Run this while the server is running on port 8000
"""
import requests
import json

def test_single_endpoint(endpoint, description):
    """Test a single endpoint"""
    try:
        response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=3)
        print(f"{endpoint:30} {response.status_code:3d} - {description}")
        return response.status_code == 200
    except Exception as e:
        print(f"{endpoint:30} ERR - {description} ({str(e)[:50]})")
        return False

def main():
    print("🧪 Simple API Validation Test")
    print("=" * 60)
    print("Make sure the server is running on port 8000")
    print("=" * 60)
    
    # Test endpoints that were failing before
    tests = [
        ("/health", "Health check"),
        ("/", "Root endpoint"), 
        ("/departments", "Departments list (was 500 error)"),
        ("/specialties", "Specialties list (was 500 error)"),
    ]
    
    results = []
    for endpoint, description in tests:
        results.append(test_single_endpoint(endpoint, description))
    
    # Try authentication
    print("\\nTesting authentication...")
    try:
        login_data = {"login": "admin.user", "password": "admin123"}
        response = requests.post("http://127.0.0.1:8000/auth/login", json=login_data, timeout=3)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("Login successful - got token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test authenticated endpoints that were failing
            auth_tests = [
                ("/auth/users", "Users list (was 500 error)"),
                ("/admin/students", "Students list (was 500 error)"),
                ("/admin/levels", "Levels list (was 500 error)"),
                ("/admin/subjects", "Subjects list (was 500 error)"),
            ]
            
            for endpoint, description in auth_tests:
                try:
                    response = requests.get(f"http://127.0.0.1:8000{endpoint}", headers=headers, timeout=3)
                    print(f"{endpoint:30} {response.status_code:3d} - {description}")
                    results.append(response.status_code == 200)
                except Exception as e:
                    print(f"{endpoint:30} ERR - {description}")
                    results.append(False)
        else:
            print(f"Login failed: {response.status_code}")
            
    except Exception as e:
        print(f"Authentication error: {e}")
    
    # Summary
    passed = sum(results)
    total = len(results) 
    print("\\n" + "=" * 60)
    print(f"Results: {passed}/{total} endpoints working ({(passed/total)*100:.0f}% success rate)")
    
    if passed == total:
        print("🎉 ALL FIXED! No more 500 errors!")
    else:
        print(f"⚠️  {total-passed} issues remain")

if __name__ == "__main__":
    main()