#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta, date

def create_schedules_via_api():
    """Create schedules for the student's group using the department head API"""
    
    print("=== CREATING SCHEDULES VIA API ===")
    
    base_url = "http://localhost:8000"
    
    # First, we need to login as a department head
    # Let me check what department head accounts exist
    
    # Try common department head credentials
    dept_head_credentials = [
        {"email": "john.doe@university.com", "password": "depthead123"},
        {"email": "pierre.leclerc@university.com", "password": "depthead123"},
        {"email": "admin@university.com", "password": "admin123"},
        {"email": "souhir@university.edu", "password": "daligh15"}
    ]
    
    token = None
    for creds in dept_head_credentials:
        try:
            print(f"Trying to login as: {creds['email']}")
            login_response = requests.post(f"{base_url}/auth/login", json=creds)
            
            if login_response.status_code == 200:
                login_data = login_response.json()
                user_info = login_data.get("user", {})
                
                if user_info.get("role") == "DEPARTMENT_HEAD":
                    token = login_data["access_token"]
                    print(f"✅ Logged in as department head: {user_info.get('email')}")
                    break
                else:
                    print(f"❌ User is not a department head: {user_info.get('role')}")
            else:
                print(f"❌ Login failed: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ Login error: {e}")
    
    if not token:
        print("❌ Could not login as department head")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get available resources
    print("\n🔍 Getting available resources...")
    
    try:
        # Get subjects
        subjects_response = requests.get(f"{base_url}/department-head/subjects", headers=headers)
        subjects = subjects_response.json() if subjects_response.status_code == 200 else []
        print(f"   📚 Found {len(subjects)} subjects")
        
        # Get teachers
        teachers_response = requests.get(f"{base_url}/department-head/teachers", headers=headers)
        teachers = teachers_response.json() if teachers_response.status_code == 200 else []
        print(f"   👨‍🏫 Found {len(teachers)} teachers")
        
        # Get rooms
        rooms_response = requests.get(f"{base_url}/department-head/rooms", headers=headers)
        rooms = rooms_response.json() if rooms_response.status_code == 200 else []
        print(f"   🏛️ Found {len(rooms)} rooms")
        
        # Get groups
        groups_response = requests.get(f"{base_url}/department-head/groups", headers=headers)
        groups = groups_response.json() if groups_response.status_code == 200 else []
        print(f"   👥 Found {len(groups)} groups")
        
        # Find the student's group
        student_group_id = "cmg6pgscy000bbm1o5iy4kd06"
        target_group = None
        
        for group in groups:
            if group.get("id") == student_group_id:
                target_group = group
                break
        
        if not target_group:
            print(f"❌ Student's group not found in department groups")
            print("Available groups:")
            for group in groups[:3]:
                print(f"   - {group.get('nom', 'Unknown')} (ID: {group.get('id', 'Unknown')})")
            return
        
        print(f"✅ Found target group: {target_group.get('nom')}")
        
        if not subjects or not teachers or not rooms:
            print("❌ Missing required resources")
            return
        
        # Create schedule entries
        print(f"\n📅 Creating schedule entries...")
        
        # Get next Monday
        today = date.today()
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        # Schedule template for a week
        schedule_template = [
            {"day": 0, "start": "08:00", "end": "10:00"},  # Monday
            {"day": 0, "start": "10:30", "end": "12:30"},
            {"day": 1, "start": "08:00", "end": "10:00"},  # Tuesday
            {"day": 1, "start": "14:00", "end": "16:00"},
            {"day": 2, "start": "10:30", "end": "12:30"},  # Wednesday
            {"day": 3, "start": "08:00", "end": "10:00"},  # Thursday
            {"day": 3, "start": "14:00", "end": "16:00"},
            {"day": 4, "start": "08:00", "end": "10:00"},  # Friday
        ]
        
        created_schedules = []
        
        for i, schedule_info in enumerate(schedule_template):
            try:
                # Calculate date
                schedule_date = next_monday + timedelta(days=schedule_info["day"])
                
                # Select resources (rotate through available options)
                subject = subjects[i % len(subjects)]
                teacher = teachers[i % len(teachers)]
                room = rooms[i % len(rooms)]
                
                # Create schedule payload
                schedule_payload = {
                    "date": schedule_date.strftime("%Y-%m-%d"),
                    "start_time": schedule_info["start"],
                    "end_time": schedule_info["end"],
                    "subject_id": subject["id"],
                    "group_id": student_group_id,
                    "teacher_id": teacher["id"],
                    "room_id": room["id"]
                }
                
                print(f"   Creating: {schedule_date.strftime('%A %Y-%m-%d')} {schedule_info['start']}-{schedule_info['end']}")
                
                # Create the schedule
                create_response = requests.post(
                    f"{base_url}/department-head/schedules",
                    json=schedule_payload,
                    headers=headers
                )
                
                if create_response.status_code == 201:
                    created_schedules.append(schedule_payload)
                    print(f"   ✅ Created successfully")
                else:
                    print(f"   ❌ Failed: {create_response.status_code} - {create_response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error creating schedule: {e}")
        
        print(f"\n🎉 SCHEDULE CREATION COMPLETE!")
        print(f"Successfully created {len(created_schedules)} schedule entries")
        
        return created_schedules
        
    except Exception as e:
        print(f"❌ Error getting resources: {e}")
        return None

if __name__ == "__main__":
    create_schedules_via_api()