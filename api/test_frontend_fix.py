#!/usr/bin/env python3
"""
Quick test for the fixed frontend schedule endpoint
"""

import requests
import json

# API Configuration
API_BASE = "http://localhost:8000"

def test_frontend_schedule():
    print("🧪 Testing Frontend Schedule Endpoint Fix")
    print("=" * 50)
    
    # Step 1: Login as student
    print("\n🔐 Step 1: Login as student...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Test the failing endpoint
    print("\n📅 Step 2: Test schedule endpoint that was failing...")
    schedule_response = requests.get(
        f"{API_BASE}/student/schedule?start_date=2025-09-29&end_date=2025-10-05", 
        headers=headers
    )
    
    if schedule_response.status_code == 200:
        data = schedule_response.json()
        print("✅ Schedule endpoint now working!")
        
        # Display summary
        timetable = data.get("timetable", {})
        student_info = data.get("student_info", {})
        week_info = data.get("week_info", {})
        
        print(f"👤 Student: {student_info.get('name')}")
        print(f"📅 Week: {week_info.get('week_start')} to {week_info.get('week_end')}")
        print(f"🔢 Week offset: {week_info.get('week_offset')}")
        print(f"📊 Time slots in timetable: {len(timetable)}")
        
        # Count courses
        total_courses = 0
        for slot_data in timetable.values():
            days = slot_data.get("days", {})
            for day_courses in days.values():
                if day_courses:
                    total_courses += 1
        
        print(f"📚 Total courses found: {total_courses}")
        
        if total_courses > 0:
            print("\n🎯 Sample course:")
            for slot_id, slot_data in timetable.items():
                days = slot_data.get("days", {})
                for day_id, course in days.items():
                    if course:
                        subject_name = course.get("subject", {}).get("nom", "Unknown")
                        teacher_name = course.get("teacher", {}).get("nom", "Unknown")
                        room_code = course.get("room", {}).get("code", "Unknown")
                        print(f"  • {day_id.title()}: {subject_name} - {teacher_name} - {room_code}")
                        break
                if course:
                    break
        
        print("\n🎉 Frontend schedule endpoint is now working!")
        
    else:
        print(f"❌ Schedule endpoint still failing: {schedule_response.status_code}")
        try:
            error_data = schedule_response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Raw error: {schedule_response.text}")
    
    # Step 3: Test today's schedule endpoint
    print("\n📅 Step 3: Test today's schedule endpoint...")
    today_response = requests.get(f"{API_BASE}/student/schedule/today", headers=headers)
    
    if today_response.status_code == 200:
        print("✅ Today's schedule endpoint working!")
        today_data = today_response.json()
        today_schedules = today_data.get("schedules", [])
        print(f"📚 Today's courses: {len(today_schedules)}")
    else:
        print(f"⚠️ Today's schedule: {today_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_frontend_schedule()