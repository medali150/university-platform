#!/usr/bin/env python3
"""
Test teacher profile endpoint
"""

import asyncio
import requests
import json

async def test_teacher_profile():
    """Test teacher profile functionality"""
    
    base_url = "http://localhost:8000"
    
    # First, login as teacher to get token
    login_data = {
        "email": "jean.martin@university.com",
        "password": "password123"
    }
    
    print("🔐 Logging in as teacher...")
    login_response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data["access_token"]
    print(f"✅ Login successful")
    
    # Test teacher profile endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n👤 Getting teacher profile...")
    profile_response = requests.get(f"{base_url}/teacher/profile", headers=headers)
    
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print("✅ Teacher profile retrieved successfully!")
        print(json.dumps(profile_data, indent=2, default=str))
    else:
        print(f"❌ Profile request failed: {profile_response.status_code}")
        print(profile_response.text)
    
    # Test departments endpoint
    print("\n🏢 Getting available departments...")
    dept_response = requests.get(f"{base_url}/teacher/departments", headers=headers)
    
    if dept_response.status_code == 200:
        dept_data = dept_response.json()
        print("✅ Departments retrieved successfully!")
        print(json.dumps(dept_data, indent=2, default=str))
    else:
        print(f"❌ Departments request failed: {dept_response.status_code}")
        print(dept_response.text)
    
    # Test subjects endpoint
    print("\n📚 Getting teacher subjects...")
    subjects_response = requests.get(f"{base_url}/teacher/subjects", headers=headers)
    
    if subjects_response.status_code == 200:
        subjects_data = subjects_response.json()
        print("✅ Subjects retrieved successfully!")
        print(json.dumps(subjects_data, indent=2, default=str))
    else:
        print(f"❌ Subjects request failed: {subjects_response.status_code}")
        print(subjects_response.text)

if __name__ == "__main__":
    asyncio.run(test_teacher_profile())