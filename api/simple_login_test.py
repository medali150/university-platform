#!/usr/bin/env python3
"""
SIMPLE LOGIN TEST
================
Test login without complex database dependencies
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple_login():
    """Test simple login scenarios"""
    
    print("🔍 SIMPLE LOGIN TEST")
    print("=" * 30)
    
    # Test admin login with different payload formats
    test_payloads = [
        {
            "name": "Standard email format",
            "payload": {"email": "admin@university.com", "password": "admin123"}
        },
        {
            "name": "Login field format", 
            "payload": {"login": "admin@university.com", "password": "admin123"}
        },
        {
            "name": "Both fields format",
            "payload": {"email": "admin@university.com", "login": "admin@university.com", "password": "admin123"}
        }
    ]
    
    for i, test in enumerate(test_payloads, 1):
        print(f"\n{i}️⃣ Testing: {test['name']}")
        print(f"   Payload: {json.dumps(test['payload'])}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login", 
                json=test['payload'],
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Login successful!")
                data = response.json()
                if 'user' in data:
                    user = data['user']
                    print(f"   User: {user.get('prenom', 'N/A')} {user.get('nom', 'N/A')} ({user.get('role', 'N/A')})")
                    print(f"   Token: {data.get('access_token', 'N/A')[:30]}...")
                return True
                
            elif response.status_code in [400, 401, 422]:
                print(f"   ❌ Client error: {response.text}")
                
            elif response.status_code >= 500:
                print(f"   ❌ Server error: {response.text}")
                # Try to get more details
                try:
                    error_data = response.json()
                    print(f"   Error details: {error_data}")
                except:
                    pass
                    
            else:
                print(f"   ⚠️  Unexpected status: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed - is the server running?")
            return False
        except Exception as e:
            print(f"   ❌ Request error: {str(e)}")
    
    return False

def test_simple_endpoints():
    """Test other simple endpoints"""
    
    print(f"\n📊 Testing Other Endpoints...")
    
    endpoints = [
        {"url": "/health", "name": "Health Check"},
        {"url": "/departments", "name": "Departments"},
        {"url": "/auth/users", "name": "Users List"}
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint['url']}", timeout=5)
            print(f"   {endpoint['name']}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'status' in data:
                        print(f"      Status: {data['status']}")
                    elif isinstance(data, list):
                        print(f"      Items: {len(data)}")
                except:
                    pass
                    
        except Exception as e:
            print(f"   {endpoint['name']}: Error - {str(e)}")

if __name__ == "__main__":
    success = test_simple_login()
    test_simple_endpoints()
    
    if success:
        print(f"\n✅ Login is working!")
    else:
        print(f"\n❌ Login needs fixing")