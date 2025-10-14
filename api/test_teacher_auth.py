"""
Test teacher login and profile fetching
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_teacher_auth():
    async with httpx.AsyncClient() as client:
        print("="*80)
        print("TESTING TEACHER AUTHENTICATION")
        print("="*80)
        
        # 1. Login as teacher
        print("\n1. Logging in as teacher1@university.tn...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "teacher1@university.tn",
                "password": "Test123!"
            }
        )
        
        print(f"Status: {login_response.status_code}")
        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"✅ Login successful!")
            print(f"Access Token: {login_data['access_token'][:50]}...")
            print(f"User Role: {login_data['user']['role']}")
            print(f"User Name: {login_data['user']['prenom']} {login_data['user']['nom']}")
            
            access_token = login_data['access_token']
            
            # 2. Get profile
            print("\n2. Fetching teacher profile...")
            profile_response = await client.get(
                f"{BASE_URL}/teacher/profile",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            print(f"Status: {profile_response.status_code}")
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"✅ Profile fetched successfully!")
                print(f"Teacher: {profile_data['teacher_info']['prenom']} {profile_data['teacher_info']['nom']}")
                print(f"Email: {profile_data['teacher_info']['email']}")
                print(f"Department: {profile_data['department']['nom']}")
                print(f"Subjects taught: {len(profile_data['subjects_taught'])}")
            else:
                print(f"❌ Profile fetch failed!")
                print(f"Error: {profile_response.text}")
            
            # 3. Get schedule
            print("\n3. Fetching teacher schedule...")
            schedule_response = await client.get(
                f"{BASE_URL}/teacher/schedule",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            print(f"Status: {schedule_response.status_code}")
            if schedule_response.status_code == 200:
                schedule_data = schedule_response.json()
                print(f"✅ Schedule fetched successfully!")
                print(f"Schedules found: {len(schedule_data['schedules'])}")
                if schedule_data['schedules']:
                    first_schedule = schedule_data['schedules'][0]
                    print(f"First class: {first_schedule['matiere']['nom']} on {first_schedule['date']}")
            else:
                print(f"❌ Schedule fetch failed!")
                print(f"Error: {schedule_response.text}")
                
        else:
            print(f"❌ Login failed!")
            print(f"Error: {login_response.text}")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    asyncio.run(test_teacher_auth())
