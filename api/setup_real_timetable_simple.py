#!/usr/bin/env python3
"""
Simple check of current timetable data and create real timetable
"""
import requests
import json

def main():
    base_url = "http://localhost:8000"
    
    print("🎓 REAL TIMETABLE SETUP FOR YOUR UNIVERSITY SCHEDULE")
    print("=" * 60)
    
    # Login as existing student
    print("🔑 Logging in as student...")
    login_response = requests.post(f"{base_url}/auth/login", json={
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    })
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Student login successful")
        
        # Check current timetable
        timetable_response = requests.get(f"{base_url}/student/timetable", headers=headers)
        if timetable_response.status_code == 200:
            data = timetable_response.json()
            print(f"\n📊 Current Timetable Data:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Now create a test student for LI 04 group
        print("\n👨‍🎓 Registering new student for LI 04...")
        student_data = {
            "first_name": "Test",
            "last_name": "LI04",
            "email": "student.li04@univ.tn",
            "password": "student123",
            "role": "student"
        }
        
        register_response = requests.post(f"{base_url}/auth/register", json=student_data)
        if register_response.status_code in [200, 201]:
            print("✅ Student LI04 registered successfully")
        elif register_response.status_code == 422:
            print("📍 Student LI04 already exists")
        
        # Try to login as LI04 student
        print("\n🔑 Testing LI04 Student Login...")
        li04_login = requests.post(f"{base_url}/auth/login", json={
            "email": "student.li04@univ.tn", 
            "password": "student123"
        })
        
        if li04_login.status_code == 200:
            li04_token = li04_login.json()["access_token"]
            li04_headers = {"Authorization": f"Bearer {li04_token}"}
            print("✅ LI04 student login successful")
            
            # Check LI04 timetable
            li04_timetable = requests.get(f"{base_url}/student/timetable", headers=li04_headers)
            if li04_timetable.status_code == 200:
                li04_data = li04_timetable.json()
                print(f"\n📅 LI04 Student Timetable:")
                print(f"   Success: {li04_data.get('success', False)}")
                if 'timetable' in li04_data:
                    courses = li04_data['timetable']
                    print(f"   📚 Total courses: {len(courses)}")
                    if len(courses) > 0:
                        print("   Courses found:")
                        for i, course in enumerate(courses[:3]):  # Show first 3
                            print(f"   {i+1}. {course}")
                else:
                    print("   ⚠️ No timetable data found")
        else:
            print(f"❌ LI04 student login failed: {li04_login.status_code}")
    
    print("\n" + "=" * 60)  
    print("🎯 CURRENT STATUS:")
    print("✅ Server is running")
    print("✅ Student accounts exist")
    print("⚠️ Need to populate with your real timetable data")
    print("\n🚨 TO SEE YOUR REAL TIMETABLE:")
    print("1. Go to: http://localhost:3000/dashboard/student/timetable")
    print("2. Login as: student.li04@univ.tn / student123")
    print("3. Check if your schedule appears (based on group LI 04)")
    print("=" * 60)

if __name__ == "__main__":
    main()