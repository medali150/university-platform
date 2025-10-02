#!/usr/bin/env python3
"""
Test the complete department head registration flow (simulating frontend behavior)
"""

import requests
import json

def test_complete_registration_flow():
    """Test the complete registration flow exactly as the frontend would do it"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Complete Department Head Registration Flow...")
    
    # Step 1: Get available departments (like frontend does)
    print("\n1️⃣ Getting departments (like frontend)...")
    try:
        dept_response = requests.get(f"{base_url}/departments")
        if dept_response.status_code != 200:
            print(f"❌ Departments endpoint failed: {dept_response.status_code}")
            print(f"Error: {dept_response.text}")
            return
        
        departments = dept_response.json()
        if not departments:
            print("❌ No departments found")
            return
            
        department_id = departments[0]["id"]
        department_name = departments[0]["name"]
        print(f"✅ Using department: {department_name} (ID: {department_id})")
        
    except Exception as e:
        print(f"❌ Error getting departments: {e}")
        return
    
    # Step 2: Prepare registration data (exactly like frontend)
    registration_data = {
        "nom": "FrontendTest",
        "prenom": "Marie",
        "email": "marie.frontend@university.com",
        "password": "frontend123",
        "role": "DEPARTMENT_HEAD"
        # Note: departmentId is NOT in the body, it's in the query parameter
    }
    
    print(f"\n2️⃣ Registration data (body):")
    print(json.dumps(registration_data, indent=2))
    
    # Step 3: Make registration request with department_id as query parameter
    url = f"{base_url}/auth/register?department_id={department_id}"
    print(f"\n3️⃣ Making registration request:")
    print(f"URL: {url}")
    
    try:
        response = requests.post(
            url,
            json=registration_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            result = response.json()
            print(f"User: {result.get('prenom')} {result.get('nom')}")
            print(f"Role: {result.get('role')}")
            print(f"Email: {result.get('email')}")
        else:
            print("❌ Registration failed!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")

if __name__ == "__main__":
    test_complete_registration_flow()