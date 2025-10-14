#!/usr/bin/env python3
"""
Test student endpoints to debug the issue
"""
import requests
import json

def test_student_endpoints():
    """Test student endpoints to identify the issue"""
    
    # Login as student
    student_creds = {'email': 'ahmed.student@university.edu', 'password': 'student2025'}
    login_response = requests.post('http://localhost:8000/auth/login', json=student_creds)
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access_token')
        user_info = token_data.get('user', {})
        
        print('✅ Student login successful')
        print(f'   User ID: {user_info.get("id")}')
        print(f'   Email: {user_info.get("email")}')
        print(f'   Role: {user_info.get("role")}')
        print()
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test profile endpoint
        print("🔍 Testing /student/profile...")
        profile_response = requests.get('http://localhost:8000/student/profile', headers=headers)
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print('✅ Profile endpoint works')
            print(f'   Student ID: {profile_data.get("id")}')
            print(f'   Name: {profile_data.get("prenom")} {profile_data.get("nom")}')
            print(f'   Group: {profile_data.get("groupe", {}).get("nom", "No group")}')
        else:
            print(f'❌ Profile error: {profile_response.status_code}')
            print(profile_response.text)
        
        print()
        
        # Test schedule endpoint
        print("🔍 Testing /student/schedule...")
        try:
            schedule_response = requests.get('http://localhost:8000/student/schedule', headers=headers, timeout=10)
            
            if schedule_response.status_code == 200:
                schedule_data = schedule_response.json()
                print('✅ Schedule endpoint works')
                print(f'   Found {len(schedule_data.get("schedules", []))} schedules')
            else:
                print(f'❌ Schedule error: {schedule_response.status_code}')
                print(schedule_response.text)
        except Exception as e:
            print(f'❌ Schedule request failed: {e}')
        
        print()
        
        # Test today's schedule endpoint
        print("🔍 Testing /student/schedule/today...")
        try:
            today_response = requests.get('http://localhost:8000/student/schedule/today', headers=headers, timeout=10)
            
            if today_response.status_code == 200:
                today_data = today_response.json()
                print('✅ Today schedule endpoint works')
                print(f'   Found {len(today_data)} today schedules')
            else:
                print(f'❌ Today schedule error: {today_response.status_code}')
                print(today_response.text)
        except Exception as e:
            print(f'❌ Today schedule request failed: {e}')
    
    else:
        print(f'❌ Login failed: {login_response.status_code}')
        print(login_response.text)

if __name__ == "__main__":
    test_student_endpoints()