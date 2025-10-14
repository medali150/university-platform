#!/usr/bin/env python3
"""
Simple test script to check if our auth registration fix works
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_available_departments():
    """Test the new available departments endpoint"""
    print("=== Testing Available Departments Endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/auth/available-departments")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Available departments:")
            print(f"   Total departments: {data['total_departments']}")
            print(f"   Occupied departments: {data['occupied_departments']}")
            print(f"   Available for assignment: {data['available_count']}")
            
            if data['available_departments']:
                print("\n   Available departments:")
                for dept in data['available_departments']:
                    print(f"   - {dept['nom']} (ID: {dept['id']})")
            else:
                print("   ⚠️  No departments available for assignment")
                
            return data
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_registration_with_duplicate_dept(dept_id):
    """Test registration with a department that might already have a head"""
    print(f"\n=== Testing Registration with Department ID: {dept_id} ===")
    
    test_user = {
        "prenom": "Test",
        "nom": "Head",
        "email": f"testhead_{dept_id[:8]}@example.com",
        "password": "testpass123",
        "role": "DEPARTMENT_HEAD"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register?department_id={dept_id}",
            json=test_user
        )
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            data = response.json()
            print(f"   Created user: {data['prenom']} {data['nom']}")
        elif response.status_code == 400:
            error_data = response.json()
            if "already has a department head" in error_data.get('detail', ''):
                print("✅ Good! Properly caught duplicate department head error:")
                print(f"   {error_data['detail']}")
            else:
                print(f"❌ Unexpected 400 error: {error_data['detail']}")
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Auth Registration Fixes")
    print("=" * 50)
    
    # Test the available departments endpoint
    dept_data = test_available_departments()
    
    if dept_data and dept_data['available_departments']:
        # Test registration with an available department
        available_dept = dept_data['available_departments'][0]
        print(f"\n=== Testing Registration with Available Department ===")
        print(f"Using department: {available_dept['nom']} (ID: {available_dept['id']})")
        
        test_user = {
            "prenom": "New",
            "nom": "DeptHead",
            "email": f"newhead_{available_dept['id'][:8]}@example.com",
            "password": "testpass123",
            "role": "DEPARTMENT_HEAD"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register?department_id={available_dept['id']}",
                json=test_user
            )
            
            if response.status_code == 201:
                print("✅ Registration successful with available department!")
            else:
                print(f"❌ Registration failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Test with the problematic department ID from the original error
    print(f"\n=== Testing with Original Problem Department ID ===")
    test_registration_with_duplicate_dept("cmgf7np350000bmb0jj5odswj")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")