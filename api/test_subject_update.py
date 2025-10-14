#!/usr/bin/env python3
"""
Test script to verify subject update functionality
"""

import requests
import json

def test_subject_update():
    """Test subject update with null teacher handling"""
    
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
        
        # Get subjects
        print("\n📚 Getting subjects...")
        subjects_response = requests.get(
            "http://localhost:8000/department-head/subjects/?page=1&pageSize=10",
            headers=headers
        )
        
        if subjects_response.status_code != 200:
            print(f"❌ Get subjects failed: {subjects_response.status_code}")
            return
        
        subjects_data = subjects_response.json()
        subjects = subjects_data.get('data', [])
        
        if not subjects:
            print("❌ No subjects found for testing")
            return
        
        # Test updating the first subject
        test_subject = subjects[0]
        print(f"📝 Testing update for subject: {test_subject.get('name')}")
        print(f"Current teacher: {test_subject.get('teacher')}")
        
        # Update subject data
        update_data = {
            "name": f"Updated Subject - {hash('test') % 1000}",
            "levelId": test_subject.get('levelId'),
            "teacherId": test_subject.get('teacherId')  # Keep existing teacher (might be None)
        }
        
        print(f"🔄 Updating subject with data: {json.dumps(update_data, indent=2)}")
        
        update_response = requests.put(
            f"http://localhost:8000/department-head/subjects/{test_subject['id']}",
            headers=headers,
            json=update_data
        )
        
        print(f"Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            updated_subject = update_response.json()
            print("✅ Subject updated successfully!")
            print(f"Updated name: {updated_subject.get('name')}")
            print(f"Teacher: {updated_subject.get('teacher')}")
            print(f"Level: {updated_subject.get('level', {}).get('name')}")
        else:
            print(f"❌ Update failed: {update_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_subject_update()