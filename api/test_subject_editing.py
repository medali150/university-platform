#!/usr/bin/env python3
"""
Test script to verify subject editing functionality
"""

import requests
import json

def test_subject_editing():
    """Test subject editing with field transformations"""
    
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
        
        # Get existing subjects
        print("\n📚 Getting existing subjects...")
        subjects_response = requests.get(
            "http://localhost:8000/department-head/subjects/?page=1&pageSize=10",
            headers=headers
        )
        
        if subjects_response.status_code != 200:
            print(f"❌ Failed to get subjects: {subjects_response.status_code}")
            return
        
        subjects_data = subjects_response.json()
        subjects = subjects_data.get('data', [])
        
        if not subjects:
            print("❌ No subjects found to edit")
            return
        
        # Pick the first subject to edit
        subject_to_edit = subjects[0]
        print(f"📝 Editing subject: {subject_to_edit.get('name')} (ID: {subject_to_edit.get('id')})")
        
        # Test edit with new name
        updated_name = f"EDITED - {subject_to_edit.get('name')} - Test"
        edit_data = {
            "name": updated_name,
            "levelId": subject_to_edit.get('levelId'),
            "teacherId": subject_to_edit.get('teacherId')
        }
        
        print(f"🧪 Testing edit with data: {json.dumps(edit_data, indent=2)}")
        
        edit_response = requests.put(
            f"http://localhost:8000/department-head/subjects/{subject_to_edit['id']}",
            headers=headers,
            json=edit_data
        )
        
        print(f"Edit Status: {edit_response.status_code}")
        
        if edit_response.status_code == 200:
            edited_subject = edit_response.json()
            print("✅ Subject edited successfully!")
            print(f"Updated name: {edited_subject.get('name')}")
            print(f"Level ID: {edited_subject.get('levelId')}")
            print(f"Teacher ID: {edited_subject.get('teacherId')}")
            
            # Verify the edit by fetching the subject again
            print("\n🔍 Verifying edit by fetching updated subject...")
            verify_response = requests.get(
                f"http://localhost:8000/department-head/subjects/{subject_to_edit['id']}",
                headers=headers
            )
            
            if verify_response.status_code == 200:
                verified_subject = verify_response.json()
                if verified_subject.get('name') == updated_name:
                    print("✅ Edit verification successful!")
                else:
                    print(f"❌ Edit verification failed: expected '{updated_name}', got '{verified_subject.get('name')}'")
            else:
                print(f"⚠️  Could not verify edit: {verify_response.status_code}")
                
        else:
            print(f"❌ Edit failed: {edit_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_subject_editing()