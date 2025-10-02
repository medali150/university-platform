#!/usr/bin/env python3
"""
Quick test of teacher profile HTTP endpoint
"""

import asyncio
import httpx

async def quick_teacher_test():
    """Quick test of teacher endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Login credentials for teacher
    login_data = {
        "email": "jean.martin@university.com",
        "password": "password123"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("🔐 Logging in as teacher...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(login_response.text)
                return
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful!")
            
            # Test teacher profile endpoint
            print("\n📋 Testing /teacher/profile endpoint...")
            try:
                profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("✅ Teacher profile endpoint works!")
                    print(f"   Teacher: {profile_data['teacher_info']['nom']} {profile_data['teacher_info']['prenom']}")
                    print(f"   Department: {profile_data['department']['nom']}")
                    print(f"   Department Head: {profile_data.get('department_head', 'None')}")
                    print(f"   Subjects: {len(profile_data['subjects_taught'])}")
                else:
                    print(f"❌ Profile failed: {profile_response.status_code}")
                    print(profile_response.text)
            except Exception as e:
                print(f"❌ Profile request error: {e}")
            
            # Test departments endpoint
            print("\n🏢 Testing /teacher/departments endpoint...")
            try:
                dept_response = await client.get(f"{base_url}/teacher/departments", headers=headers)
                
                if dept_response.status_code == 200:
                    dept_data = dept_response.json()
                    print(f"✅ Departments endpoint works! Found {len(dept_data)} departments")
                else:
                    print(f"❌ Departments failed: {dept_response.status_code}")
                    print(dept_response.text)
            except Exception as e:
                print(f"❌ Departments request error: {e}")
            
            # Test subjects endpoint
            print("\n📚 Testing /teacher/subjects endpoint...")
            try:
                subjects_response = await client.get(f"{base_url}/teacher/subjects", headers=headers)
                
                if subjects_response.status_code == 200:
                    subjects_data = subjects_response.json()
                    print(f"✅ Subjects endpoint works! Found {len(subjects_data)} subjects")
                else:
                    print(f"❌ Subjects failed: {subjects_response.status_code}")
                    print(subjects_response.text)
            except Exception as e:
                print(f"❌ Subjects request error: {e}")
                
    except Exception as e:
        print(f"❌ General error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_teacher_test())