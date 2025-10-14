#!/usr/bin/env python3
"""
Test to check timezone handling and time storage
"""
import requests
import json
from datetime import datetime

def test_time_storage():
    """Test how times are stored and retrieved"""
    
    base_url = "http://localhost:8000"
    
    # Login with test credentials
    login_data = {
        "email": "test.depthead@university.com",
        "password": "test123"
    }
    
    print("🔐 Logging in...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get data needed for schedule creation
            print("\n📋 Getting required data...")
            
            groups_resp = requests.get(f"{base_url}/department-head/timetable/groups", headers=headers)
            subjects_resp = requests.get(f"{base_url}/department-head/timetable/subjects", headers=headers)
            teachers_resp = requests.get(f"{base_url}/department-head/timetable/teachers", headers=headers)
            rooms_resp = requests.get(f"{base_url}/department-head/timetable/rooms", headers=headers)
            
            if all(r.status_code == 200 for r in [groups_resp, subjects_resp, teachers_resp, rooms_resp]):
                groups = groups_resp.json()
                subjects = subjects_resp.json()
                teachers = teachers_resp.json()
                rooms = rooms_resp.json()
                
                if all([groups, subjects, teachers, rooms]):
                    # Create a test schedule with specific time
                    test_time = "08:30"
                    print(f"\n🕐 Creating schedule with start time: {test_time}")
                    
                    schedule_data = {
                        "date": "2025-12-15",  # Use future date to avoid conflicts
                        "start_time": test_time,
                        "end_time": "10:00",
                        "subject_id": subjects[0]["id"],
                        "group_id": groups[0]["id"],
                        "teacher_id": teachers[0]["id"],
                        "room_id": rooms[0]["id"]
                    }
                    
                    create_response = requests.post(
                        f"{base_url}/department-head/timetable/schedules",
                        headers=headers,
                        json=schedule_data
                    )
                    
                    if create_response.status_code == 200:
                        created_schedule = create_response.json()
                        schedule_id = created_schedule["id"]
                        
                        print(f"✅ Schedule created successfully!")
                        print(f"   📝 Input start time: {test_time}")
                        print(f"   💾 Stored start time: {created_schedule['heure_debut']}")
                        
                        # Now retrieve the schedule to see how it's returned
                        print(f"\n📖 Retrieving schedule...")
                        
                        schedules_resp = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
                        if schedules_resp.status_code == 200:
                            schedules = schedules_resp.json()
                            our_schedule = next((s for s in schedules if s["id"] == schedule_id), None)
                            
                            if our_schedule:
                                print(f"✅ Schedule retrieved!")
                                print(f"   💾 Retrieved start time: {our_schedule['heure_debut']}")
                                print(f"   💾 Retrieved end time: {our_schedule['heure_fin']}")
                                
                                # Parse the returned datetime to check the time
                                stored_datetime = datetime.fromisoformat(our_schedule['heure_debut'].replace('Z', '+00:00'))
                                print(f"   ⏰ Parsed time (UTC): {stored_datetime.strftime('%H:%M')}")
                                print(f"   ⏰ Expected time: {test_time}")
                                
                                if stored_datetime.strftime('%H:%M') != test_time:
                                    print(f"   ⚠️ TIME MISMATCH DETECTED!")
                                    print(f"      Expected: {test_time}")
                                    print(f"      Got: {stored_datetime.strftime('%H:%M')}")
                                else:
                                    print(f"   ✅ Time matches correctly!")
                        
                        # Clean up - delete the test schedule
                        print(f"\n🧹 Cleaning up test schedule...")
                        delete_response = requests.delete(f"{base_url}/department-head/timetable/schedules/{schedule_id}", headers=headers)
                        if delete_response.status_code == 200:
                            print("✅ Test schedule deleted")
                        
                    else:
                        print(f"❌ Schedule creation failed!")
                        print(f"   Status: {create_response.status_code}")
                        print(f"   Response: {create_response.text}")
                else:
                    print("❌ Not enough data available")
            else:
                print("❌ Failed to fetch required data")
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_time_storage()