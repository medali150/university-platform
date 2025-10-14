#!/usr/bin/env python3
"""
Test specialty creation to debug the 500 error
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login_admin():
    """Login and get token"""
    login_data = {
        "email": "admin@university.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Admin login successful")
            return token_data['access_token']
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error during admin login: {str(e)}")
        return None

def test_specialty_creation():
    """Test specialty creation with detailed error info"""
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get departments first
    print("=== Getting Departments ===")
    response = requests.get(f"{BASE_URL}/departments", headers=headers)
    if response.status_code == 200:
        departments = response.json()
        print(f"Found {len(departments)} departments")
        for dept in departments:
            print(f"  - {dept['name']} (ID: {dept['id']})")
        
        if departments:
            dept = departments[0]  # Use first department
            spec_data = {
                "name": "Test Specialty",
                "departmentId": dept['id']
            }
            
            print(f"\n=== Testing Specialty Creation ===")
            print(f"Creating specialty with data: {json.dumps(spec_data, indent=2)}")
            
            response = requests.post(f"{BASE_URL}/specialties", json=spec_data, headers=headers)
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Success! Created specialty: {result['name']}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw response: {response.text}")
        else:
            print("❌ No departments found")
    else:
        print(f"❌ Failed to get departments: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_specialty_creation()