#!/usr/bin/env python3
"""
Test complete CRUD operations for timetable schedules
"""
import asyncio
import requests
import json

async def test_schedule_crud():
    """Test Create, Read, Update, Delete operations"""
    
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
                    # 1. CREATE: Create test schedule
                    print(f"\n🔨 1. CREATE - Creating new schedule...")
                    schedule_data = {
                        "date": "2025-10-15",
                        "start_time": "09:00",
                        "end_time": "10:30",
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
                        print(f"   🆔 Schedule ID: {schedule_id}")
                        
                        # 2. READ: Get the created schedule
                        print(f"\n📖 2. READ - Getting schedules...")
                        read_response = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
                        
                        if read_response.status_code == 200:
                            schedules = read_response.json()
                            print(f"✅ Retrieved {len(schedules)} schedules")
                            
                            # Find our created schedule
                            our_schedule = next((s for s in schedules if s["id"] == schedule_id), None)
                            if our_schedule:
                                print(f"   📅 Date: {our_schedule['date']}")
                                print(f"   ⏰ Start: {our_schedule['heure_debut']}")
                                print(f"   ⏰ End: {our_schedule['heure_fin']}")
                                print(f"   👥 Group: {our_schedule['groupe']['nom']}")
                                print(f"   📚 Subject: {our_schedule['matiere']['nom']}")
                        
                        # 3. UPDATE: Update the schedule
                        print(f"\n✏️ 3. UPDATE - Updating schedule...")
                        update_data = {
                            "start_time": "10:00",
                            "end_time": "11:30"
                        }
                        
                        update_response = requests.put(
                            f"{base_url}/department-head/timetable/schedules/{schedule_id}",
                            headers=headers,
                            json=update_data
                        )
                        
                        if update_response.status_code == 200:
                            print(f"✅ Schedule updated successfully!")
                            
                            # Verify the update
                            read_again_response = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
                            if read_again_response.status_code == 200:
                                updated_schedules = read_again_response.json()
                                updated_schedule = next((s for s in updated_schedules if s["id"] == schedule_id), None)
                                if updated_schedule:
                                    print(f"   ⏰ New Start: {updated_schedule['heure_debut']}")
                                    print(f"   ⏰ New End: {updated_schedule['heure_fin']}")
                        else:
                            print(f"❌ Update failed - Status: {update_response.status_code}")
                            print(f"   Response: {update_response.text}")
                        
                        # 4. DELETE: Delete the schedule
                        print(f"\n🗑️ 4. DELETE - Deleting schedule...")
                        delete_response = requests.delete(
                            f"{base_url}/department-head/timetable/schedules/{schedule_id}",
                            headers=headers
                        )
                        
                        if delete_response.status_code == 200:
                            print(f"✅ Schedule deleted successfully!")
                            
                            # Verify deletion
                            final_read_response = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
                            if final_read_response.status_code == 200:
                                final_schedules = final_read_response.json()
                                deleted_schedule = next((s for s in final_schedules if s["id"] == schedule_id), None)
                                if not deleted_schedule:
                                    print(f"✅ Verified: Schedule no longer exists")
                                else:
                                    print(f"⚠️ Warning: Schedule still exists after deletion")
                        else:
                            print(f"❌ Delete failed - Status: {delete_response.status_code}")
                            print(f"   Response: {delete_response.text}")
                            
                    else:
                        print(f"❌ Schedule creation failed!")
                        print(f"   Status: {create_response.status_code}")
                        print(f"   Response: {create_response.text}")
                else:
                    print("❌ Not enough data available to test CRUD operations")
            else:
                print("❌ Failed to fetch required data")
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_schedule_crud())