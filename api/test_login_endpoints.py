#!/usr/bin/env python3
"""
Test login and find available endpoints for real timetable creation
"""
import requests
import json

def test_login_and_endpoints():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Login and Available Endpoints")
    print("=" * 50)
    
    # Try to login with different admin accounts
    admin_credentials = [
        {"email": "admin@university.edu", "password": "admin123"},
        {"email": "admin@admin.com", "password": "admin123"},
        {"email": "boubaked@example.com", "password": "boubaked123"},
        {"email": "boubaked.saadallah@exemple.com", "password": "secure123"}
    ]
    
    admin_token = None
    for creds in admin_credentials:
        try:
            response = requests.post(f"{base_url}/auth/login", json=creds)
            if response.status_code == 200:
                admin_token = response.json()["access_token"]
                print(f"✅ Admin login successful: {creds['email']}")
                break
            else:
                print(f"❌ Admin login failed for: {creds['email']} - {response.status_code}")
        except Exception as e:
            print(f"❌ Error trying {creds['email']}: {e}")
    
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test different admin endpoints
        endpoints_to_test = [
            "/admin/groups",
            "/admin/subjects", 
            "/admin/rooms",
            "/admin/teachers",
            "/admin/students",
            "/admin/schedules",
            "/department-head/dashboard",
            "/department-head/subjects",
            "/department-head/schedules"
        ]
        
        print("\n🔎 Testing Available Endpoints:")
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                print(f"   {endpoint}: {response.status_code}")
                if endpoint == "/admin/subjects" and response.status_code == 200:
                    subjects = response.json()
                    print(f"      📖 Found {len(subjects)} subjects")
            except Exception as e:
                print(f"   {endpoint}: ERROR - {e}")
    
    # Test student login
    print("\n👨‍🎓 Testing Student Login:")
    student_credentials = [
        {"email": "student.li04@univ.tn", "password": "student123"},
        {"email": "ahmed.student@university.edu", "password": "student2025"}
    ]
    
    for creds in student_credentials:
        try:
            response = requests.post(f"{base_url}/auth/login", json=creds)
            if response.status_code == 200:
                student_token = response.json()["access_token"]
                student_headers = {"Authorization": f"Bearer {student_token}"}
                print(f"✅ Student login successful: {creds['email']}")
                
                # Test student timetable endpoint
                timetable_response = requests.get(f"{base_url}/student/timetable", headers=student_headers)
                print(f"   📅 Timetable endpoint: {timetable_response.status_code}")
                if timetable_response.status_code == 200:
                    timetable_data = timetable_response.json()
                    print(f"   📊 Timetable data available: {timetable_data.get('success', False)}")
                    if 'timetable' in timetable_data:
                        courses = len(timetable_data['timetable'])
                        print(f"   📚 Total courses: {courses}")
                break
            else:
                print(f"❌ Student login failed for: {creds['email']} - {response.status_code}")
        except Exception as e:
            print(f"❌ Error testing student {creds['email']}: {e}")

if __name__ == "__main__":
    test_login_and_endpoints()