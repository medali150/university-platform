#!/usr/bin/env python3

import requests
import json

def test_schedule_diagnosis():
    """Test the diagnostic schedule endpoint"""
    
    print("=== Testing Schedule Diagnosis ===")
    
    # Login as student
    login_data = {
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    }
    
    login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test diagnostic endpoint
    try:
        diag_response = requests.get("http://localhost:8000/student/schedule/test", headers=headers)
        print(f"Diagnosis Status: {diag_response.status_code}")
        
        if diag_response.status_code == 200:
            data = diag_response.json()
            print("✅ Diagnosis successful!")
            print(json.dumps(data, indent=2, default=str))
        else:
            print(f"❌ Diagnosis failed: {diag_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_schedule_diagnosis()