#!/usr/bin/env python3
"""
Test script to verify helper endpoints for subject creation
"""

import requests
import json

def test_helper_endpoints():
    """Test helper endpoints for subject creation"""
    
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
        
        # Test levels endpoint
        print("\n📚 Testing levels endpoint...")
        levels_response = requests.get(
            "http://localhost:8000/department-head/subjects/helpers/levels",
            headers=headers
        )
        
        print(f"Levels Status: {levels_response.status_code}")
        if levels_response.status_code == 200:
            levels_data = levels_response.json()
            print(f"✅ Retrieved {len(levels_data.get('levels', []))} levels")
            
            if levels_data.get('levels'):
                sample_level = levels_data['levels'][0]
                print(f"Sample level: {json.dumps(sample_level, indent=2)}")
        else:
            print(f"❌ Levels failed: {levels_response.text}")
        
        # Test teachers endpoint
        print("\n👨‍🏫 Testing teachers endpoint...")
        teachers_response = requests.get(
            "http://localhost:8000/department-head/subjects/helpers/teachers",
            headers=headers
        )
        
        print(f"Teachers Status: {teachers_response.status_code}")
        if teachers_response.status_code == 200:
            teachers_data = teachers_response.json()
            print(f"✅ Retrieved {len(teachers_data.get('teachers', []))} teachers")
            
            if teachers_data.get('teachers'):
                sample_teacher = teachers_data['teachers'][0]
                print(f"Sample teacher: {json.dumps(sample_teacher, indent=2)}")
        else:
            print(f"❌ Teachers failed: {teachers_response.text}")
            
        # Test create subject with sample data
        if levels_response.status_code == 200 and teachers_response.status_code == 200:
            levels_data = levels_response.json()
            teachers_data = teachers_response.json()
            
            if levels_data.get('levels') and teachers_data.get('teachers'):
                print("\n🧪 Testing subject creation...")
                
                sample_subject = {
                    "name": "Test Matière - " + str(hash("test") % 1000),
                    "levelId": levels_data['levels'][0]['id'],
                    "teacherId": teachers_data['teachers'][0]['id']
                }
                
                create_response = requests.post(
                    "http://localhost:8000/department-head/subjects/",
                    headers=headers,
                    json=sample_subject
                )
                
                print(f"Create Status: {create_response.status_code}")
                if create_response.status_code == 200:
                    created_subject = create_response.json()
                    print(f"✅ Subject created successfully!")
                    print(f"Created subject: {json.dumps(created_subject, indent=2)}")
                else:
                    print(f"❌ Create failed: {create_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_helper_endpoints()