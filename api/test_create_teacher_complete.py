"""
Create test teacher and test endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def create_and_test_teacher():
    print("=" * 80)
    print("🧪 CREATE TEST TEACHER AND TEST ENDPOINTS")
    print("=" * 80)
    
    # Step 1: Get departments
    print("\n📋 Step 1: Getting departments...")
    try:
        dept_response = requests.get(f"{BASE_URL}/auth/departments")
        if dept_response.status_code == 200:
            departments = dept_response.json()
            print(f"   ✅ Found {len(departments)} departments")
            if departments:
                dept_id = departments[0]["id"]
                dept_name = departments[0]["nom"]
                print(f"   Using department: {dept_name} ({dept_id})")
        else:
            print(f"   ❌ Failed to get departments")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 2: Register a test teacher
    print("\n📝 Step 2: Registering test teacher...")
    teacher_data = {
        "nom": "TestTeacher",
        "prenom": "Jean",
        "email": f"test.teacher.{datetime.now().timestamp()}@university.com",
        "password": "password123",
        "role": "TEACHER",
        "department_id": dept_id
    }
    
    try:
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json=teacher_data
        )
        print(f"   Status: {register_response.status_code}")
        
        if register_response.status_code == 200:
            teacher = register_response.json()
            print(f"   ✅ Teacher registered successfully!")
            print(f"   Email: {teacher_data['email']}")
        else:
            print(f"   ❌ Registration failed: {register_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Registration error: {e}")
        return
    
    # Step 3: Login as the new teacher
    print("\n🔐 Step 3: Login as teacher...")
    login_data = {
        "email": teacher_data["email"],
        "password": teacher_data["password"]
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            user = login_result["user"]
            print(f"   ✅ Login successful!")
            print(f"   User: {user.get('prenom')} {user.get('nom')}")
            print(f"   Token: {token[:30]}...")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 4: Test profile endpoint
    print("\n📋 Step 4: Testing /teacher/profile endpoint...")
    try:
        profile_response = requests.get(f"{BASE_URL}/teacher/profile", headers=headers)
        print(f"   Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"   ✅ Profile retrieved successfully!")
            print(f"\n   Teacher Info:")
            print(f"      Name: {profile['teacher_info']['prenom']} {profile['teacher_info']['nom']}")
            print(f"      Email: {profile['teacher_info']['email']}")
            print(f"      Created: {profile['teacher_info']['createdAt']}")
            
            print(f"\n   Department:")
            print(f"      Name: {profile['department']['nom']}")
            print(f"      ID: {profile['department']['id']}")
            print(f"      Specialties: {len(profile['department']['specialties'])}")
            
            for specialty in profile['department']['specialties']:
                print(f"         - {specialty['nom']} ({len(specialty['levels'])} levels)")
            
            if profile.get('department_head'):
                print(f"\n   Department Head:")
                print(f"      {profile['department_head']['prenom']} {profile['department_head']['nom']}")
            else:
                print(f"\n   Department Head: None")
            
            print(f"\n   Subjects Taught: {len(profile.get('subjects_taught', []))}")
            for subject in profile.get('subjects_taught', []):
                print(f"      - {subject['nom']}")
        else:
            print(f"   ❌ Profile fetch failed")
            print(f"   Response: {profile_response.text}")
            
    except Exception as e:
        print(f"   ❌ Profile error: {e}")
    
    # Step 5: Test schedule endpoint
    print("\n📅 Step 5: Testing /teacher/schedule endpoint...")
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    
    start_date = monday.strftime('%Y-%m-%d')
    end_date = sunday.strftime('%Y-%m-%d')
    
    try:
        schedule_response = requests.get(
            f"{BASE_URL}/teacher/schedule",
            params={"start_date": start_date, "end_date": end_date},
            headers=headers
        )
        print(f"   Status: {schedule_response.status_code}")
        
        if schedule_response.status_code == 200:
            schedule_data = schedule_response.json()
            schedules = schedule_data.get('schedules', [])
            print(f"   ✅ Schedule retrieved successfully!")
            print(f"\n   Date Range: {schedule_data['date_range']['start']} to {schedule_data['date_range']['end']}")
            print(f"   Teacher: {schedule_data['teacher_info']['prenom']} {schedule_data['teacher_info']['nom']}")
            print(f"   Total Classes: {len(schedules)}")
            
            if schedules:
                print(f"\n   Schedule Details:")
                for idx, schedule in enumerate(schedules[:3], 1):
                    print(f"\n      Class {idx}:")
                    print(f"         Date: {schedule['date']}")
                    print(f"         Time: {schedule['heure_debut']} - {schedule['heure_fin']}")
                    print(f"         Subject: {schedule['matiere']['nom']}")
                    print(f"         Group: {schedule['groupe']['nom']}")
                    print(f"         Room: {schedule['salle']['code']}")
                    print(f"         Status: {schedule['status']}")
                
                if len(schedules) > 3:
                    print(f"\n      ... and {len(schedules) - 3} more classes")
            else:
                print(f"\n   ℹ️  No classes scheduled for this week")
                print(f"   This is expected for a newly created teacher with no schedule")
        else:
            print(f"   ❌ Schedule fetch failed")
            print(f"   Response: {schedule_response.text}")
            
    except Exception as e:
        print(f"   ❌ Schedule error: {e}")
    
    # Step 6: Test today's schedule
    print("\n📅 Step 6: Testing /teacher/schedule/today endpoint...")
    try:
        today_response = requests.get(f"{BASE_URL}/teacher/schedule/today", headers=headers)
        print(f"   Status: {today_response.status_code}")
        
        if today_response.status_code == 200:
            today_schedules = today_response.json()
            print(f"   ✅ Today's schedule retrieved!")
            print(f"   Classes today: {len(today_schedules)}")
            
            if today_schedules:
                for idx, schedule in enumerate(today_schedules, 1):
                    print(f"\n      Class {idx}:")
                    print(f"         Time: {schedule['heure_debut']} - {schedule['heure_fin']}")
                    print(f"         Subject: {schedule['matiere']['nom']}")
                    print(f"         Group: {schedule['groupe']['nom']}")
            else:
                print(f"\n   ℹ️  No classes scheduled for today")
                print(f"   This is expected for a newly created teacher")
        else:
            print(f"   ❌ Today's schedule fetch failed")
            print(f"   Response: {today_response.text}")
            
    except Exception as e:
        print(f"   ❌ Today's schedule error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print(f"\n📧 Teacher Email: {teacher_data['email']}")
    print(f"🔑 Password: {teacher_data['password']}")
    print(f"🎫 Token: {token[:50]}...")

if __name__ == "__main__":
    create_and_test_teacher()
