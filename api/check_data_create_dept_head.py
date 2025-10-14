#!/usr/bin/env python3
"""
Check current data and create department head for real timetable management
"""
import requests
import json

def check_current_data_and_create_dept_head():
    base_url = "http://localhost:8000"
    
    print("🔍 CHECKING CURRENT DATA & CREATING DEPARTMENT HEAD")
    print("=" * 60)
    
    # Login as student to see current state
    student_login = requests.post(f"{base_url}/auth/login", json={
        "email": "ahmed.student@university.edu",
        "password": "student2025"
    })
    
    if student_login.status_code == 200:
        student_token = student_login.json()["access_token"]
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        # Check current timetable
        timetable_response = requests.get(f"{base_url}/student/timetable", headers=student_headers)
        if timetable_response.status_code == 200:
            data = timetable_response.json()
            print(f"📊 Current timetable status: {data.get('success', False)}")
            print(f"📚 Current courses: {len(data.get('timetable', []))}")
            print(f"👥 Student group: {data.get('student_info', {}).get('group_name', 'Unknown')}")
            
            # Show current courses
            if 'timetable' in data:
                print("\n📅 Current Courses:")
                for course in data['timetable']:
                    print(f"   • {course.get('subject_name', 'Unknown')} - {course.get('day', 'Unknown')} {course.get('time_slot', 'Unknown')}")
    
    # Create department head for managing real timetable
    print("\n👨‍💼 Creating Department Head for Real Timetable Management...")
    
    # Try to register a department head
    dept_head_data = {
        "first_name": "Chef",
        "last_name": "Departement Informatique", 
        "email": "chef.info@univ.tn",
        "password": "chef123",
        "role": "department_head"
    }
    
    try:
        register_response = requests.post(f"{base_url}/auth/register", json=dept_head_data)
        if register_response.status_code in [200, 201]:
            print("✅ Department head registered successfully")
        elif register_response.status_code == 422:
            print("📍 Department head already exists")
        else:
            print(f"⚠️ Department head registration issue: {register_response.status_code}")
            print(f"Response: {register_response.text}")
    except Exception as e:
        print(f"❌ Error registering department head: {e}")
    
    # Try to login as department head
    print("\n🔑 Testing Department Head Login...")
    try:
        dept_login = requests.post(f"{base_url}/auth/login", json={
            "email": "chef.info@univ.tn",
            "password": "chef123"
        })
        
        if dept_login.status_code == 200:
            dept_token = dept_login.json()["access_token"]
            dept_headers = {"Authorization": f"Bearer {dept_token}"}
            print("✅ Department head login successful")
            
            # Test department head endpoints
            dept_endpoints = [
                "/department-head/dashboard",
                "/department-head/subjects",
                "/department-head/schedules",
                "/department-head/groups",
                "/department-head/teachers"
            ]
            
            print("\n🔎 Testing Department Head Endpoints:")
            for endpoint in dept_endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", headers=dept_headers)
                    print(f"   {endpoint}: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"      📊 Items found: {len(data)}")
                        elif isinstance(data, dict):
                            print(f"      📊 Data available: {list(data.keys())}")
                except Exception as e:
                    print(f"   {endpoint}: ERROR - {e}")
            
            # Try to create a subject via department head
            print("\n📖 Testing Subject Creation...")
            test_subject = {
                "name": "Développement Mobile",
                "code": "DEV_MOB", 
                "credits": 4
            }
            
            try:
                subject_response = requests.post(f"{base_url}/department-head/subjects", 
                                               json=test_subject, headers=dept_headers)
                print(f"   Subject creation: {subject_response.status_code}")
                if subject_response.status_code in [200, 201]:
                    print("   ✅ Subject created successfully")
                elif subject_response.status_code == 422:
                    print("   📍 Subject already exists")
                else:
                    print(f"   Response: {subject_response.text}")
            except Exception as e:
                print(f"   ❌ Subject creation error: {e}")
                
        else:
            print(f"❌ Department head login failed: {dept_login.status_code}")
            print(f"Response: {dept_login.text}")
            
    except Exception as e:
        print(f"❌ Error testing department head login: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. Use department head login: chef.info@univ.tn / chef123")
    print("2. Create subjects, rooms, and schedules for your real timetable")
    print("3. Assign students to the correct groups (LI 04, etc.)")
    print("=" * 60)

if __name__ == "__main__":
    check_current_data_and_create_dept_head()