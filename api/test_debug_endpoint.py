#!/usr/bin/env python3

import requests
import json

# Test the new debug endpoint
base_url = "http://localhost:8000"

def test_debug_endpoint():
    """Test the new debug endpoint to understand student data structure"""
    
    print("=== Testing Student Debug Endpoint ===")
    
    # First login as student
    login_data = {
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
        
        login_result = login_response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test debug endpoint
        debug_response = requests.get(f"{base_url}/student/debug", headers=headers)
        print(f"Debug Status: {debug_response.status_code}")
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print("Debug Data:")
            print(json.dumps(debug_data, indent=2, default=str))
        else:
            print(f"Debug failed: {debug_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_debug_endpoint()