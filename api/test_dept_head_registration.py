#!/usr/bin/env python3
"""
Test department head registration with debugging
"""

import requests
import json

def test_department_head_registration():
    """Test the department head registration with department selection"""
    base_url = "http://127.0.0.1:8000"
    
    # Test data
    registration_data = {
        "nom": "TestChef",
        "prenom": "Jean",
        "email": "testchef@university.com",
        "password": "test123456",
        "role": "DEPARTMENT_HEAD"
    }
    
    print("🧪 Testing Department Head Registration with Department Selection...")
    
    try:
        # First, get available departments
        print("\n1️⃣ Getting available departments...")
        dept_response = requests.get(f"{base_url}/departments")
        print(f"Departments response status: {dept_response.status_code}")
        
        if dept_response.status_code == 200:
            departments = dept_response.json()
            print(f"Found {len(departments)} departments")
            
            if departments:
                department_id = departments[0]["id"]
                department_name = departments[0]["name"]
                print(f"Using department: {department_name} (ID: {department_id})")
                
                # Test registration with department_id
                print(f"\n2️⃣ Testing registration with department_id...")
                url = f"{base_url}/auth/register?department_id={department_id}"
                print(f"POST URL: {url}")
                print(f"Data: {json.dumps(registration_data, indent=2)}")
                
                response = requests.post(
                    url,
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Response status: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Registration successful!")
                    result = response.json()
                    print(f"User created: {result.get('prenom')} {result.get('nom')} - {result.get('role')}")
                else:
                    print("❌ Registration failed!")
                    print(f"Response: {response.text}")
            else:
                print("❌ No departments found in response")
        else:
            print(f"❌ Failed to get departments: {dept_response.status_code}")
            print(f"Response: {dept_response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_department_head_registration()