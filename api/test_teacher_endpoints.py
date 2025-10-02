#!/usr/bin/env python3
"""
Test script for teacher profile endpoints
"""

import asyncio
import httpx

async def test_teacher_endpoints():
    """Test teacher profile endpoints"""
    
    base_url = "http://localhost:8000"
    
    # First, login as the teacher to get a token
    login_data = {
        "email": "jean.martin@university.com",
        "password": "password123"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            print("🔐 Logging in as teacher...")
            login_response = await client.post(f"{base_url}/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code}")
                print(login_response.text)
                return
            
            login_result = login_response.json()
            token = login_result["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            print(f"✅ Login successful, token: {token[:20]}...")
            
            # Test teacher profile endpoint
            print("\n📋 Testing teacher profile endpoint...")
            profile_response = await client.get(f"{base_url}/teacher/profile", headers=headers)
            
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print("✅ Teacher profile retrieved successfully!")
                print(f"   Teacher: {profile_data.get('teacher_info', {}).get('nom')} {profile_data.get('teacher_info', {}).get('prenom')}")
                print(f"   Department: {profile_data.get('department', {}).get('nom')}")
                if profile_data.get('department_head'):
                    print(f"   Department Head: {profile_data['department_head']['nom']} {profile_data['department_head']['prenom']}")
                print(f"   Subjects taught: {len(profile_data.get('subjects_taught', []))}")
            else:
                print(f"❌ Profile request failed: {profile_response.status_code}")
                print(profile_response.text)
            
            # Test departments endpoint
            print("\n🏢 Testing departments endpoint...")
            departments_response = await client.get(f"{base_url}/teacher/departments", headers=headers)
            
            if departments_response.status_code == 200:
                departments_data = departments_response.json()
                print(f"✅ Found {len(departments_data)} departments")
                for dept in departments_data:
                    print(f"   - {dept['nom']} ({len(dept['specialties'])} specialties)")
                    if dept.get('department_head'):
                        print(f"     Head: {dept['department_head']['nom']} {dept['department_head']['prenom']}")
            else:
                print(f"❌ Departments request failed: {departments_response.status_code}")
                print(departments_response.text)
            
            # Test subjects endpoint
            print("\n📚 Testing subjects endpoint...")
            subjects_response = await client.get(f"{base_url}/teacher/subjects", headers=headers)
            
            if subjects_response.status_code == 200:
                subjects_data = subjects_response.json()
                print(f"✅ Found {len(subjects_data)} subjects taught by teacher")
                for subject in subjects_data:
                    print(f"   - {subject['nom']} (Level: {subject['level']['nom']})")
            else:
                print(f"❌ Subjects request failed: {subjects_response.status_code}")
                print(subjects_response.text)
                
            print("\n🎉 All teacher endpoint tests completed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_teacher_endpoints())