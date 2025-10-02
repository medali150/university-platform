#!/usr/bin/env python3
"""
Debug script to test the registration endpoint
"""

import asyncio
import requests
import json

async def test_registration():
    """Test the registration endpoint"""
    base_url = "http://127.0.0.1:8000"
    
    # Test data for department head registration
    registration_data = {
        "nom": "Dupont",
        "prenom": "Jean",
        "email": "jean.dupont@university.com",
        "password": "test123456",
        "role": "DEPARTMENT_HEAD"
    }
    
    print("🧪 Testing Department Head Registration...")
    print(f"Registration data: {json.dumps(registration_data, indent=2)}")
    
    try:
        # First get available departments to use one for testing
        print("\n1️⃣ Getting available departments...")
        dept_response = requests.get(f"{base_url}/departments")
        if dept_response.status_code == 200:
            departments = dept_response.json()
            if departments:
                department_id = departments[0]["id"]
                print(f"✅ Found department: {departments[0]['name']} (ID: {department_id})")
                
                # Test registration with department_id parameter
                print(f"\n2️⃣ Testing registration with department_id: {department_id}")
                response = requests.post(
                    f"{base_url}/auth/register?department_id={department_id}",
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Registration successful!")
                    print(f"Response: {json.dumps(response.json(), indent=2)}")
                else:
                    print("❌ Registration failed!")
                    print(f"Error: {response.text}")
            else:
                print("❌ No departments found!")
        else:
            print(f"❌ Failed to get departments: {dept_response.status_code}")
            print(f"Error: {dept_response.text}")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_registration())