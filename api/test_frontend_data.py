#!/usr/bin/env python3
"""
Test that frontend will get the university timetable data
"""

import requests

def test_frontend_data():
    print("🎓 TESTING FRONTEND DATA WITH WEEK_OFFSET=1")
    print("=" * 50)
    
    # Login
    login_response = requests.post("http://localhost:8000/auth/login", json={
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the exact call the frontend will make
    response = requests.get("http://localhost:8000/student/timetable?week_offset=1", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            timetable = data.get('timetable', {})
            time_slots = data.get('time_slots', [])
            days = data.get('days', [])
            student_info = data.get('student_info', {})
            week_info = data.get('week_info', {})
            
            # Count courses
            total_courses = 0
            sample_courses = []
            
            for slot_id, slot_data in timetable.items():
                courses = slot_data.get('courses', {})
                for day_id, course in courses.items():
                    if course and course != "null":
                        total_courses += 1
                        if len(sample_courses) < 3:
                            # Handle the course data structure properly
                            subject_name = "Unknown Subject"
                            teacher_name = "Unknown Teacher"
                            room_code = "Unknown Room"
                            
                            try:
                                if isinstance(course, dict):
                                    subject = course.get('subject', {})
                                    if isinstance(subject, dict):
                                        subject_name = subject.get('nom', 'Unknown Subject')
                                    
                                    teacher = course.get('teacher', {})
                                    if isinstance(teacher, dict):
                                        teacher_name = f"{teacher.get('prenom', '')} {teacher.get('nom', '')}".strip()
                                    
                                    room = course.get('room', {})
                                    if isinstance(room, dict):
                                        room_code = room.get('code', 'Unknown Room')
                            except:
                                pass
                            
                            time_info = slot_data.get('time_info', {})
                            time_label = time_info.get('label', slot_id)
                            
                            sample_courses.append(f"{day_id.title()} {time_label}: {subject_name} ({teacher_name}) - {room_code}")
            
            print(f"✅ API Response: success = {data.get('success')}")
            print(f"📚 Total courses: {total_courses}")
            print(f"👤 Student: {student_info.get('name', 'Unknown')}")
            print(f"👥 Group: {student_info.get('group', {}).get('name', 'Unknown')}")
            print(f"📅 Week: {week_info.get('start_date')} to {week_info.get('end_date')}")
            print(f"🎯 Table: {len(time_slots)} rows × {len(days)} columns")
            
            if sample_courses:
                print(f"\n📋 Sample courses (what frontend will show):")
                for course in sample_courses:
                    print(f"  • {course}")
            
            print(f"\n🎉 FRONTEND DATA IS READY!")
            print(f"✅ The university timetable should now display with {total_courses} courses")
            print(f"✅ Navigate to: http://localhost:3000/dashboard/student/timetable")
            
        else:
            print(f"❌ API error: {data.get('error')}")
    else:
        print(f"❌ HTTP error: {response.status_code}")

if __name__ == "__main__":
    test_frontend_data()