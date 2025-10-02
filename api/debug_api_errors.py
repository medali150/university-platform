"""
Debug script to identify the root cause of 500 errors in the API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_detailed_endpoints():
    """Test endpoints with detailed error reporting"""
    
    print("🔍 Detailed API Error Analysis")
    print("=" * 50)
    
    # First, get admin token
    login_data = {
        "login": "mohamedali.gh15@gmail.com",
        "password": "daligh15"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Cannot get admin token: {response.text}")
        return
    
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test each endpoint with detailed error reporting
    endpoints_to_test = [
        ("GET", "/auth/users", "Get all users"),
        ("GET", "/departments/", "Get departments"),
        ("GET", "/specialties/", "Get specialties"), 
        ("GET", "/admin/students/", "Get students"),
        ("GET", "/admin/teachers/", "Get teachers"),
        ("GET", "/admin/department-heads/", "Get department heads"),
        ("GET", "/admin/levels/", "Get levels"),
        ("GET", "/admin/subjects/", "Get subjects"),
        ("GET", "/admin/dashboard/stats", "Get dashboard stats")
    ]
    
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            print(f"\n📍 {description}")
            print(f"   Endpoint: {method} {endpoint}")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'total' in data:
                        print(f"   ✅ Success: {data.get('total')} items")
                    elif isinstance(data, list):
                        print(f"   ✅ Success: {len(data)} items")
                    else:
                        print(f"   ✅ Success: {type(data).__name__}")
                except:
                    print(f"   ✅ Success: Non-JSON response")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
    
    # Test a simple direct database query to check if it's a database issue
    print(f"\n🔍 Direct Database Test")
    try:
        response = requests.get(f"{BASE_URL}/health", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   Database Status: {data.get('database')}")
            print(f"   Users Count: {data.get('users_count')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   💥 Health check exception: {str(e)}")


if __name__ == "__main__":
    test_detailed_endpoints()