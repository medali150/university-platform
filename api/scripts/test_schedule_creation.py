#!/usr/bin/env python3
"""
Test schedule creation API endpoint
"""
import asyncio
import requests
import json

async def test_schedule_creation():
    """Test creating a schedule via API"""
    
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
            
            # Get available data first
            print("\n📋 Getting available data...")
            
            groups_resp = requests.get(f"{base_url}/department-head/timetable/groups", headers=headers)
            subjects_resp = requests.get(f"{base_url}/department-head/timetable/subjects", headers=headers)
            teachers_resp = requests.get(f"{base_url}/department-head/timetable/teachers", headers=headers)
            rooms_resp = requests.get(f"{base_url}/department-head/timetable/rooms", headers=headers)
            
            if all(r.status_code == 200 for r in [groups_resp, subjects_resp, teachers_resp, rooms_resp]):
                groups = groups_resp.json()
                subjects = subjects_resp.json()
                teachers = teachers_resp.json()
                rooms = rooms_resp.json()
                
                print(f"📊 Available data:")
                print(f"   👥 Groups: {len(groups)}")
                print(f"   📚 Subjects: {len(subjects)}")
                print(f"   👨‍🏫 Teachers: {len(teachers)}")
                print(f"   🏛️ Rooms: {len(rooms)}")
                
                if groups and subjects and teachers and rooms:
                    # Create test schedule
                    schedule_data = {
                        "date": "2025-10-10",
                        "start_time": "08:30",
                        "end_time": "10:00",
                        "subject_id": subjects[0]["id"],
                        "group_id": groups[0]["id"],
                        "teacher_id": teachers[0]["id"],
                        "room_id": rooms[0]["id"]
                    }
                    
                    print(f"\n🔨 Creating schedule with data:")
                    print(f"   📅 Date: {schedule_data['date']}")
                    print(f"   ⏰ Time: {schedule_data['start_time']} - {schedule_data['end_time']}")
                    print(f"   👥 Group: {groups[0]['nom']}")
                    print(f"   📚 Subject: {subjects[0]['nom']}")
                    print(f"   👨‍🏫 Teacher: {teachers[0]['nom']} {teachers[0]['prenom']}")
                    print(f"   🏛️ Room: {rooms[0]['code']}")
                    
                    create_response = requests.post(
                        f"{base_url}/department-head/timetable/schedules",
                        headers=headers,
                        json=schedule_data
                    )
                    
                    if create_response.status_code == 200:
                        result = create_response.json()
                        print(f"\n✅ Schedule created successfully!")
                        print(f"   🆔 Schedule ID: {result.get('id', 'N/A')}")
                    else:
                        print(f"\n❌ Schedule creation failed!")
                        print(f"   Status: {create_response.status_code}")
                        print(f"   Response: {create_response.text}")
                else:
                    print("❌ Not enough data available to create schedule")
            else:
                print("❌ Failed to fetch required data")
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_schedule_creation())