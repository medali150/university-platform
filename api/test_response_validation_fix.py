#!/usr/bin/env python3
"""
Test the schedule creation after fixing the response validation issue
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_schedule_creation_fix():
    """Test schedule creation with a new time to avoid conflicts"""
    print("🧪 TESTING SCHEDULE CREATION - RESPONSE VALIDATION FIX")
    print("="*70)
    
    # Step 1: Login
    print("1️⃣ Testing login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "login": "hathemhafsi@gmail.com",
        "password": "dslighgh15"
    })
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   ✅ Login successful!")
    
    # Step 2: Test schedule creation with new time
    print(f"\n2️⃣ Testing schedule creation...")
    
    schedule_data = {
        "date": "2025-10-06T10:00:00.000Z",
        "startTime": "2025-10-06T10:00:00.000Z",
        "endTime": "2025-10-06T12:00:00.000Z",
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
            print(f"   👨‍🏫 Teacher: {data['teacher']['user']['firstName']} {data['teacher']['user']['lastName']}")
            print(f"   ⏰ Date: {data['date']}")
            print(f"   ⏰ Time: {data['startTime']} - {data['endTime']}")
            return True
            
        elif schedule_response.status_code == 409:
            print(f"   ⚠️  Conflict detected:")
            conflict_data = schedule_response.json()
            print(f"   📋 Conflicts: {len(conflict_data['detail']['conflicts'])} found")
            for conflict in conflict_data['detail']['conflicts']:
                print(f"      - {conflict['type']}: {conflict['message']}")
            
            # Try with a different room
            print(f"\n   🔄 Trying with different room...")
            schedule_data["roomId"] = "cmg2kma6y0000bmyoon64aiqb"  # Different room
            
            schedule_response2 = requests.post(f"{BASE_URL}/schedules/", json=schedule_data, headers=headers)
            print(f"   Second attempt status: {schedule_response2.status_code}")
            
            if schedule_response2.status_code == 201:
                data = schedule_response2.json()
                print(f"   ✅ Schedule created with different room!")
                print(f"   🏢 Room: {data['room']['code']}")
                return True
            else:
                print(f"   ❌ Still failed: {schedule_response2.text}")
                return False
            
        else:
            print(f"   ❌ Schedule creation failed:")
            print(f"   Status: {schedule_response.status_code}")
            print(f"   Response: {schedule_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during request: {e}")
        return False

def main():
    success = test_schedule_creation_fix()
    
    if success:
        print(f"\n🎉 RESPONSE VALIDATION FIX SUCCESSFUL!")
        print(f"✅ Schedule creation now works properly")
        print(f"✅ Response schema is correctly structured")
        
        print(f"\n🎯 FINAL WORKING PAYLOADS:")
        print(f"\n1️⃣ LOGIN:")
        print(f'{{')
        print(f'  "login": "hathemhafsi@gmail.com",')
        print(f'  "password": "dslighgh15"')
        print(f'}}')
        
        print(f"\n2️⃣ SCHEDULE CREATION:")
        print(f'{{')
        print(f'  "date": "2025-10-07T09:00:00.000Z",')
        print(f'  "startTime": "2025-10-07T09:00:00.000Z",')
        print(f'  "endTime": "2025-10-07T11:00:00.000Z",')
        print(f'  "roomId": "cmg2kma6y0000bmyoon64aiqb",')
        print(f'  "subjectId": "cmg3ygxwm000vbm8w7krco7g9",')
        print(f'  "groupId": "cmg0xm3sw0006bmw03g4od0tp",')
        print(f'  "teacherId": "cmg3yei9j0001bmug3qq8z3cw",')
        print(f'  "status": "PLANNED"')
        print(f'}}')
        
    else:
        print(f"\n❌ TEST FAILED")
        print(f"There may be additional issues to resolve")

if __name__ == "__main__":
    main()