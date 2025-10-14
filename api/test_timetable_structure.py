#!/usr/bin/env python3
"""
Get detailed university timetable structure for frontend debugging
"""

import requests
import json

def test_timetable_structure():
    print("🔍 DETAILED UNIVERSITY TIMETABLE STRUCTURE")
    print("=" * 60)
    
    # Login
    login_response = requests.post("http://localhost:8000/auth/login", json={
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get university timetable
    response = requests.get("http://localhost:8000/student/timetable?week_offset=0", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ API call failed: {response.status_code}")
        return
    
    data = response.json()
    
    if not data.get('success'):
        print(f"❌ API error: {data.get('error')}")
        return
    
    print("✅ API call successful")
    print(f"📊 Top level keys: {list(data.keys())}")
    
    timetable = data.get('timetable', {})
    time_slots = data.get('time_slots', [])
    days = data.get('days', [])
    week_info = data.get('week_info', {})
    student_info = data.get('student_info', {})
    
    print(f"\n📅 Week Info:")
    print(f"  Start: {week_info.get('start_date')}")
    print(f"  End: {week_info.get('end_date')}")
    print(f"  Offset: {week_info.get('week_offset')}")
    
    print(f"\n👤 Student Info:")
    print(f"  Name: {student_info.get('name')}")
    print(f"  Group: {student_info.get('group', {}).get('name')}")
    
    print(f"\n🕐 Time Slots ({len(time_slots)}):")
    for slot in time_slots[:3]:  # Show first 3
        print(f"  - {slot.get('id')}: {slot.get('label')}")
    
    print(f"\n📅 Days ({len(days)}):")
    for day in days:
        print(f"  - {day.get('id')}: {day.get('name')}")
    
    print(f"\n🎓 Timetable Structure:")
    total_courses = 0
    course_examples = []
    
    for slot_id, slot_data in timetable.items():
        courses = slot_data.get('courses', {})
        slot_course_count = len([c for c in courses.values() if c])
        total_courses += slot_course_count
        
        time_info = slot_data.get('time_info', {})
        print(f"  {slot_id} ({time_info.get('label', 'Unknown time')}): {slot_course_count} courses")
        
        # Get first non-null course as example
        for day_id, course in courses.items():
            if course and len(course_examples) < 3:
                course_examples.append({
                    'slot': slot_id,
                    'day': day_id,
                    'course': course
                })
    
    print(f"\n📚 Total Courses: {total_courses}")
    
    if course_examples:
        print(f"\n🎯 Sample Courses:")
        for i, example in enumerate(course_examples, 1):
            course = example['course']
            subject = course.get('subject', {})
            teacher = course.get('teacher', {})
            room = course.get('room', {})
            
            print(f"  {i}. {example['day'].title()} @ {example['slot']}:")
            print(f"     Subject: {subject.get('nom', 'Unknown')}")
            print(f"     Teacher: {teacher.get('prenom', '')} {teacher.get('nom', '')}")
            print(f"     Room: {room.get('code', 'Unknown')}")
    else:
        print("\n⚠️ No course examples found")
    
    print(f"\n🎨 Frontend Integration Check:")
    print(f"  ✅ API endpoint: /student/timetable")
    print(f"  ✅ Response structure: success = {data.get('success')}")
    print(f"  ✅ Timetable data: {len(timetable)} time slots")
    print(f"  ✅ Time slots array: {len(time_slots)} items")
    print(f"  ✅ Days array: {len(days)} items")
    print(f"  ✅ Total courses: {total_courses}")
    
    if total_courses > 0:
        print(f"  🎉 Frontend should display university timetable table!")
    else:
        print(f"  ⚠️ No courses to display")

if __name__ == "__main__":
    test_timetable_structure()