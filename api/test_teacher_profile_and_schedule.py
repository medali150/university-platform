"""
Test script for teacher profile and schedule endpoints
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_teacher_profile_and_schedule():
    print("=" * 80)
    print("🧪 TESTING TEACHER PROFILE AND SCHEDULE ENDPOINTS")
    print("=" * 80)
    
    # Step 1: Login as a teacher
    print("\n📝 Step 1: Login as teacher...")
    login_data = {
        "email": "teacher@university.com",
        "password": "password123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result["access_token"]
            user = login_result["user"]
            print(f"   ✅ Login successful!")
            print(f"   User: {user.get('prenom')} {user.get('nom')} ({user.get('role')})")
            print(f"   Token: {token[:20]}...")
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
    
    # Step 2: Test profile endpoint
    print("\n📋 Step 2: Testing /teacher/profile endpoint...")
    try:
        profile_response = requests.get(f"{BASE_URL}/teacher/profile", headers=headers)
        print(f"   Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            print(f"   ✅ Profile retrieved successfully!")
            print(f"\n   Teacher Info:")
            print(f"      Name: {profile['teacher_info']['prenom']} {profile['teacher_info']['nom']}")
            print(f"      Email: {profile['teacher_info']['email']}")
            print(f"      Image URL: {profile['teacher_info'].get('image_url', 'None')}")
            
            print(f"\n   Department:")
            print(f"      Name: {profile['department']['nom']}")
            print(f"      Specialties: {len(profile['department']['specialties'])}")
            
            if profile.get('department_head'):
                print(f"\n   Department Head:")
                print(f"      {profile['department_head']['prenom']} {profile['department_head']['nom']}")
            
            print(f"\n   Subjects Taught: {len(profile.get('subjects_taught', []))}")
            for subject in profile.get('subjects_taught', []):
                print(f"      - {subject['nom']}")
        else:
            print(f"   ❌ Profile fetch failed: {profile_response.text}")
            
    except Exception as e:
        print(f"   ❌ Profile error: {e}")
    
    # Step 3: Test schedule endpoint
    print("\n📅 Step 3: Testing /teacher/schedule endpoint...")
    
    # Get current week
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
            print(f"   Total Classes: {len(schedules)}")
            
            if schedules:
                print(f"\n   Schedule Details:")
                for idx, schedule in enumerate(schedules[:5], 1):  # Show first 5
                    print(f"\n      Class {idx}:")
                    print(f"         Date: {schedule['date']}")
                    print(f"         Time: {schedule['heure_debut']} - {schedule['heure_fin']}")
                    print(f"         Subject: {schedule['matiere']['nom']}")
                    print(f"         Group: {schedule['groupe']['nom']}")
                    print(f"         Room: {schedule['salle']['code']}")
                    print(f"         Status: {schedule['status']}")
                
                if len(schedules) > 5:
                    print(f"\n      ... and {len(schedules) - 5} more classes")
            else:
                print(f"\n   ℹ️  No classes scheduled for this week")
        else:
            print(f"   ❌ Schedule fetch failed: {schedule_response.text}")
            
    except Exception as e:
        print(f"   ❌ Schedule error: {e}")
    
    # Step 4: Test today's schedule
    print("\n📅 Step 4: Testing /teacher/schedule/today endpoint...")
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
        else:
            print(f"   ❌ Today's schedule fetch failed: {today_response.text}")
            
    except Exception as e:
        print(f"   ❌ Today's schedule error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_teacher_profile_and_schedule()
