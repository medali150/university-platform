#!/usr/bin/env python3
"""
Test university schedule system after fixing unique constraint issues
"""

import requests
import json
from datetime import datetime

# API Configuration
API_BASE = "http://localhost:8000"

def test_system():
    print("🧪 Testing University Schedule System - Post Fix")
    print("=" * 60)
    
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
    
    # Step 2: Check existing schedules first
    print("\n📅 Step 2: Check existing schedules...")
    timetable_response = requests.get(f"{API_BASE}/student/timetable?week_offset=1", headers=headers)
    
    if timetable_response.status_code == 200:
        data = timetable_response.json()
        if data.get("success"):
            timetable = data.get("timetable", {})
            total_courses = sum(len(slot_data.get("courses", {})) for slot_data in timetable.values())
            print(f"📊 Found {total_courses} existing courses in timetable")
            
            if total_courses > 0:
                print("✅ Schedules already exist, skipping creation")
            else:
                print("ℹ️ No existing schedules found")
        else:
            print(f"⚠️ Timetable error: {data.get('error')}")
    else:
        print(f"❌ Failed to check timetable: {timetable_response.status_code}")
    
    # Step 3: Try to create university schedule (should handle duplicates now)
    print("\n🏫 Step 3: Test university schedule creation...")
    create_response = requests.post(f"{API_BASE}/student/admin/create-university-schedule", headers=headers)
    
    if create_response.status_code == 200:
        create_data = create_response.json()
        if create_data.get("success"):
            print(f"✅ Schedule creation successful!")
            print(f"📝 Message: {create_data.get('message')}")
            print(f"👥 Group: {create_data.get('group_name')}")
            print(f"📅 Week start: {create_data.get('week_start')}")
            
            schedules = create_data.get("schedules_created", [])
            print(f"📚 Created/Updated {len(schedules)} schedule entries:")
            for i, schedule in enumerate(schedules[:5]):  # Show first 5
                print(f"  {i+1}. {schedule['day']} {schedule['time']} - {schedule['subject']} ({schedule['teacher']}) - {schedule['room']}")
            if len(schedules) > 5:
                print(f"  ... and {len(schedules) - 5} more")
        else:
            print(f"❌ Schedule creation error: {create_data.get('error')}")
    else:
        print(f"❌ Schedule creation failed: {create_response.status_code}")
        try:
            error_data = create_response.json()
            print(f"Error details: {error_data}")
        except:
            print(f"Raw error: {create_response.text}")
    
    # Step 4: Test the university timetable display
    print("\n🎓 Step 4: Test university timetable display...")
    timetable_response = requests.get(f"{API_BASE}/student/timetable?week_offset=1", headers=headers)
    
    if timetable_response.status_code == 200:
        data = timetable_response.json()
        if data.get("success"):
            print("✅ Timetable retrieval successful!")
            
            # Display timetable summary
            timetable = data.get("timetable", {})
            days = data.get("days", [])
            time_slots = data.get("time_slots", [])
            week_info = data.get("week_info", {})
            student_info = data.get("student_info", {})
            
            print(f"\n📋 UNIVERSITY TIMETABLE SUMMARY")
            print(f"👤 Student: {student_info.get('name')}")
            print(f"👥 Group: {student_info.get('group')}")
            print(f"📅 Week: {week_info.get('start_date')} to {week_info.get('end_date')}")
            print(f"🕐 Time slots: {len(time_slots)}")
            print(f"📅 Days: {len(days)}")
            
            # Count total courses
            total_courses = 0
            for slot_data in timetable.values():
                courses = slot_data.get("courses", {})
                total_courses += len(courses)
            
            print(f"📚 Total courses in timetable: {total_courses}")
            
            if total_courses > 0:
                print("\n🎯 Sample timetable entries:")
                entry_count = 0
                for time_slot, slot_data in timetable.items():
                    courses = slot_data.get("courses", {})
                    for day, course in courses.items():
                        if entry_count < 3:  # Show first 3 entries
                            if isinstance(course, dict):
                                subject = course.get("subject", {}).get("name", "Unknown") if isinstance(course.get("subject"), dict) else str(course.get("subject", "Unknown"))
                                teacher = course.get("teacher", {})
                                teacher_name = f"{teacher.get('prenom', '')} {teacher.get('nom', '')}" if isinstance(teacher, dict) else str(teacher)
                                room = course.get("room", {}).get("code", "Unknown") if isinstance(course.get("room"), dict) else str(course.get("room", "Unknown"))
                                print(f"  • {day.title()} {time_slot}: {subject} ({teacher_name.strip()}) - {room}")
                            else:
                                print(f"  • {day.title()} {time_slot}: {str(course)}")
                            entry_count += 1
                
                print("\n🎉 University timetable system is working perfectly!")
            else:
                print("ℹ️ No courses found in timetable")
                
        else:
            print(f"❌ Timetable error: {data.get('error')}")
    else:
        print(f"❌ Failed to get timetable: {timetable_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_system()