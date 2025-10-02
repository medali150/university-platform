"""
Test script for Subject CRUD operations
This script tests the newly created Subject CRUD endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_subject_crud():
    print("🧪 Testing Subject CRUD Operations")
    print("=" * 50)
    
    # Test login to get admin token
    print("1. Testing admin login...")
    login_data = {
        "login": "mohamedali.gh15@gmail.com",
        "password": "daligh15"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.text}")
        return
    
    # Test get levels (helper endpoint)
    print("\n2. Testing get levels helper...")
    response = requests.get(f"{BASE_URL}/admin/subjects/helpers/levels", headers=headers)
    if response.status_code == 200:
        levels_data = response.json()
        print(f"✅ Got {len(levels_data.get('levels', []))} levels")
        levels = levels_data.get('levels', [])
    else:
        print(f"❌ Get levels failed: {response.text}")
        levels = []
    
    # Test get teachers (helper endpoint)
    print("\n3. Testing get teachers helper...")
    response = requests.get(f"{BASE_URL}/admin/subjects/helpers/teachers", headers=headers)
    if response.status_code == 200:
        teachers_data = response.json()
        print(f"✅ Got {len(teachers_data.get('teachers', []))} teachers")
        teachers = teachers_data.get('teachers', [])
    else:
        print(f"❌ Get teachers failed: {response.text}")
        teachers = []
    
    # Test get subjects (empty list initially)
    print("\n4. Testing get subjects...")
    response = requests.get(f"{BASE_URL}/admin/subjects/", headers=headers)
    if response.status_code == 200:
        subjects_data = response.json()
        print(f"✅ Got {subjects_data.get('total', 0)} subjects")
    else:
        print(f"❌ Get subjects failed: {response.text}")
    
    # Create a subject if we have levels and teachers
    if levels and teachers:
        print("\n5. Testing create subject...")
        create_data = {
            "name": "Test Mathematics",
            "levelId": levels[0]["id"],
            "teacherId": teachers[0]["id"]
        }
        
        response = requests.post(f"{BASE_URL}/admin/subjects/", json=create_data, headers=headers)
        if response.status_code == 201:
            subject = response.json()
            subject_id = subject["id"]
            print(f"✅ Subject created: {subject['name']}")
            
            # Test get specific subject
            print("\n6. Testing get specific subject...")
            response = requests.get(f"{BASE_URL}/admin/subjects/{subject_id}", headers=headers)
            if response.status_code == 200:
                subject_detail = response.json()
                print(f"✅ Got subject details: {subject_detail['name']}")
            else:
                print(f"❌ Get subject details failed: {response.text}")
            
            # Test update subject
            print("\n7. Testing update subject...")
            update_data = {
                "name": "Advanced Mathematics"
            }
            response = requests.put(f"{BASE_URL}/admin/subjects/{subject_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                updated_subject = response.json()
                print(f"✅ Subject updated: {updated_subject['name']}")
            else:
                print(f"❌ Update subject failed: {response.text}")
            
            # Test delete subject
            print("\n8. Testing delete subject...")
            response = requests.delete(f"{BASE_URL}/admin/subjects/{subject_id}", headers=headers)
            if response.status_code == 204:
                print("✅ Subject deleted successfully")
            else:
                print(f"❌ Delete subject failed: {response.text}")
        else:
            print(f"❌ Create subject failed: {response.text}")
    else:
        print("⚠️  Skipping create/update/delete tests - no levels or teachers available")
    
    print("\n" + "=" * 50)
    print("🎯 Subject CRUD testing completed!")


def test_level_crud():
    print("\n🧪 Testing Level CRUD Operations")
    print("=" * 50)
    
    # Test login to get admin token
    print("1. Testing admin login...")
    login_data = {
        "login": "admin_user",
        "password": "admin_password"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.text}")
        return
    
    # Test get levels
    print("\n2. Testing get levels...")
    response = requests.get(f"{BASE_URL}/admin/levels/", headers=headers)
    if response.status_code == 200:
        levels_data = response.json()
        print(f"✅ Got {levels_data.get('total', 0)} levels")
    else:
        print(f"❌ Get levels failed: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎯 Level CRUD testing completed!")


if __name__ == "__main__":
    print("🚀 Starting API CRUD Tests")
    print("Make sure the FastAPI server is running on http://127.0.0.1:8000")
    print()
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            test_subject_crud()
            test_level_crud()
        else:
            print("❌ Server is not healthy")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the FastAPI server first:")
        print("cd api && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")