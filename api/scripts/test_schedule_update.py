#!/usr/bin/env python3
"""
Test the schedule update functionality
"""
import requests
import json

def test_schedule_update():
    """Test updating a schedule"""
    
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
            
            # Get existing schedules
            print("\n📋 Getting existing schedules...")
            schedules_resp = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
            
            if schedules_resp.status_code == 200:
                schedules = schedules_resp.json()
                print(f"✅ Retrieved {len(schedules)} schedules")
                
                if schedules:
                    # Take the first schedule to update
                    schedule = schedules[0]
                    schedule_id = schedule["id"]
                    
                    print(f"\n🔧 Testing update for schedule {schedule_id}")
                    print(f"   Current start time: {schedule.get('heure_debut')}")
                    print(f"   Current end time: {schedule.get('heure_fin')}")
                    
                    # Update with new times
                    update_data = {
                        "start_time": "14:00",
                        "end_time": "15:30"
                    }
                    
                    print(f"\n📝 Updating schedule with: {update_data}")
                    
                    update_response = requests.put(
                        f"{base_url}/department-head/timetable/schedules/{schedule_id}",
                        headers=headers,
                        json=update_data
                    )
                    
                    if update_response.status_code == 200:
                        updated_schedule = update_response.json()
                        print("✅ Schedule updated successfully!")
                        print(f"   New start time: {updated_schedule.get('heure_debut')}")
                        print(f"   New end time: {updated_schedule.get('heure_fin')}")
                        
                        # Verify by getting schedules again
                        verify_response = requests.get(f"{base_url}/department-head/timetable/schedules", headers=headers)
                        if verify_response.status_code == 200:
                            updated_schedules = verify_response.json()
                            updated_schedule_verify = next((s for s in updated_schedules if s["id"] == schedule_id), None)
                            if updated_schedule_verify:
                                print(f"✅ Verification - Updated schedule found")
                                print(f"   Verified start time: {updated_schedule_verify.get('heure_debut')}")
                                print(f"   Verified end time: {updated_schedule_verify.get('heure_fin')}")
                    else:
                        print(f"❌ Update failed!")
                        print(f"   Status: {update_response.status_code}")
                        print(f"   Response: {update_response.text}")
                        
                else:
                    print("❌ No schedules found to update")
            else:
                print(f"❌ Failed to get schedules - Status: {schedules_resp.status_code}")
                print(f"   Response: {schedules_resp.text}")
        else:
            print(f"❌ Login failed - Status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_schedule_update()