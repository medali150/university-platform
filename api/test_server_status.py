import requests

# Simple test to see what endpoints work
base_url = "http://localhost:8000"

# Check if server is running
try:
    response = requests.get(f"{base_url}/docs")
    print(f"Server status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Server is running")
        
        # Check what users exist by looking at login options
        print("\nTesting common login combinations...")
        
        login_attempts = [
            {"email": "student@university.com", "password": "student123"},
            {"email": "teststudent@university.com", "password": "student123"},
            {"email": "ahmed.bensalem@university.edu", "password": "password123"},
            {"email": "admin@example.com", "password": "admin123"}
        ]
        
        for i, login_data in enumerate(login_attempts):
            print(f"\nAttempt {i+1}: {login_data['email']}")
            try:
                login_response = requests.post(f"{base_url}/auth/login", json=login_data)
                print(f"  Status: {login_response.status_code}")
                if login_response.status_code == 200:
                    print("  ✅ Login successful!")
                    result = login_response.json()
                    print(f"  User info: {result.get('user', {})}")
                    break
                else:
                    print(f"  ❌ Failed: {login_response.text[:100]}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    else:
        print("❌ Server not running or not accessible")
        
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")