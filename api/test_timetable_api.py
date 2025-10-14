"""
Test the timetable management API endpoints
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Test login and get access token"""
    login_data = {
        "email": "wahid@gmail.com",
        "password": "dalighgh15"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Login failed: {response.text}")
        return None

def test_timetable_endpoints(token):
    """Test all timetable endpoints"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/timetable/student",
        "/timetable/teacher", 
        "/timetable/weekly-overview"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n=== Testing {endpoint} ===")
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"Found {len(data)} entries")
                    if data:
                        print("Sample entry:")
                        print(json.dumps(data[0], indent=2))
                elif isinstance(data, dict):
                    print("Response structure:")
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"  {key}: {len(value)} items")
                        else:
                            print(f"  {key}: {value}")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    print("Testing timetable management API...")
    
    # Get access token
    token = test_login()
    if not token:
        print("Failed to get access token")
        exit(1)
    
    print(f"Got access token: {token[:20]}...")
    
    # Test all timetable endpoints
    test_timetable_endpoints(token)