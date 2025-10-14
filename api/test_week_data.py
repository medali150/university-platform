#!/usr/bin/env python3
"""
Test different weeks to see where the university timetable data is
"""

import requests
import json
from datetime import datetime, timedelta

# API Configuration
API_BASE = "http://localhost:8000"

def test_different_weeks():
    print("📅 TESTING DIFFERENT WEEKS FOR TIMETABLE DATA")
    print("=" * 60)
    
    # Login
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
    
    # Test current week (2025-09-29 to 2025-10-05)
    print("\n🗓️ CURRENT WEEK (2025-09-29 to 2025-10-05):")
    current_week = requests.get(
        f"{API_BASE}/student/schedule?start_date=2025-09-29&end_date=2025-10-05", 
        headers=headers
    )
    
    if current_week.status_code == 200:
        data = current_week.json()
        timetable = data.get('timetable', {})
        total_courses = 0
        for slot_id, slot_data in timetable.items():
            days_data = slot_data.get('days', {})
            for day_id, course in days_data.items():
                if course:
                    total_courses += 1
        print(f"📚 Courses: {total_courses}")
    else:
        print(f"❌ Error: {current_week.status_code}")
    
    # Test next week (2025-10-06 to 2025-10-12) - where we created schedules
    print("\n🗓️ NEXT WEEK (2025-10-06 to 2025-10-12):")
    next_week = requests.get(
        f"{API_BASE}/student/schedule?start_date=2025-10-06&end_date=2025-10-12", 
        headers=headers
    )
    
    if next_week.status_code == 200:
        data = next_week.json()
        timetable = data.get('timetable', {})
        total_courses = 0
        sample_courses = []
        
        for slot_id, slot_data in timetable.items():
            days_data = slot_data.get('days', {})
            for day_id, course in days_data.items():
                if course:
                    total_courses += 1
                    if len(sample_courses) < 3:
                        subject = course.get('subject', {}).get('nom', 'Unknown')
                        teacher_first = course.get('teacher', {}).get('prenom', '')
                        teacher_last = course.get('teacher', {}).get('nom', '')
                        teacher = f"{teacher_first} {teacher_last}".strip()
                        room = course.get('room', {}).get('code', 'Unknown')
                        time_info = slot_data.get('time_info', {}).get('label', slot_id)
                        sample_courses.append(f"{day_id.title()} {time_info}: {subject} ({teacher}) - {room}")
        
        print(f"📚 Courses: {total_courses}")
        if sample_courses:
            print("📋 Sample courses:")
            for course in sample_courses:
                print(f"  • {course}")
        else:
            print("ℹ️ No courses found")
    else:
        print(f"❌ Error: {next_week.status_code}")
    
    # Test university timetable endpoint with different week offsets
    print("\n🏫 UNIVERSITY TIMETABLE ENDPOINTS:")
    
    for week_offset in [0, 1]:
        print(f"\n📅 Week offset {week_offset}:")
        uni_response = requests.get(
            f"{API_BASE}/student/timetable?week_offset={week_offset}", 
            headers=headers
        )
        
        if uni_response.status_code == 200:
            data = uni_response.json()
            if data.get('success'):
                timetable = data.get('timetable', {})
                week_info = data.get('week_info', {})
                
                total_courses = 0
                for slot_data in timetable.values():
                    courses = slot_data.get('courses', {})
                    total_courses += len(courses)
                
                print(f"  📚 Courses: {total_courses}")
                print(f"  📅 Week: {week_info.get('start_date')} to {week_info.get('end_date')}")
                
                if total_courses > 0:
                    print("  📋 This week has the university timetable data! ✅")
                else:
                    print("  ℹ️ No courses this week")
            else:
                print(f"  ❌ Error: {data.get('error')}")
        else:
            print(f"  ❌ HTTP Error: {uni_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("The frontend should navigate to the week with courses!")
    print("If current week is empty, users should see next week's timetable.")

if __name__ == "__main__":
    test_different_weeks()