#!/usr/bin/env python3
"""
Test script to verify subject creation with optional teacher
"""

import requests
import json

def test_subject_creation():
    """Test subject creation with and without teacher"""
    
    try:
        # Login as department head
        print("🔐 Logging in as department head...")
        login_response = requests.post(
            "http://localhost:8000/auth/login",
            json={
                "email": "test.depthead@university.com",
                "password": "test123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful!")
        
        # Get helper data
        print("\n📚 Getting helper data...")
        levels_response = requests.get(
            "http://localhost:8000/department-head/subjects/helpers/levels",
            headers=headers
        )
        
        teachers_response = requests.get(
            "http://localhost:8000/department-head/subjects/helpers/teachers",
            headers=headers
        )
        
        if levels_response.status_code != 200 or teachers_response.status_code != 200:
            print(f"❌ Helper data failed: levels={levels_response.status_code}, teachers={teachers_response.status_code}")
            return
        
        levels_data = levels_response.json()
        teachers_data = teachers_response.json()
        
        print(f"✅ Got {len(levels_data.get('levels', []))} levels, {len(teachers_data.get('teachers', []))} teachers")
        
        if not levels_data.get('levels'):
            print("❌ No levels available for testing")
            return
        
        # Test 1: Create subject without teacher
        print("\n🧪 Test 1: Creating subject without teacher...")
        subject_without_teacher = {
            "name": f"Test Subject No Teacher - {hash('test1') % 1000}",
            "levelId": levels_data['levels'][0]['id']
            # No teacherId provided
        }
        
        create_response = requests.post(
            "http://localhost:8000/department-head/subjects/",
            headers=headers,
            json=subject_without_teacher
        )
        
        print(f"Status: {create_response.status_code}")
        if create_response.status_code == 200:
            created_subject = create_response.json()
            print("✅ Subject created without teacher!")
            print(f"Created: {created_subject.get('name')}")
            print(f"Teacher: {created_subject.get('teacher')}")
        else:
            print(f"❌ Failed: {create_response.text}")
        
        # Test 2: Create subject with teacher (if teachers available)
        if teachers_data.get('teachers'):
            print("\n🧪 Test 2: Creating subject with teacher...")
            subject_with_teacher = {
                "name": f"Test Subject With Teacher - {hash('test2') % 1000}",
                "levelId": levels_data['levels'][0]['id'],
                "teacherId": teachers_data['teachers'][0]['id']
            }
            
            create_response2 = requests.post(
                "http://localhost:8000/department-head/subjects/",
                headers=headers,
                json=subject_with_teacher
            )
            
            print(f"Status: {create_response2.status_code}")
            if create_response2.status_code == 200:
                created_subject2 = create_response2.json()
                print("✅ Subject created with teacher!")
                print(f"Created: {created_subject2.get('name')}")
                print(f"Teacher: {created_subject2.get('teacher')}")
            else:
                print(f"❌ Failed: {create_response2.text}")
        else:
            print("\n⚠️  No teachers available for Test 2")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_subject_creation()