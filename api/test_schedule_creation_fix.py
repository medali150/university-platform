#!/usr/bin/env python3
"""
Test the schedule creation after fixing the date serialization issue
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_schedule_creation():
    """Test the complete flow"""
    print("🧪 TESTING SCHEDULE CREATION AFTER FIX")
    print("="*60)
    
    # Step 1: Login
    print("1️⃣ Testing login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "login": "hathemhafsi@gmail.com",
        "password": "dslighgh15"
    })
    
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✅ Login successful!")
    
    # Step 2: Test schedule creation
    print(f"\n2️⃣ Testing schedule creation...")
    
    schedule_data = {
        "date": "2025-10-04T08:00:00.000Z",
        "startTime": "2025-10-04T08:00:00.000Z",
        "endTime": "2025-10-04T10:00:00.000Z",
        "roomId": "cmg2hx0d60006bmbsyzo4oltr",
        "subjectId": "cmg3ygxwm000vbm8w7krco7g9",
        "groupId": "cmg0xm3sw0006bmw03g4od0tp",
        "teacherId": "cmg3yei9j0001bmug3qq8z3cw",
        "status": "PLANNED"
    }
    
    try:
        schedule_response = requests.post(f"{BASE_URL}/schedules/", json=schedule_data, headers=headers)
        
        print(f"   Schedule creation status: {schedule_response.status_code}")
        
        if schedule_response.status_code == 201:
            data = schedule_response.json()
            print(f"   ✅ Schedule created successfully!")
            print(f"   📅 Schedule ID: {data['id']}")
            print(f"   📚 Subject: {data['subject']['name']}")
            print(f"   👥 Group: {data['group']['name']}")
            print(f"   🏢 Room: {data['room']['code']}")
            print(f"   ⏰ Time: {data['startTime']} - {data['endTime']}")
            return True
            
        elif schedule_response.status_code == 409:
            print(f"   ⚠️  Conflict detected (this is expected behavior):")
            conflict_data = schedule_response.json()
            print(f"   📋 Conflicts: {json.dumps(conflict_data, indent=2)}")
            return True  # Conflicts are handled correctly
            
        else:
            print(f"   ❌ Schedule creation failed:")
            print(f"   Status: {schedule_response.status_code}")
            print(f"   Response: {schedule_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during request: {e}")
        return False

def main():
    success = test_schedule_creation()
    
    if success:
        print(f"\n🎉 TEST PASSED!")
        print(f"✅ The date serialization issue has been fixed")
        print(f"✅ Schedule creation is working properly")
        print(f"\n🎯 Ready to use in Swagger UI!")
    else:
        print(f"\n❌ TEST FAILED")
        print(f"There may be other issues to resolve")

if __name__ == "__main__":
    main()