#!/usr/bin/env python3

import requests
import json

def create_schedules_for_student_group():
    """Create sample schedules for the student's group using the new admin endpoint"""
    
    print("=== CREATING SCHEDULES FOR STUDENT GROUP ===")
    
    base_url = "http://localhost:8000"
    
    # Login as student
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
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create sample schedules using the new admin endpoint
        print("\n🔧 Creating sample schedules...")
        create_response = requests.post(
            f"{base_url}/student/admin/create-sample-schedule",
            headers=headers
        )
        
        print(f"Create Status: {create_response.status_code}")
        
        if create_response.status_code == 200:
            result = create_response.json()
            print("✅ Schedule creation successful!")
            print(json.dumps(result, indent=2, default=str))
            
            # Verify schedules were created
            print("\n🔍 Verifying schedule creation...")
            diag_response = requests.get(f"{base_url}/student/schedule/test", headers=headers)
            
            if diag_response.status_code == 200:
                diag_data = diag_response.json()
                group_schedules = diag_data["tests"]["step_2_group_schedules_count"]
                print(f"✅ Group now has {group_schedules} schedules")
                
                # Test the main schedule endpoint
                print("\n📅 Testing main schedule endpoint...")
                schedule_response = requests.get(f"{base_url}/student/schedule", headers=headers)
                
                if schedule_response.status_code == 200:
                    schedule_data = schedule_response.json()
                    schedules_count = len(schedule_data.get("schedules", []))
                    print(f"✅ Schedule endpoint returns {schedules_count} schedules")
                    
                    if schedules_count > 0:
                        print("🎉 SUCCESS! Student can now see their schedule!")
                        first_schedule = schedule_data["schedules"][0]
                        print("Sample schedule entry:")
                        print(f"   Date: {first_schedule.get('date')}")
                        print(f"   Time: {first_schedule.get('heure_debut')} - {first_schedule.get('heure_fin')}")
                        print(f"   Subject: {first_schedule.get('matiere', {}).get('nom') if first_schedule.get('matiere') else 'N/A'}")
                    else:
                        print("⚠️ Schedules created but not visible to student yet")
                else:
                    print(f"❌ Schedule endpoint failed: {schedule_response.status_code}")
            else:
                print(f"❌ Diagnostic failed: {diag_response.status_code}")
        else:
            print(f"❌ Schedule creation failed: {create_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_schedules_for_student_group()