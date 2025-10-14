#!/usr/bin/env python3

import requests
import json

def test_schedule_endpoint():
    """Test schedule endpoint specifically to debug the 500 error"""
    
    print("=== Testing Student Schedule Endpoint ===")
    
    # Login as student
    login_data = {
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    }
    
    try:
        login_response = requests.post("http://localhost:8000/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
        
        login_result = login_response.json()
        token = login_result["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test schedule endpoint with detailed error catching
        print("\n🔍 Testing /student/schedule endpoint...")
        try:
            schedule_response = requests.get(
                "http://localhost:8000/student/schedule",
                headers=headers,
                timeout=30
            )
            
            print(f"Schedule Status: {schedule_response.status_code}")
            
            if schedule_response.status_code == 200:
                data = schedule_response.json()
                print("✅ Schedule endpoint works!")
                print(f"Found {len(data.get('schedules', []))} schedules")
                
                # Show first schedule if available
                if data.get('schedules'):
                    first_schedule = data['schedules'][0]
                    print("First schedule sample:")
                    print(json.dumps(first_schedule, indent=2, default=str))
            else:
                print(f"❌ Schedule failed with status {schedule_response.status_code}")
                print("Response headers:", dict(schedule_response.headers))
                print("Response body:", schedule_response.text)
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out - likely a server error")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_schedule_endpoint()